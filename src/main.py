import typer
from commands import auth
from commands import listen
from commands import grades
from commands import subjects

app = typer.Typer()

# Commands
app.add_typer(auth.app, help="Authentication.")
app.add_typer(listen.app, help="Listening for new events.")

app.add_typer(grades.app, help="Grades.")
app.add_typer(subjects.app, help="Subjects.")

# Run
if __name__ == "__main__":
    app()