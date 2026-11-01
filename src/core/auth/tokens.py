import requests
import typer

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

    res = requests.post(f'{school_url}/api/login', headers=headers, data=payload)

    if res.ok:
        data = res.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        return (access_token, refresh_token)
    else:
        typer.secho("❌ ERROR: something went wrong", fg=typer.colors.RED, bold=True)
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

    res = requests.post(f'{school_url}/api/login', headers=headers, data=payload)

    if res.ok:
        data = res.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        return (access_token, refresh_token)
    else:
        typer.secho("❌ ERROR: something went wrong", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)