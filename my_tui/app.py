import questionary
from rich.console import Console
from rich.panel import Panel

console = Console()

EXIT_FLAG=">> Выход"

def read_lines_from_file(filename):
    try:
        with open(filename, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        console.print(f"[red]Файл {filename} не найден![/red]")
        return []


def select_line(lines):
    choices = [line.strip() for line in lines]
    choices.append(EXIT_FLAG)

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

        if selected_line == EXIT_FLAG or selected_line is None:
            console.print("[green]Спасибо за использование программы![/green]")
            break

        console.print(f"[green]Вы выбрали строку:[/green] {selected_line}")


if __name__ == "__main__":
    main()
