import typer
from rich import print as stdout
from core.auth.tokens import refresh_token as refresh
from core.auth.load_config import save_config

def update_tokens(refresh_token: str, school_url: str):
    try:
        new_tokens = refresh(school_url, refresh_token)
        access_token = new_tokens[0]
        refresh_token = new_tokens[1]

        save_config(access_token, refresh_token, school_url)
    except:
        stdout("[bold red]❌ ERROR: you have been logged out")
        raise typer.Exit(code=1)