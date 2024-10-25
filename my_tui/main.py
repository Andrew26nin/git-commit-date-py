"""Main Application for Git Commit Date Changer"""

import os
import re
import signal
import subprocess
import sys
from datetime import datetime
from typing import List

import questionary
from rich.console import Console
from rich.panel import Panel

import argparse
from pathlib import Path


console = Console()


class Commit:
    """
    Represents a Git Commit.

    Attributes:
        hash (str): Commit hash.
        name (str): Author's name.
        email (str): Author's email.
        date (str): Commit date.
        subject (str): Commit subject.
    """

    def __init__(self, hash: str, name: str, email: str, date: str, subject: str):
        self.hash = hash
        self.name = name
        self.email = email
        self.date = date
        self.subject = subject

    def __repr__(self) -> str:
        return f"{self.date} -  {self.subject}  - {self.name}"


def parse_git_log(output_lines: List[str]) -> List[Commit]:
    """
    Parses Git log output into a list of Commit objects.

    Args:
        output_lines (List[str]): Output lines from the Git log command.

    Returns:
        List[Commit]: List of Commit objects.
    """
    commits = []
    commit_data = {}

    if not output_lines:
        return commits

    for line in output_lines:
        if line.startswith("commit"):
            if commit_data:
                commits.append(create_commit(commit_data))
            commit_data = {"hash": line.split()[1]}
        elif line.startswith("Author:"):
            match = re.match(r"Author: (.+) <(.+)>", line)
            if match:
                commit_data["name"] = match.group(1).strip()
                commit_data["email"] = match.group(2).strip()
        elif line.startswith("Date:"):
            commit_data["date"] = line.split(":", 1)[1].strip()
        elif line.strip():
            commit_data["subject"] = line.strip()

    # Add the last commit
    if commit_data:
        commits.append(create_commit(commit_data))

    return commits


def create_commit(data: dict) -> Commit:
    """
    Creates a Commit object from a dictionary.

    Args:
        data (dict): Dictionary containing commit data.

    Returns:
        Commit: Commit object.
    """
    return Commit(
        hash=data["hash"],
        name=data["name"],
        email=data["email"],
        date=data["date"],
        subject=data["subject"],
    )


def convert_commit_date_to_input_date(date_string: str) -> str:
    """
    Converts a Git commit date to an input-friendly format.

    Args:
        date_string (str): Date string in 'Tue Oct 8 11:59:23 2024 +0300' format.

    Returns:
        str: Date string in '2024.10.8 11:59:23 +0300' format.
    """
    dt = datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y %z")
    return dt.strftime("%Y.%m.%d %H:%M:%S %z")


def convert_input_date_to_commit_date(date_string: str) -> str:
    """
    Converts an input-friendly date to a Git commit date format.

    Args:
        date_string (str): Date string in '2024.10.8 11:59:23 +0300' format.

    Returns:
        str: Date string in 'Tue Oct 8 11:59:23 2024 +0300' format.
    """
    dt = datetime.strptime(date_string, "%Y.%m.%d %H:%M:%S %z")
    return dt.strftime("%a %b %d %H:%M:%S %Y %z")


# def get_git_log(repo_path: str, timeout: int = 10) -> List[str]:
#     """
#     Retrieves the Git log output for a given repository.
#     Args:
#         repo_path (str): Path to the Git repository.
#         timeout (int, optional): Timeout in seconds. Defaults to 10.

#     Returns:
#         List[str]: Output lines from the Git log command.
#     """
#     cmd = "git log --pretty"
#     try:
#         process = subprocess.Popen(
#             cmd,
#             cwd=repo_path,
#             shell=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             preexec_fn=os.setsid,
#         )
#         stdout, _ = process.communicate(timeout=timeout)

#         if process.returncode != 0:
#             raise subprocess.CalledProcessError(process.returncode, cmd, stdout)
#     except subprocess.CalledProcessError as e:
#         sys.stderr.write(e.output)
#     except subprocess.TimeoutExpired:
#         os.killpg(os.getpgid(process.pid), signal.SIGTERM)
#         sys.stderr.write("Killed by timeout")
#     else:
#         return str(stdout, "utf-8").split("\n")


# GIT_SET_DATE_TEMPLATE = 'git filter-branch -f --env-filter \'if [ $GIT_COMMIT = {} ]; then export GIT_COMMITTER_DATE="{}"; export GIT_AUTHOR_DATE="{}"; fi\''


# def set_git_date(
#     repo_path: str, commit: Commit, new_date: str, timeout: int = 600
# ) -> None:
#     """
#     Sets a new date for a Git commit.

#     Args:
#         repo_path (str): Path to the Git repository.
#         commit (Commit): Commit object.
#         new_date (str): New date in '2024.10.8 11:59:23 +0300' format.
#         timeout (int, optional): Timeout in seconds. Defaults to 600.
#     """
#     cmd = GIT_SET_DATE_TEMPLATE.format(commit.hash, new_date, new_date)
#     try:
#         process = subprocess.Popen(
#             cmd,
#             cwd=repo_path,
#             shell=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             preexec_fn=os.setsid,
#         )
#         stdout, _ = process.communicate(timeout=timeout)

#         if process.returncode != 0:
#             raise subprocess.CalledProcessError(process.returncode, cmd, stdout)
#     except subprocess.CalledProcessError as e:
#         sys.stderr.write(e.output)
#     except subprocess.TimeoutExpired:
#         os.killpg(os.getpgid(process.pid), signal.SIGTERM)
#         sys.stderr.write("Killed by timeout")


def execute_system_command(
    cmd: str, 
    cwd: str, 
    timeout: int = 10
) -> tuple:
    """
    Выполняет системную команду с обработкой ошибок и таймаутом.

    Args:
        cmd (str): Системная команда для выполнения.
        cwd (str): Рабочая директория для выполнения команды.
        timeout (int, optional): Таймаут в секундах. Defaults to 10.

    Returns:
        tuple: Кортеж, содержащий вывод команды (stdout) и индикатор ошибки (bool).
               Если команда выполнилась успешно, возвращает (stdout, False), 
               в случае ошибки или таймаута - (error_message, True).
    """
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        stdout, _ = process.communicate(timeout=timeout)
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd, stdout)
        
        return str(stdout, "utf-8"), False
    
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Command '{cmd}' failed with error:\n{e.output}")
        return str(e.output), True
    
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        error_msg = f"Command '{cmd}' killed by timeout ({timeout}s)"
        sys.stderr.write(error_msg + "\n")
        return error_msg, True


GIT_LOG_CMD = "git log --pretty"
GIT_SET_DATE_TEMPLATE = 'git filter-branch -f --env-filter \'if [ $GIT_COMMIT = {} ]; then export GIT_COMMITTER_DATE="{}"; export GIT_AUTHOR_DATE="{}"; fi\''


def get_git_log(repo_path: str, timeout: int = 10) -> List[str]:
    """
    Retrieves the Git log output for a given repository.

    Args:
        repo_path (str): Path to the Git repository.
        timeout (int, optional): Timeout in seconds. Defaults to 10.

    Returns:
        List[str]: Output lines from the Git log command or an empty list on error.
    """
    stdout, error_occurred = execute_system_command(GIT_LOG_CMD, repo_path, timeout)
    return stdout.split("\n") if not error_occurred else []


def set_git_date(
    repo_path: str, 
    commit: 'Commit',  # Принято использовать строковые литералы для forward reference
    new_date: str, 
    timeout: int = 600
) -> None:
    """
    Sets a new date for a Git commit.

    Args:
        repo_path (str): Path to the Git repository.
        commit (Commit): Commit object.
        new_date (str): New date in '2024.10.8 11:59:23 +0300' format.
        timeout (int, optional): Timeout in seconds. Defaults to 600.
    """
    cmd = GIT_SET_DATE_TEMPLATE.format(commit.hash, new_date, new_date)
    execute_system_command(cmd, repo_path, timeout)


def main() -> None:
    """
    Main application loop.
    """
    # repo_path = "/home/andrew/TEST_GIT"  # TODO: Add argument for repository path
    parser = argparse.ArgumentParser(description='Git Commit Date Changer')
    parser.add_argument('repo_path', type=str, help='Path to the Git repository')
    args = parser.parse_args()

    # Приводим путь к абсолютному
    repo_path = Path(args.repo_path).resolve()

    # Проверяем, что путь указывает на существующую директорию (не обязательно, но рекомендуется для повышения robustness)
    if not repo_path.is_dir():
        console.print(f"[red]Ошибка: '{repo_path}' не является существующей директорией.[/red]")
        return
    console.print(Panel(str(repo_path), highlight=True, title="Выбранный репозиторий"))
    while True:
        output_lines = get_git_log(repo_path)
        commits = parse_git_log(output_lines)
        choices = [
            {"name": str(commit), "value": commit, "disabled": False}
            for commit in commits
        ]
        selected_commit = questionary.select(
            "Choose a commit:", choices=choices, default=None
        ).ask()
        if selected_commit is None:
            break

        chosen_date = questionary.text(
            f"Change commit date [{selected_commit.date}]",
            default=convert_commit_date_to_input_date(selected_commit.date),
        ).ask()

        # Validate input date (TODO: implement validation)
        input_date = convert_input_date_to_commit_date(chosen_date)

        console.print(Panel(f"{selected_commit.date} -> {input_date}"))

        confirm_change = questionary.confirm("Save changes?", default=False).ask()
        if confirm_change:
            set_git_date(repo_path, selected_commit, input_date, timeout=60)
            console.print("[yellow]New date saved[/yellow]")

        confirm_continue = questionary.confirm("Continue?", default=True).ask()
        if not confirm_continue:
            break

    console.print("[green]Thank you![/green]")


if __name__ == "__main__":
    main()
