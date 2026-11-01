import typer
from rich import print as stdout
from core.data.fetch_data import get_response
from core.data.tokens import update_tokens

def get_subjects(access_token: str, refresh_token: str, school_url: str):

    path = '/api/3/subjects'

    res = get_response(access_token, school_url, path)

    if res.status_code == 401:
        update_tokens(refresh_token, school_url)
        res = get_response(access_token, school_url, path)

    if res.ok:
        data = res.json()
        return data['Subjects']
    else:
        stdout("[bold red]❌ ERROR: couldn't fetch the subjects")
        raise typer.Exit(code=1)