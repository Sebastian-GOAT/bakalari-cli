import typer
from commands import auth
from commands import marks

app = typer.Typer()

app.add_typer(auth.app, help="Authentication.")
app.add_typer(marks.app, help="Marks.")

if __name__ == "__main__":
    app()