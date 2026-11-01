import json

def load_config():
    try:
        with open('auth.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

            access_token = data['access_token']
            refresh_token = data['refresh_token']
            school_url = data['school_url']

            return (access_token, refresh_token, school_url)

    # If the config file can't be loaded or data is missing
    except:
        return None