import requests
import json

# Mouser API 配置信息
API_KEY = "0121926a-321e-4dd9-ac41-c159843f6147"  # 替换为你的 Mouser API Key
API_URL = "https://api.mouser.com/api/v2/search/partnumber"  # 基础 URL
API_VERSION = "2"  # API 版本号

# 查询函数
def search_by_part_number(part_number):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "SearchByPartRequest": {
            "mouserPartNumber": part_number,
            "partSearchOptions": ""
        }
    }
    params = {
        "apiKey": API_KEY,
        "version": API_VERSION
    }

    # 发送 POST 请求
    response = requests.post(API_URL, headers=headers, params=params, json=payload)

    # 处理响应
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# 示例调用
if __name__ == "__main__":
    part_number = "101020613"  # 替换为你需要查询的 part number
    result = search_by_part_number(part_number)

    if result:
        print("查询结果:")
        print(json.dumps(result, indent=4))