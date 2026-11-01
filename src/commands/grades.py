import typer
from rich import print as stdout
from typing_extensions import Annotated, Optional, List
from datetime import datetime
from core.auth.load_config import load_config_formatted
from core.grades.grades import get_grades

app = typer.Typer()

@app.command('grades')
def grades(
    args: Annotated[
        Optional[List[str]],
        typer.Argument(help="baka grades [...subjects]")
    ] = None
):

    (access_token, refresh_token, school_url) = load_config_formatted()

    subjects = get_grades(access_token, refresh_token, school_url)

    if args:
        subjects = list(filter(lambda subject: subject['Subject']['Abbrev'].strip() in args, subjects))

    for subject in subjects:
        sub_name = subject['Subject']['Name']
        subject_grades = subject['Marks']

        stdout(f'[bold white]\n----- {sub_name} -----\n')
        for grade_entry in subject_grades:
            text = grade_entry['MarkText']
            spaces = 4 - len(text)
            date = datetime.fromisoformat(grade_entry['MarkDate']).strftime("%d.%m.%Y")
            is_points = grade_entry['IsPoints']

            colors = ['green', '#c3ff00', 'yellow', 'orange', 'red']

            try:
                if is_points:
                    color = 'cyan'
                else:
                    if text == 'N' or text == '?':
                        color = 'red'
                    else:
                        grade_value = int(text)
                        color = colors[grade_value - 1]
            except:
                color = 'white'

            stdout(f'[bold {color}]{text}{spaces * " "}|   {date}   |   {grade_entry["Caption"]}')

    stdout()