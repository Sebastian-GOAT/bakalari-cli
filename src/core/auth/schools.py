import requests
import typer
import urllib.parse

def get_cities():

    headers = {
        'Accept': 'application/json'
    }

    res = requests.get('https://sluzby.bakalari.cz/api/v1/municipality', headers=headers)

    if res.ok:
        return res.json()
    else:
        typer.secho("❌ ERROR: couldn't reach the Bakaláři servers", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)

def get_schools(city: str):

    url = f'https://sluzby.bakalari.cz/api/v1/municipality/{urllib.parse.quote(city)}'
    headers = {
        'Accept': 'application/json'
    }

    res = requests.get(url, headers=headers)

    if res.ok:
        data = res.json()
        return data['schools']
    else:
        typer.secho("❌ ERROR: couldn't reach the Bakaláři servers", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)