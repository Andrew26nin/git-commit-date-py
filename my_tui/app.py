import json
import os

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def read_lines_from_file(filename):
    try:
        with open(filename, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        console.print(f"[red]Файл {filename} не найден![/red]")
        return []


def display_menu(lines):
    table = Table(title="Выберите строку")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Строка", style="magenta")

    for i, line in enumerate(lines, start=1):
        table.add_row(str(i), line.strip())

    console.print(table)


def select_line(lines):
    choices = [line.strip() for line in lines]
    selected_line = questionary.select(
        "Выберите строку:", choices=choices, default=None
    ).ask()

    if selected_line is None:
        console.print("[yellow]Вы отменили выбор.[/yellow]")
        return None

    return selected_line


def main():
    filename = "test.txt"
    lines = read_lines_from_file(filename)

    while True:
        selected_line = select_line(lines)

        if selected_line is None:
            continue

        console.print(f"[green]Вы выбрали строку:[/green] {selected_line}")


if __name__ == "__main__":
    main()
