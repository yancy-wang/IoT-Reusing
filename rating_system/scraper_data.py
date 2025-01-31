import json
import re
from scrapegraphai.graphs import SmartScraperGraph

# 定义抓取配置
graph_config = {
    "llm": {
        "api_key": "ollama",
        "model": "ollama/llama3:8b",
        "temperature": 0,
        "rate_limit": {
            "requests_per_second": 1
        }
    },
    "verbose": True,
    "headless": False,
}

# **确保 ScrapeGraphAI 生成 JSON**
prompt_text = """
List all protocol technologies (e.g., BLE, WiFi, LoRa, GNSS) supported by this product.
Return ONLY a valid JSON output without explanations, markdown, or extra text.

Strictly format the output as:
{
    "protocols": ["BLE", "WiFi", "LoRa", "GNSS"]
}
"""

# 初始化 ScrapeGraphAI
smart_scraper_graph = SmartScraperGraph(
    prompt=prompt_text,
    source="https://wiki.seeedstudio.com/Wio-Tracker_Introduction/",
    config=graph_config
)

# 运行抓取任务
raw_result = smart_scraper_graph.run()

# **尝试解析 JSON**
try:
    result = json.loads(raw_result)  # 直接解析 JSON
except json.JSONDecodeError:
    print("Error: Output is not valid JSON. Trying to extract JSON from text...")
    
    # **方法 2：如果 JSON 解析失败，手动提取**
    def extract_json_from_text(text):
        match = re.search(r'\{.*\}', text, re.DOTALL)  # 提取 JSON 内容
        if match:
            try:
                return json.loads(match.group(0))  # 解析 JSON
            except json.JSONDecodeError:
                return None
        return None

    result = extract_json_from_text(raw_result)

# 打印最终 JSON 结果
print(result)
