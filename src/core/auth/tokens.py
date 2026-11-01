import requests
import typer
from rich import print as stdout

def login(school_url: str, username: str, password: str):

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'client_id': 'ANDR',
        'grant_type': 'password',
        'username': username,
        'password': password
    }

    base_url = school_url
    path = '/api/login'
    url = f'{base_url.rstrip('/')}/{path.lstrip('/')}'

    res = requests.post(url, headers=headers, data=payload)

    if res.ok:
        data = res.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        return (access_token, refresh_token)
    else:
        stdout("[bold red]❌ ERROR: something went wrong")
        raise typer.Exit(code=1)

def refresh_token(school_url: str, token: str):

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'client_id': 'ANDR',
        'grant_type': 'refresh_token',
        'refresh_token': token
    }

    base_url = school_url
    path = '/api/login'
    url = f'{base_url.rstrip('/')}/{path.lstrip('/')}'

    res = requests.post(url, headers=headers, data=payload)

    if res.ok:
        data = res.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        return (access_token, refresh_token)
    else:
        stdout("[bold red]❌ ERROR: something went wrong")
        raise typer.Exit(code=1)