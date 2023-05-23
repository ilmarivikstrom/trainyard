import shutil
from invoke.tasks import task, Call

@task
def clean(call: Call) -> None:
    dirs_to_delete = [
        "src/__pycache__",
        "build/",
        "dist/"
    ]
    for dir_to_delete in dirs_to_delete:
        try:
            shutil.rmtree(dir_to_delete)
            print(f"Deleted directory {dir_to_delete}.")
        except FileNotFoundError:
            print(f"Directory {dir_to_delete} not found.")

@task
def run(call: Call) -> None:
    call.run("python main.py")


@task
def build(call: Call) -> None:
    call.run("pyinstaller main.py")
