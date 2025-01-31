import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

# 超参数
LEARNING_RATE_ACTOR = 0.001
LEARNING_RATE_CRITIC = 0.002
DISCOUNT_FACTOR = 0.99

# 初始数据定义
def initialize_state():
    return {
        # Sensor
        "sensor_types": {"critical": 1, "scenario_related": 1, "others": 0},
        "sensor_relevance": 0.8,  # 重要性分数（范围 0-1）
        # Power Supply Modes
        "power_supply_modes": {"renewable": 1, "reliable": 0, "portable": 1},
        "power_priority": 0.9,  # 重要性优先级（范围 0-1）
        # Expandability
        "expandability_score": 0.7,  # 扩展性评分（范围 0-1）
        "max_interface": 5,  # 当前系统最大接口数量
        # Communication
        "protocol_types": {"BLE": 1, "WiFi": 0, "LoRa": 0},
        "protocol_expandability_score": 0.8,  # 协议扩展性评分（范围 0-1）
        "protocol_performance": {
            "latency": 50,  # 延迟（毫秒）
            "error_rate": 0.02,  # 错误率（范围 0-1）
            "stability": 0.9,  # 稳定性（范围 0-1）
            "coverage": 30  # 覆盖范围（米）
        },
        # Computing
        "computing_performance": {
            "inference_time": 10,  # 推理时间（毫秒）
            "memory_usage": 500,  # 内存使用量（MB）
            "cpu_usage": 0.8,  # CPU 使用率（范围 0-1）
            "accuracy": 0.95  # 精度（范围 0-1）
        },
        # System Constraints
        "energy_consumption": 10,  # 能耗（单位：mW）
        "budget": 50  # 预算（单位：欧元）
    }

# 将状态扁平化为一维数组
def flatten_state(state):
    flat_state = []
    # 展开 sensor_types
    flat_state.extend(state["sensor_types"].values())
    # 展开 sensor_relevance
    flat_state.append(state["sensor_relevance"])
    # 展开 power_supply_modes
    flat_state.extend(state["power_supply_modes"].values())
    # 展开 power_priority
    flat_state.append(state["power_priority"])
    # 展开 expandability_score 和 max_interface
    flat_state.append(state["expandability_score"])
    flat_state.append(state["max_interface"])
    # 展开 protocol_types
    flat_state.extend(state["protocol_types"].values())
    # 展开 protocol_expandability_score
    flat_state.append(state["protocol_expandability_score"])
    # 展开 protocol_performance
    flat_state.extend(state["protocol_performance"].values())
    # 展开 computing_performance
    flat_state.extend(state["computing_performance"].values())
    # 展开 energy_consumption 和 budget
    flat_state.append(state["energy_consumption"])
    flat_state.append(state["budget"])
    return np.array(flat_state, dtype=np.float32)

# 奖励公式中所需的权重
def initialize_weights():
    return {
        # Sensor
        "sensor_k": np.pi / 4,  # 传感器相关奖励的敏感度因子
        # Power Supply Modes
        "power_weights": {"renewable": 0.4, "reliable": 0.3, "portable": 0.3},
        "power_k": np.pi / 4,  # 电源优先级敏感度因子
        # Expandability
        "expandability_k": np.pi / 4,  # 扩展性敏感度因子
        # Communication
        "protocol_weights": {"latency": 0.3, "error_rate": 0.2, "stability": 0.3, "coverage": 0.2},
        "protocol_k": np.pi / 4,  # 协议相关奖励的敏感度因子
        # Computing
        "computing_weights": {"inference_time": 0.3, "memory_usage": 0.2, "cpu_usage": 0.2, "accuracy": 0.3},
        "computing_k": np.pi / 4,  # 计算性能敏感度因子
        # System
        "energy_w": -0.1,  # 能耗权重（调整为范围[-1, 0]）
        "cost_w": -0.1  # 成本权重（调整为范围[-1, 0]）
    }

# 奖励函数：根据状态和动作计算基础奖励值
def calculate_reward(state, weights):
    # 计算传感器相关的奖励
    sensor_reward = 0.5 * (1 + np.cos(weights["sensor_k"] * abs(state["sensor_relevance"] - 1)))

    # 计算电源模式的奖励
    power_priority = (
        weights["power_weights"]["renewable"] * state["power_supply_modes"]["renewable"] +
        weights["power_weights"]["reliable"] * state["power_supply_modes"]["reliable"] +
        weights["power_weights"]["portable"] * state["power_supply_modes"]["portable"]
    ) / sum(weights["power_weights"].values())
    power_reward = 0.5 * (1 + np.cos(weights["power_k"] * abs(power_priority - 1)))

    # 计算扩展性相关的奖励
    expandability_reward = 0.5 * (1 + np.cos(weights["expandability_k"] * abs(state["expandability_score"] - 1)))

    # 计算协议相关的奖励
    protocol_reward = 0.5 * (1 + np.cos(weights["protocol_k"] * abs(state["protocol_expandability_score"] - 1)))

    # 计算协议性能的奖励
    protocol_perf_score = (
        weights["protocol_weights"]["latency"] * state["protocol_performance"]["latency"] +
        weights["protocol_weights"]["error_rate"] * state["protocol_performance"]["error_rate"] +
        weights["protocol_weights"]["stability"] * state["protocol_performance"]["stability"] +
        weights["protocol_weights"]["coverage"] * state["protocol_performance"]["coverage"]
    ) / sum(weights["protocol_weights"].values())
    protocol_perf_reward = 0.5 * (1 + np.cos(weights["protocol_k"] * abs(protocol_perf_score - 1)))

    # 计算计算性能的奖励
    computing_perf_score = (
        weights["computing_weights"]["inference_time"] * state["computing_performance"]["inference_time"] +
        weights["computing_weights"]["memory_usage"] * state["computing_performance"]["memory_usage"] +
        weights["computing_weights"]["cpu_usage"] * state["computing_performance"]["cpu_usage"] +
        weights["computing_weights"]["accuracy"] * state["computing_performance"]["accuracy"]
    ) / sum(weights["computing_weights"].values())
    computing_reward = 0.5 * (1 + np.cos(weights["computing_k"] * abs(computing_perf_score - 1)))

    # 计算系统相关的奖励
    energy_reward = max(-1, weights["energy_w"] * state["energy_consumption"])  # 限制范围 [-1, 0]
    cost_reward = max(-1, weights["cost_w"] * state["budget"])  # 限制范围 [-1, 0]

    # 总奖励
    total_reward = (
        sensor_reward +
        power_reward +
        expandability_reward +
        protocol_reward +
        protocol_perf_reward +
        computing_reward +
        energy_reward +
        cost_reward
    )
    return total_reward

# 人类反馈接口
def get_human_feedback(state, action):
    """
    模拟获取用户反馈的接口。实际实现中可以通过GUI或API交互。
    """
    print(f"current state: {state}")
    print(f"action: {action}")
    feedback = input("please enter your comment about the current system（-1:negative, 0:medium, 1:positive): ")
    return float(feedback)

# 奖励函数（结合人类反馈）
def calculate_reward_with_feedback(state, weights, action):
    # 计算基础奖励
    reward = calculate_reward(state, weights)
    print(f"Basic rewarding score: {reward:.2f}")
    # 获取人类反馈
    human_feedback = get_human_feedback(state, action)
    # 修正奖励
    final_reward = reward + 10 * human_feedback
    print(f"The rewarding score after the human adjustment: {final_reward:.2f}")
    return final_reward

# Actor网络定义
def create_actor(input_dim, output_dim):
    inputs = Input(shape=(input_dim,))
    x = Dense(64, activation='relu')(inputs)
    x = Dense(64, activation='relu')(x)
    outputs = Dense(output_dim, activation='softmax')(x)
    model = Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE_ACTOR))
    return model

# Critic网络定义
def create_critic(input_dim):
    inputs = Input(shape=(input_dim,))
    x = Dense(64, activation='relu')(inputs)
    x = Dense(64, activation='relu')(x)
    outputs = Dense(1, activation='linear')(x)
    model = Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE_CRITIC), loss='mse')
    return model

# 训练循环（加入HITL）
def train_with_hitl(actor, critic, episodes=1000):
    weights = initialize_weights()

    for episode in range(episodes):
        state = initialize_state()
        total_reward = 0
        done = False

        while not done:
            # 扁平化状态
            state_vector = flatten_state(state)
            # Actor选择动作
            action_probs = actor.predict(state_vector[np.newaxis, :])[0]
            action_index = np.random.choice(len(action_probs), p=action_probs)
            action = {"type": action_index}  # 示例动作

            # 计算奖励（结合人类反馈）
            reward = calculate_reward_with_feedback(state, weights, action)
            total_reward += reward

            # 更新状态（模拟环境）
            state["energy_consumption"] += 1  # 示例更新
            if total_reward > 500:  # 停止条件
                done = True

        print(f"Episode {episode + 1}, Total Reward: {total_reward}")

# 初始化网络并训练
state_dim = len(flatten_state(initialize_state()))
action_dim = 2  # 动作维度
actor = create_actor(state_dim, action_dim)
critic = create_critic(state_dim)

train_with_hitl(actor, critic)
