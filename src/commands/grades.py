import typer
from rich import print as stdout
from rich.console import Console
from typing_extensions import Annotated, Optional, List
from datetime import datetime
from core.auth.load_config import load_config_formatted
from core.grades.grades import get_grades
from core.grades.final import get_final_grades
from core.grades.gpa import calculate_gpa, calculate_final_gpa

app = typer.Typer()
console = Console()

@app.command('grades')
def grades(
    args: Annotated[
        Optional[List[str]],
        typer.Argument(help="baka grades [...subjects]")
    ] = None,
    final: Annotated[
        bool,
        typer.Option("--final", help="Display final grades.")
    ] = False,
):

    with console.status("[bold white]Loading...", spinner="dots"):
        (access_token, refresh_token, school_url) = load_config_formatted()

    if final: print_final_grades(args, access_token, refresh_token, school_url)
    else: print_grades(args, access_token, refresh_token, school_url)


def print_grades(args, access_token, refresh_token, school_url):

    with console.status("[bold white]Fetching the grades...", spinner="dots"):
        subjects = get_grades(access_token, refresh_token, school_url)

    if args:
        subjects = list(filter(lambda subject: subject['Subject']['Abbrev'].strip() in args, subjects))
    else:
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


def print_final_grades(args, access_token, refresh_token, school_url):

    with console.status("[bold white]Fetching the grades...", spinner="dots"):
        years = get_final_grades(access_token, refresh_token, school_url)

    if args:
        for year in years:
            for semester in year['Semesters']:
                semester['Grades'] = [
                    grade
                    for grade in semester['Grades']
                    if grade['SubjectAbbrev'].strip() in args
                ]
            year['Semesters'] = [
                semester for semester in year['Semesters'] if semester['Grades']
            ]
        years = [year for year in years if year['Semesters']]
    else:
        gpa = calculate_final_gpa(years)
        stdout(f'\nGPA: {gpa:.1f} / 4.0')

    for year in years:
        year_name = year['YearInSchool']
        semesters = year['Semesters']

        stdout(f'[bold white]\n----- Year {year_name} -----\n')

        for semester in semesters:

            semester_name = semester['SemesterName']
            semester_grades = semester['Grades']

            colors = ['green', '#c3ff00', 'yellow', 'orange', 'red']

            stdout(f'[bold white]{semester_name} Semester\n')

            for grade_entry in semester_grades:
                grade_text = grade_entry['GradeText']
                grade_subject = grade_entry['SubjectName']
                spaces = 4 - len(grade_text)

                try:
                    if grade_text == 'N' or grade_text == '?':
                        color = 'red'
                    else:
                        grade_value = int(grade_text)
                        color = colors[grade_value - 1]
                except:
                    color = 'white'

                stdout(f'[bold {color}]{grade_text}{spaces * " "}|   {grade_subject}')

    stdout()