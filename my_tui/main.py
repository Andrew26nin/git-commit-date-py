"""Основной скрипт."""

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

console = Console()
# Получить список коммитов


# Пока имитировать как чтение из файла
def read_lines_from_file(filename):
    try:
        with open(filename, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        console.print(f"[red]Файл {filename} не найден![/red]")
        return []


class Commit:
    def __init__(self, hash, name, email, date, subject):
        self.hash = hash
        self.name = name
        self.email = email
        self.date = date
        self.subject = subject

    def __repr__(self):
        # return f"Commit(hash={self.hash}, name='{self.name}', email='{self.email}', date='{self.date}', subject='{self.subject}')"
        return f"{self.date} -  {self.subject}  - {self.name}"


def parse_git_log(output_lines) -> List[Commit]:
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

    # Добавляем последний коммит
    if commit_data:
        commits.append(create_commit(commit_data))

    return commits


def create_commit(data):
    return Commit(
        hash=data["hash"],
        name=data["name"],
        email=data["email"],
        date=data["date"],
        subject=data["subject"],
    )


def convert_commit_date_to_input_date(date_string):
    """Конвертирует дату из формата 'Tue Oct 8 11:59:23 2024 +0300'
    в формат '2024.10.8 11:59:23 +0300'"""
    dt = datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y %z")
    return dt.strftime("%Y.%m.%d %H:%M:%S %z")


def convert_input_date_to_commit_date(date_string):
    """Конвертирует дату из формата '2024.10.8 11:59:23 +0300'
    в формат 'Tue Oct 8 11:59:23 2024 +0300'"""
    dt = datetime.strptime(date_string, "%Y.%m.%d %H:%M:%S %z")
    return dt.strftime("%a %b %d %H:%M:%S %Y %z")


def get_git_log(repo_path, timeout: int = 10):
    cmd = "git log --pretty"
    try:
        process = subprocess.Popen(
            cmd,
            cwd=repo_path,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
        )
        stdout, _ = process.communicate(timeout=timeout)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd, stdout)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.output)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        sys.stderr.write("Killed by timeout")
    else:
        return str(stdout, "utf-8").split("\n")


GIT_SET_DATE_TEMPLATE = 'git filter-branch -f --env-filter \'if [ $GIT_COMMIT = {} ]; then export GIT_COMMITTER_DATE="{}"; export GIT_AUTHOR_DATE="{}"; fi\''


def set_git_date(repo_path, commit: Commit, new_date, timeout: int = 600):
    cmd = GIT_SET_DATE_TEMPLATE.format(commit.hash, new_date, new_date)
    try:
        process = subprocess.Popen(
            cmd,
            cwd=repo_path,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
        )
        stdout, _ = process.communicate(timeout=timeout)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd, stdout)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.output)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        sys.stderr.write("Killed by timeout")


def main():
    while True:
        # output_lines = read_lines_from_file("test.txt")
        # TODO: нужно добавить аргумент для получения пути репозитория
        repo_path = "/home/andrew/TEST_GIT"
        output_lines = get_git_log(repo_path)
        commits = parse_git_log(output_lines)
        choices = [
            {"name": str(commit), "value": commit, "disabled": False}
            for commit in commits
        ]
        selected_commit = questionary.select(
            "Choose commit:", choices=choices, default=None
        ).ask()
        if selected_commit is None:
            break

        chosen_date = questionary.text(
            "Change commit date [{}]".format(selected_commit.date),
            default=convert_commit_date_to_input_date(selected_commit.date),
        ).ask()
        # Проверить значение даты на корректность

        input_date = convert_input_date_to_commit_date(chosen_date)

        console.print(Panel("{} -> {}".format(selected_commit.date, input_date)))

        confirm_change = questionary.confirm("Save changes?", default=False).ask()
        if confirm_change:
            set_git_date(repo_path, selected_commit, input_date, timeout=60)
            console.print("[yellow]New date save[/yellow]")

        confirm_continue = questionary.confirm("Continue?", default=True).ask()
        if not confirm_continue:
            break

    console.print("[green]Thank you![/green]")


if __name__ == "__main__":
    main()
