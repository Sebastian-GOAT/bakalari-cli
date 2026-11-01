import typer
from rich.console import Console
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import get_style
import json
from pathlib import Path
from typing_extensions import Annotated, Optional, List
from core.auth.schools import get_cities, get_schools
from core.auth import tokens
from core.auth.load_config import load_config

app = typer.Typer()
console = Console()

choice_style = get_style({
    "questionmark": "#e0af68",
    "question": "bold #e0af68",
    "input": "#ffffff",
    "pointer": "#e0af68",
    "scrolling-indicator": "#e0af68",
    "marker": "#e0af68",
    "fuzzy_match": "#e0af68 bold"
}, style_override=False)

@app.command('login')
def login(
    args: Annotated[
        Optional[List[str]], 
        typer.Argument(help="baka login [school_url] [username] [password]")
    ] = None
):

    # Direct arguments
    if args:
        if len(args) != 3:
            typer.secho("❌ ERROR: you must provide all 3 arguments", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)

        config = load_config()
        if config:
            typer.secho(f"You are already logged in at {config[2]}", fg=typer.colors.RED, bold=True)
            return

        (school_url, username, password) = args

        with console.status("[bold white]Logging in...", spinner="dots"):
            (access_token, refresh_token) = tokens.login(school_url, username, password)

        data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'school_url': school_url
        }
        with open('auth.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        typer.secho(f'Successfully logged in as {username}', fg=typer.colors.GREEN, bold=True)

        return

    # Load the auth config
    config = load_config()
    if config:
        typer.secho(f"You are already logged in at {config[2]}", fg=typer.colors.RED, bold=True)
        return

    # Get the city
    with console.status("[bold white]Loading...", spinner="dots"):
        cities = get_cities()

    formatted_choices = [
        Choice(
            value=city, 
            name=f"{city['name']}"
        )
        for city in cities if city.get('name')
    ]

    selected_city_dict = inquirer.fuzzy(
        message="Enter your city:",
        choices=formatted_choices,
        style=choice_style
    ).execute()

    city = selected_city_dict['name']

    # Get the school
    with console.status("[bold white]Searching...", spinner="dots"):
        schools = get_schools(city)

    formatted_choices = [
        Choice(
            value=school,
            name=school['name']
        )
        for school in schools if school.get('name')
    ]

    selected_city_dict = inquirer.fuzzy(
        message="Enter your school:",
        choices=formatted_choices,
        style=choice_style
    ).execute()

    school_url = selected_city_dict['schoolUrl']

    # Get user's credentials
    username = typer.prompt(typer.style("Enter your username", fg=typer.colors.YELLOW, bold=True))
    password = typer.prompt(typer.style("Enter your password", fg=typer.colors.YELLOW, bold=True))

    with console.status("[bold white]Logging in...", spinner="dots"):
        (access_token, refresh_token) = tokens.login(school_url, username, password)

    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'school_url': school_url
    }
    with open('auth.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    typer.secho(f'Successfully logged in as {username}', fg=typer.colors.GREEN, bold=True)

@app.command('logout')
def logout():
    file = Path('auth.json')
    file.unlink(missing_ok=True)

if __name__ == "__main__":
    app()