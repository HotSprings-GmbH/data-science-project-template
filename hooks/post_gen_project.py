import os
import pathlib
import subprocess

path_conda_executable = pathlib.Path(os.environ["CONDA_EXE"])
path_mamba_executable = path_conda_executable.parent.joinpath(
    path_conda_executable.name.replace("conda", "mamba")
)

# initialize new project repository
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "add", "."], check=True)
subprocess.run(
    ["git", "commit", "-m", "chore: initialize repo from data science template"], check=True
)
subprocess.run(["git", "branch", "-m", "main"], check=True)
subprocess.run(["git", "remote", "add", "origin", "{{cookiecutter.repo_url}}"], check=True)

# setup environment
subprocess.run(
    [path_mamba_executable, "env", "create", "-f", "environment.yaml", "--quiet"], check=True
)
subprocess.run(
    [
        path_mamba_executable,
        "run",
        "--no-banner",
        "-n",
        "{{cookiecutter.env_name}}",
        "pre-commit",
        "install",
    ],
    check=True,
)
