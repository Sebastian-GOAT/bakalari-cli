import typer
import json
from rich import print as stdout
from core.auth.tokens import refresh_token as refresh

def update_tokens(refresh_token: str, school_url: str):
    try:
        new_tokens = refresh(school_url, refresh_token)
        access_token = new_tokens[0]
        refresh_token = new_tokens[1]

        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "school_url": school_url
        }
        with open('auth.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except:
        stdout("[bold red]❌ ERROR: you have been logged out")
        raise typer.Exit(code=1)