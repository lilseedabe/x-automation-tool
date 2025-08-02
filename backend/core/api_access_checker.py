from backend.auth.user_service import get_user_api_keys
import requests

def check_x_api_access_level(api_key, api_secret, access_token, access_token_secret):
    """
    X(Twitter) APIのアクセスレベルを判定する（Free/Elevated/等）
    """
    url = "https://api.twitter.com/2/tweets?ids=20"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return "Elevated"
        elif resp.status_code == 403:
            return "Free"
        elif resp.status_code == 401:
            return "Invalid"
        else:
            return "Unknown"
    except Exception as e:
        return f"Error: {str(e)}"

def get_user_api_access_level(user_id):
    keys = get_user_api_keys(user_id)
    if not keys:
        return "NoKeys"
    return check_x_api_access_level(
        keys["api_key"], keys["api_secret"], keys["access_token"], keys["access_token_secret"]
    )