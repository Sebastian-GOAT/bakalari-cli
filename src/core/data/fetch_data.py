import requests

def get_response(token: str, school_url: str, path: str):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {token}'
    }
    url = f'{school_url.rstrip('/')}/{path.lstrip('/')}'

    return requests.get(url, headers=headers)