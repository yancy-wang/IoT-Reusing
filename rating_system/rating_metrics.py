import mysql.connector
from mysql.connector import Error
import json

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='16.170.225.25',
            port=3306,
            user='root',
            password='1234',
            database='iot_system'
        )

        if connection.is_connected():
            print("Connected to the database")
            return connection
    except Error as e:
        print(f"Error while connecting to database: {e}")
        return None

def calculate_experiment_score(sensor_scenario_count, protocol_scenario_count, total_interfaces_count, total_power_supply_count,
                                cpu_usage, memory_usage, inference_time, model_accuracy,
                                latency, error_rate, stability, cost,
                                max_values):
    # Define weights (adjusted to sum to 1)
    weights = {
        'sensor_scenario_count': 0.1,
        'protocol_scenario_count': 0.1,
        'total_interfaces_count': 0.1,
        'total_power_supply_count': 0.1,
        'cpu_usage': -0.1,
        'memory_usage': -0.1,
        'inference_time': -0.1,
        'model_accuracy': 0.15,
        'latency': -0.05,
        'error_rate': -0.05,
        'stability': 0.1,
        'cost': -0.05
    }

    # Normalize metrics to [0, 1] based on max values
    normalized_values = {
        'sensor_scenario_count': sensor_scenario_count / max_values['sensor_scenario_count'] if max_values['sensor_scenario_count'] else 0,
        'protocol_scenario_count': protocol_scenario_count / max_values['protocol_scenario_count'] if max_values['protocol_scenario_count'] else 0,
        'total_interfaces_count': total_interfaces_count / max_values['total_interfaces_count'] if max_values['total_interfaces_count'] else 0,
        'total_power_supply_count': total_power_supply_count / max_values['total_power_supply_count'] if max_values['total_power_supply_count'] else 0,
        'cpu_usage': (max_values['cpu_usage'] - cpu_usage) / max_values['cpu_usage'] if max_values['cpu_usage'] else 0,
        'memory_usage': (max_values['memory_usage'] - memory_usage) / max_values['memory_usage'] if max_values['memory_usage'] else 0,
        'inference_time': (max_values['inference_time'] - inference_time) / max_values['inference_time'] if max_values['inference_time'] else 0,
        'model_accuracy': model_accuracy / max_values['model_accuracy'] if max_values['model_accuracy'] else 0,
        'latency': (max_values['latency'] - latency) / max_values['latency'] if max_values['latency'] else 0,
        'error_rate': (max_values['error_rate'] - error_rate) / max_values['error_rate'] if max_values['error_rate'] else 0,
        'stability': stability / max_values['stability'] if max_values['stability'] else 0,
        'cost': (float(max_values['cost'] - float(cost)) )/ float(max_values['cost']) if max_values['cost'] else 0
    }

    # Scale normalized values to [0, 10] and calculate score
    score = 0
    for metric, weight in weights.items():
        score += weight * normalized_values[metric] * 10

    return round(score, 2)

def process_experiments():
    connection = connect_to_database()
    if not connection:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch all data from the experiments table
        cursor.execute("SELECT * FROM experiments")
        experiments = cursor.fetchall()

        # Calculate max values for normalization
        max_values = {
            'sensor_scenario_count': 0,
            'protocol_scenario_count': 0,
            'total_interfaces_count': 0,
            'total_power_supply_count': 0,
            'cpu_usage': 0,
            'memory_usage': 0,
            'inference_time': 0,
            'model_accuracy': 0,
            'latency': 0,
            'error_rate': 0,
            'stability': 0,
            'cost': 0
        }

        # Collect max values from experiments
        for experiment in experiments:
            protocol_experiment_id = experiment['protocol_experiments_id']
            computing_experiment_id = experiment['computing_experiments_id']
            used_devices_id = json.loads(experiment['used_devices_id'])

            sensor_ids = set()
            usage_ids_from_sensors = set()
            usage_ids_from_protocol = set()
            interface_types = set()
            power_supply_modes = set()
            cost = 0

            for device_id in used_devices_id:
                cursor.execute("SELECT sensor_id FROM sensor_device_mapping WHERE m_id = %s", (device_id,))
                sensors = cursor.fetchall()
                for sensor in sensors:
                    sensor_ids.add(sensor['sensor_id'])

                cursor.execute("SELECT price FROM devices WHERE m_id = %s", (device_id,))
                device_cost = cursor.fetchone()
                if device_cost:
                    cost += float(device_cost['price'])

                cursor.execute("SELECT interface_id FROM interface_device_mapping WHERE m_id = %s", (device_id,))
                interfaces = cursor.fetchall()
                for interface in interfaces:
                    cursor.execute("SELECT interface_type FROM interface_type WHERE interface_id = %s", (interface['interface_id'],))
                    interface_type = cursor.fetchone()
                    if interface_type:
                        interface_types.add(interface_type['interface_type'])

                cursor.execute("SELECT power_id FROM power_supply_device_mapping WHERE m_id = %s", (device_id,))
                power_supplies = cursor.fetchall()
                for power_supply in power_supplies:
                    cursor.execute("SELECT power_supply_mode FROM power_supply WHERE power_id = %s", (power_supply['power_id'],))
                    power_mode = cursor.fetchone()
                    if power_mode:
                        power_supply_modes.add(power_mode['power_supply_mode'])

            for sensor_id in sensor_ids:
                cursor.execute("SELECT usage_id FROM sensor_usage_mapping WHERE sensor_id = %s", (sensor_id,))
                usages = cursor.fetchall()
                for usage in usages:
                    usage_ids_from_sensors.add(usage['usage_id'])

            cursor.execute("SELECT used_protocol_id FROM protocol_experiments WHERE protocol_experiments_id = %s", (protocol_experiment_id,))
            protocol_experiment = cursor.fetchone()
            if protocol_experiment:
                used_protocol_ids = json.loads(protocol_experiment['used_protocol_id'])
                for protocol_id in used_protocol_ids:
                    cursor.execute("SELECT usage_id FROM protocol_usage_scenario_mapping WHERE protocol_id = %s", (protocol_id,))
                    protocol_usages = cursor.fetchall()
                    for protocol_usage in protocol_usages:
                        usage_ids_from_protocol.add(protocol_usage['usage_id'])

            max_values['cost'] = float(max(max_values['cost'], cost))
            max_values['sensor_scenario_count'] = max(max_values['sensor_scenario_count'], len(usage_ids_from_sensors))
            max_values['protocol_scenario_count'] = max(max_values['protocol_scenario_count'], len(usage_ids_from_protocol))
            max_values['total_interfaces_count'] = max(max_values['total_interfaces_count'], len(interface_types))
            max_values['total_power_supply_count'] = max(max_values['total_power_supply_count'], len(power_supply_modes))

            cursor.execute("SELECT * FROM computing_experiments WHERE computing_experiments_id = %s", (computing_experiment_id,))
            computing_metrics = cursor.fetchone()
            if computing_metrics:
                max_values['cpu_usage'] = max(max_values['cpu_usage'], computing_metrics['cpu_usage'])
                max_values['memory_usage'] = max(max_values['memory_usage'], computing_metrics['memory_usage'])
                max_values['inference_time'] = max(max_values['inference_time'], computing_metrics['inference_time'])
                max_values['model_accuracy'] = max(max_values['model_accuracy'], computing_metrics['model_accuracy'])

            cursor.execute("SELECT latency, error_rate, stability FROM protocol_experiments WHERE protocol_experiments_id = %s", (protocol_experiment_id,))
            protocol_metrics = cursor.fetchone()
            if protocol_metrics:
                max_values['latency'] = max(max_values['latency'], protocol_metrics['latency'])
                max_values['error_rate'] = max(max_values['error_rate'], protocol_metrics['error_rate'])
                max_values['stability'] = max(max_values['stability'], protocol_metrics['stability'])

        # Process experiments and calculate scores
        for experiment in experiments:
            experiment_id = experiment['experiments_id']
            protocol_experiment_id = experiment['protocol_experiments_id']
            computing_experiment_id = experiment['computing_experiments_id']
            used_devices_id = json.loads(experiment['used_devices_id'])

            sensor_ids = set()
            usage_ids_from_sensors = set()
            usage_ids_from_protocol = set()
            interface_types = set()
            power_supply_modes = set()
            cost = 0

            for device_id in used_devices_id:
                cursor.execute("SELECT sensor_id FROM sensor_device_mapping WHERE m_id = %s", (device_id,))
                sensors = cursor.fetchall()
                for sensor in sensors:
                    sensor_ids.add(sensor['sensor_id'])

                cursor.execute("SELECT price FROM devices WHERE m_id = %s", (device_id,))
                device_cost = cursor.fetchone()
                if device_cost:
                    cost += device_cost['price']

                cursor.execute("SELECT interface_id FROM interface_device_mapping WHERE m_id = %s", (device_id,))
                interfaces = cursor.fetchall()
                for interface in interfaces:
                    cursor.execute("SELECT interface_type FROM interface_type WHERE interface_id = %s", (interface['interface_id'],))
                    interface_type = cursor.fetchone()
                    if interface_type:
                        interface_types.add(interface_type['interface_type'])

                cursor.execute("SELECT power_id FROM power_supply_device_mapping WHERE m_id = %s", (device_id,))
                power_supplies = cursor.fetchall()
                for power_supply in power_supplies:
                    cursor.execute("SELECT power_supply_mode FROM power_supply WHERE power_id = %s", (power_supply['power_id'],))
                    power_mode = cursor.fetchone()
                    if power_mode:
                        power_supply_modes.add(power_mode['power_supply_mode'])

            for sensor_id in sensor_ids:
                cursor.execute("SELECT usage_id FROM sensor_usage_mapping WHERE sensor_id = %s", (sensor_id,))
                usages = cursor.fetchall()
                for usage in usages:
                    usage_ids_from_sensors.add(usage['usage_id'])

            cursor.execute("SELECT used_protocol_id FROM protocol_experiments WHERE protocol_experiments_id = %s", (protocol_experiment_id,))
            protocol_experiment = cursor.fetchone()
            if protocol_experiment:
                used_protocol_ids = json.loads(protocol_experiment['used_protocol_id'])
                for protocol_id in used_protocol_ids:
                    cursor.execute("SELECT usage_id FROM protocol_usage_scenario_mapping WHERE protocol_id = %s", (protocol_id,))
                    protocol_usages = cursor.fetchall()
                    for protocol_usage in protocol_usages:
                        usage_ids_from_protocol.add(protocol_usage['usage_id'])

            # Fetch computing_experiments metrics
            cursor.execute("SELECT * FROM computing_experiments WHERE computing_experiments_id = %s", (computing_experiment_id,))
            computing_metrics = cursor.fetchone() or {}

            # Fetch protocol_experiments metrics
            cursor.execute("SELECT latency, error_rate, stability FROM protocol_experiments WHERE protocol_experiments_id = %s", (protocol_experiment_id,))
            protocol_metrics = cursor.fetchone() or {}

            # Calculate score
            score = calculate_experiment_score(
                sensor_scenario_count=len(usage_ids_from_sensors),
                protocol_scenario_count=len(usage_ids_from_protocol),
                total_interfaces_count=len(interface_types),
                total_power_supply_count=len(power_supply_modes),
                cpu_usage=computing_metrics.get('cpu_usage', 100),
                memory_usage=computing_metrics.get('memory_usage', 100),
                inference_time=computing_metrics.get('inference_time', 100),
                model_accuracy=computing_metrics.get('model_accuracy', 0),
                latency=protocol_metrics.get('latency', 100),
                error_rate=protocol_metrics.get('error_rate', 100),
                stability=protocol_metrics.get('stability', 0),
                cost=cost,
                max_values=max_values
            )

            # Print results
            print(f"Experiment ID: {experiment_id}")
            print(f"Score: {score}")

    except Error as e:
        print(f"Error while processing data: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("Connection closed")

if __name__ == "__main__":
    process_experiments()
