import typer
from rich import print as stdout
from rich.console import Console
from core.auth.load_config import load_config_formatted
from core.subjects.subjects import get_subjects

app = typer.Typer()
console = Console()

@app.command('subjects')
def subjects():

    with console.status("[bold white]Loading...", spinner="dots"):
        (access_token, refresh_token, school_url) = load_config_formatted()

    with console.status("[bold white]Fetching the subjects...", spinner="dots"):
        subjs = get_subjects(access_token, refresh_token, school_url)

    max_len = max((len(subject['SubjectName']) for subject in subjs), default=0)

    for subject in subjs:
        abbrev = subject['SubjectAbbrev']
        name = subject['SubjectName']
        teacher = subject['TeacherName']

        spaces_1 = 6 - len(abbrev)
        spaces_2 = max_len + 3 - len(name)

        stdout(f'[bold white]{abbrev}{spaces_1 * ' '}|   [/][yellow]{name}{spaces_2 * ' '}[bold white]|   [cyan]{teacher}')