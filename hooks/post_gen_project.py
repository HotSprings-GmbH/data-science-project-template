# standard library imports
import os
import pathlib
import subprocess
from abc import ABC, abstractmethod


# as cookiecutter is currently (v2.1.1) unable to support local imports in hooks
# the environment management code has to be included here
class CondaLikePackageManager(ABC):
    def __init__(self, executable_path: pathlib.Path):
        self.executable: pathlib.Path = executable_path

    @abstractmethod
    def create_env_from_yaml_file(self, yaml_file_path: pathlib.Path) -> None:
        """Create environment using specs from yaml file.

        Args:
            yaml_file_path (Path): pathlib.Path to yaml file with conda compatible env specs.
        """
        raise NotImplementedError

    def run_subprocess_in_env(self, env_name: str, cmd: list[str]):
        full_cmd = [self.executable, "run", "-n", env_name] + cmd
        subprocess.run(full_cmd, check=True)

    def remove_env(self, env_name: str):
        full_cmd = [self.executable, "env", "remove", "--name", env_name]
        subprocess.run(full_cmd, check=True)


class CondaPackageManager(CondaLikePackageManager):
    def create_env_from_yaml_file(self, yaml_file_path: pathlib.Path) -> None:
        full_cmd = [self.executable, "env", "create", "--file", str(yaml_file_path), "-q"]
        subprocess.run(full_cmd, check=True)


class MambaPackageManager(CondaLikePackageManager):
    def create_env_from_yaml_file(self, yaml_file_path: pathlib.Path) -> None:
        full_cmd = [self.executable, "env", "create", "--file", str(yaml_file_path), "-q"]
        subprocess.run(full_cmd, check=True)


class MicroMambaPackageManager(CondaLikePackageManager):
    def create_env_from_yaml_file(self, yaml_file_path: pathlib.Path) -> None:
        full_cmd = [self.executable, "create", "--file", str(yaml_file_path), "-q"]
        subprocess.run(full_cmd, check=True)


def get_package_manager() -> CondaLikePackageManager:
    system_env = os.environ
    if "MAMBA_EXE" in system_env:
        executable_micromamba = pathlib.Path(system_env["MAMBA_EXE"])
        return MicroMambaPackageManager(executable_path=executable_micromamba)
    if "CONDA_EXE" in system_env:
        if "mamba" in system_env["CONDA_EXE"]:
            executable_parent = pathlib.Path(system_env["CONDA_EXE"]).parent
            # conda.exe on windows, conda on unix
            # to be changed to mamba.exe on windows, mamba on unix
            executable_name_conda = pathlib.Path(system_env["CONDA_EXE"]).name
            executable_mamba = executable_parent.joinpath(
                executable_name_conda.replace("conda", "mamba")
            )
            return MambaPackageManager(executable_path=executable_mamba)
        else:
            executable_conda = pathlib.Path(system_env["CONDA_EXE"])
            return CondaPackageManager(executable_path=executable_conda)
    raise RuntimeError("Could not determine conda-like package manager.")


if __name__ == "__main__":
    # actual hook starts here
    # initialize new project repository
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "branch", "-m", "main"], check=True)
    subprocess.run(["git", "remote", "add", "origin", "{{cookiecutter.repo_url}}"], check=True)

    # Include or exclude CI setup based on user choice
    CI_FILES = {
        "none"   : [],
        "gitlab" : ['.gitlab-ci.yml', '.gitlab-ci-test.yaml', '.gitlab-ci-stages.yaml'],
        "github" : []
    }
    CI_option = '{{cookiecutter.CI_configuration}}'.lower()
    if CI_option == "github":
        print("Sorry, template does not support GitHub support yet.\nWe will proceed with no CI for now.")
    del CI_FILES[CI_option]
    files_to_exclude = {x for v in CI_FILES.values() for x in v}
    for file_name in files_to_exclude:
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    # setup environment
    PACKAGE_MANAGER = get_package_manager()
    PACKAGE_MANAGER.create_env_from_yaml_file(yaml_file_path=pathlib.Path("environment.yaml"))
    PACKAGE_MANAGER.run_subprocess_in_env(env_name="{{cookiecutter.env_name}}", cmd=["pre-commit"])

    # add template files to git and create initial commit
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initialize repo from data science template"], check=True
    )