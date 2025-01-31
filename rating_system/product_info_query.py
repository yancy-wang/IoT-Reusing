import os
import json
import requests

DIGIKEY_CLIENT_ID=os.getenv("DIGIKEY_CLIENT_ID")
DIGIKEY_CLIENT_SECRET=os.getenv("DIGIKEY_CLIENT_SECRET")

DIGIKEY_AUTH_URL_V4  = 'https://sandbox-api.digikey.com/v1/oauth2/authorize'
DIGIKEY_TOKEN_URL_V4 = 'https://sandbox-api.digikey.com/v1/oauth2/token'
DIGIKEY_PRODUCT_SEARCH_URL_V4 = 'https://sandbox-api.digikey.com/products/v4/search/keyword'

# Sanity Check That Authorisation Details Was Provided
if not DIGIKEY_CLIENT_ID or not DIGIKEY_CLIENT_SECRET:
    print("Missing client id or secret")
    quit()

def oauthV2_get_simple_access_token(url, client_id, client_secret):
    # Get the simple access token required for 2 Legged Authorization OAutV2.0 flow
    # This is typically used for basic search and retreival of publically avaliable information
    response = requests.post(
        url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            }
    )
    return response.json()

def oauthv2_product_search(url, client_id, token, keyword):
    # Dev Note: Why did I not just place the data?
    # https://stackoverflow.com/questions/15737434/python-requests-module-urlencoding-json-data
    data_payload = {
        "Keywords": str(keyword),
    }
    response = requests.post(
        url,
        headers = {            
            "X-DIGIKEY-Client-Id": client_id,
            "authorization": "Bearer {access_token}".format(access_token=token.get("access_token")),
            "content-type": "application/json",
            "accept": "application/json",
            },
        data = json.dumps(data_payload)
    )
    return response.json()

oauth_token = oauthV2_get_simple_access_token(DIGIKEY_TOKEN_URL_V4, DIGIKEY_CLIENT_ID, DIGIKEY_CLIENT_SECRET)
print(oauth_token)

search_result = oauthv2_product_search(DIGIKEY_PRODUCT_SEARCH_URL_V4, DIGIKEY_CLIENT_ID, oauth_token, "MCP2221A-I/SL-ND")

print(json.dumps(search_result, indent=4))