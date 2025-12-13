# standard library imports
import os
import pathlib
import shutil
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
        subprocess.run(full_cmd, check=True, env={"CONDA_YES": "true"})


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


def _verify_if_dir_valid(path_to_dir: pathlib.Path):
    if not path_to_dir.is_dir():
        raise RuntimeError(f"{path_to_dir} is not a valid directory.")


class ConditionalFileManager:
    def __init__(
        self,
        temp_files_dir: pathlib.Path,
        template_root_dir: pathlib.Path,
        relevant_paths_list: list[pathlib.Path],
    ) -> None:
        _verify_if_dir_valid(temp_files_dir)
        self.temp_files_dir = temp_files_dir
        _verify_if_dir_valid(template_root_dir)
        self.template_root_dir = template_root_dir
        for relevant_path in relevant_paths_list:
            if not self.temp_files_dir.joinpath(relevant_path).exists():
                raise RuntimeError(
                    f"A relevant path {relevant_path} does not exist in temp dir {self.temp_files_dir}."
                )
        self.relevant_paths_list = relevant_paths_list

    def clean_temp_dir(self) -> None:
        _verify_if_dir_valid(path_to_dir=self.temp_files_dir)
        shutil.rmtree(self.temp_files_dir)

    def copy_chosen_files(self) -> None:
        for relevant_path in self.relevant_paths_list:
            src = self.temp_files_dir.joinpath(relevant_path)
            dst = self.template_root_dir.joinpath(relevant_path)
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)


def get_conditional_file_manager(ci_cd_option: str, linter_option: str) -> ConditionalFileManager:
    template_root_dir = pathlib.Path.cwd()
    temp_files_dir = template_root_dir.joinpath(".conditional_files")
    relevant_paths = []

    match ci_cd_option:
        case "gitlab":
            relevant_paths.append(".gitlab-ci.yml")
        case "none":
            pass
        case _:
            raise NotImplementedError(f"Option {ci_cd_option} is not implemented as CI/CD pipeline")

    match linter_option:
        case "pylint":
            relevant_paths.append(".pylintrc")
        case "ruff":
            relevant_paths.append("ruff.toml")
        case _:
            raise NotImplementedError(f"Option {linter_option} is not implemented as Linter")

    manager = ConditionalFileManager(
        temp_files_dir=temp_files_dir,
        template_root_dir=template_root_dir,
        relevant_paths_list=relevant_paths,
    )

    return manager


if __name__ == "__main__":
    # actual hook starts here
    # initialize new project repository
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "branch", "-m", "main"], check=True)
    subprocess.run(["git", "remote", "add", "origin", "{{cookiecutter.repo_url}}"], check=True)

    # setup environment
    PACKAGE_MANAGER = get_package_manager()
    PACKAGE_MANAGER.create_env_from_yaml_file(yaml_file_path=pathlib.Path("environment.yaml"))
    PACKAGE_MANAGER.run_subprocess_in_env(env_name="{{cookiecutter.env_name}}", cmd=["pre-commit"])

    print("before")
    # setup ci/cd related files (if any)
    print("initializing")
    CICD_FILE_MANAGER = get_conditional_file_manager(
        ci_cd_option="{{cookiecutter.cicd_configuration}}",
        linter_option="{{cookiecutter.linter_name}}",
    )
    print("copying")
    CICD_FILE_MANAGER.copy_chosen_files()
    print("cleaning")
    CICD_FILE_MANAGER.clean_temp_dir()
    print("after")

    # add template files to git and create initial commit
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initialize repo from data science template"], check=True
    )
