import subprocess

# initialize new project repository
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "branch", "-m", "main"], check=True)
subprocess.run(["git", "add", "."], check=True)
subprocess.run(
    ["git", "commit", "-m", "chore: initialize repo from data science template"], check=True
)
subprocess.run(["git", "remote", "add", "origin", "{{cookiecutter.repo_url}}"], check=True)

# setup environment
subprocess.run(["mamba", "env", "create", "-f", "environment.yaml", "--quiet"], check=True)
subprocess.run(
    ["mamba", "run", "--no-banner", "-n", "{{cookiecutter.env_name}}", "pre-commit", "install"],
    check=True,
)
