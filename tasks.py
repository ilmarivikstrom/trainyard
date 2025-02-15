import shutil

from invoke.tasks import Call, task


@task
def clean(call: Call) -> None:
    print(call)
    dirs_to_delete = ["src/__pycache__", "build/", "dist/"]
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
    # call.run("pyinstaller main.py --onefile --noconsole --add-data assets\\;dist\\assets\ --add-data levels\\;dist\levels\\")
    call.run("pyinstaller main.py --onefile --noconsole")
    call.run(r"if not exist dist\assets mkdir dist\assets")
    call.run(r"if not exist dist\levels mkdir dist\levels")
    call.run(r"xcopy assets dist\assets /E /H /C /I")
    call.run(r"xcopy levels dist\levels /E /H /C /I")


@task
def black(call: Call) -> None:
    call.run("black . --line-length 120")
