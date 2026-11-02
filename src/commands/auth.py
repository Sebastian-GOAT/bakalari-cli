import typer
from rich import print as stdout
from rich.console import Console
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import get_style
from typing_extensions import Annotated, Optional, List
from core.auth.schools import get_cities, get_schools
from core.auth import tokens
from core.auth.load_config import delete_config, load_config, save_config

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
            stdout("[bold red]❌ ERROR: you must provide all 3 arguments")
            raise typer.Exit(code=1)

        config = load_config()
        if config:
            stdout(f"[bold red]❌ ERROR: you are already logged in at {config[2]}")
            raise typer.Exit(code=1)

        (school_url, username, password) = args

        with console.status("[bold white]Logging in...", spinner="dots"):
            (access_token, refresh_token) = tokens.login(school_url, username, password)

        with console.status("[bold white]Loading...", spinner="dots"):
            save_config(access_token, refresh_token, school_url)

        stdout(f'[bold green]Successfully logged in as {username}.')

        return

    # Load the auth config
    with console.status("[bold white]Loading...", spinner="dots"):
        config = load_config()
        if config:
            stdout(f"You are already logged in at {config[2]}")
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

    save_config(access_token, refresh_token, school_url)

    stdout(f'[bold green]Successfully logged in as {username}.')

@app.command('logout')
def logout():

    with console.status("[bold white]Loading...", spinner="dots"):
        config = load_config()

    if not config:
        stdout("[bold red]❌ ERROR: you are already logged out")
        raise typer.Exit(code=1)

    with console.status("[bold white]Loading...", spinner="dots"):
        delete_config()
    
    stdout(f'[bold green]Successfully logged out.')

if __name__ == "__main__":
    app()