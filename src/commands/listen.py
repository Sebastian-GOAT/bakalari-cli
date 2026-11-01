import typer
import time
from rich import print as stdout
from core.listen.grades import fetch

app = typer.Typer()

INTERVAL_SECONDS = 30

@app.command('listen')
def listen():
    try:
        while True:
            fetch()
            time.sleep(INTERVAL_SECONDS) # Execute every 'x' seconds
    except KeyboardInterrupt:
        stdout('[bold yellow]Stopped listening.')