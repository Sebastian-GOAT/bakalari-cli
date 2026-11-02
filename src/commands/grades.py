import typer
from rich import print as stdout
from rich.console import Console
from typing_extensions import Annotated, Optional, List
from datetime import datetime
from core.auth.load_config import load_config_formatted
from core.grades.grades import get_grades

app = typer.Typer()
console = Console()

def calculate_gpa(subjects):
    valid_averages = []

    for subject in subjects:
        average_text = subject.get('AverageText')

        if average_text is None:
            continue

        try:
            average = float(average_text.replace(",", "."))
        except (TypeError, ValueError):
            continue

        if 1 <= average <= 5:
            valid_averages.append(5 - average)

    if not valid_averages:
        return 0.0

    return sum(valid_averages) / len(valid_averages)


@app.command('grades')
def grades(
    args: Annotated[
        Optional[List[str]],
        typer.Argument(help="baka grades [...subjects]")
    ] = None
):

    with console.status("[bold white]Loading...", spinner="dots"):
        (access_token, refresh_token, school_url) = load_config_formatted()

    with console.status("[bold white]Fetching the grades...", spinner="dots"):
        subjects = get_grades(access_token, refresh_token, school_url)

    if args:
        subjects = list(filter(lambda subject: subject['Subject']['Abbrev'].strip() in args, subjects))

    gpa = calculate_gpa(subjects)
    stdout(f'\nGPA: {gpa:.1f} / 4.0')

    for subject in subjects:
        sub_name = subject['Subject']['Name']
        subject_grades = subject['Marks']
        average = float(subject['AverageText'].replace(",", "."))

        colors = ['green', '#c3ff00', 'yellow', 'orange', 'red']

        stdout(f'[bold white]\n----- {sub_name} -----\n')
        stdout(f'Average: {average}\n')

        for grade_entry in subject_grades:
            text = grade_entry['MarkText']
            spaces = 4 - len(text)
            date = datetime.fromisoformat(grade_entry['MarkDate']).strftime("%d.%m.%Y")
            is_points = grade_entry['IsPoints']

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