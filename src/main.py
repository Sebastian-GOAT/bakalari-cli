import typer
from commands import auth
from commands import grades
from commands import subjects

app = typer.Typer()

app.add_typer(auth.app, help="Authentication.")
app.add_typer(grades.app, help="Grades.")
app.add_typer(subjects.app, help="Subjects.")

if __name__ == "__main__":
    app()