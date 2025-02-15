"""Invoke tasks."""

import logging
import os
import shutil

from invoke import Call, task


@task
def clean(call: Call) -> None:
    logging.info(call)
    dirs_to_delete = ["build/", "dist/"]
    not_founds: list[str] = []

    for root, dirs, _ in os.walk("src", topdown=False):
        if "__pycache__" in dirs:
            dir_to_delete = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(dir_to_delete)
                logging.info(f"Deleted directory {dir_to_delete}.")
            except FileNotFoundError:
                not_founds.append(dir_to_delete)

    for dir_to_delete in dirs_to_delete:
        try:
            shutil.rmtree(dir_to_delete)
            logging.info(f"Deleted directory {dir_to_delete}.")
        except FileNotFoundError:  # noqa: PERF203
            not_founds.append(dir_to_delete)

    logging.info("Directories not found:")
    for not_found in not_founds:
        logging.info(f" - {not_found}")


@task
def run(call: Call) -> None:
    call.run("python main.py")


@task
def build(call: Call) -> None:
    # call.run("pyinstaller main.py --onefile --noconsole --add-data assets\\;dist\\assets\ --add-data levels\\;dist\levels\\")
    call.run("pyinstaller main.py --onefile --noconsole")
    call.run(r"if not exist dist\assets mkdir dist\assets")
    call.run(r"if not exist dist\levels mkdir dist\levels")
    call.run(r"xcopy assets dist\assets /E /H /C /I")
    call.run(r"xcopy levels dist\levels /E /H /C /I")


@task
def black(call: Call) -> None:
    call.run("black . --line-length 120")
