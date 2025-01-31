import requests

# 配置 Digi-Key API
ACCESS_TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
CLIENT_ID = "BDV2P3CADoAL6ZkoiN5K0Ram2UneIdKD"
CLIENT_SECRET = "GW5r9ExvMb4r3AV2"
REDIRECT_URI = "https://localhost:8139/digikey_callback"
AUTH_CODE = "GMQG3abV"  # 替换为您的授权码

# 交换 Access Token
def exchange_auth_code_for_token(auth_code):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(ACCESS_TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error exchanging auth code: {response.status_code}, {response.text}")
        return None

# 获取 Access Token
token_response = exchange_auth_code_for_token(AUTH_CODE)

if token_response:
    print("Access Token:", token_response["access_token"])
    print("Refresh Token:", token_response["refresh_token"])