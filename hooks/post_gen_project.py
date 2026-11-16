# standard library imports
import os
import pathlib
import shutil
import subprocess
from abc import ABC, abstractmethod


class PackageManager(ABC):
    @abstractmethod
    def create_environment(self): ...

    @abstractmethod
    def run_subprocess_in_env(self, env_name: str, cmd: list[str], check: bool = True): ...


# as cookiecutter is currently (v2.1.1) unable to support local imports in hooks
# the environment management code has to be included here
class CondaLikePackageManager(PackageManager):
    def __init__(self, executable_path: pathlib.Path, yaml_file_path: pathlib.Path):
        self.executable: pathlib.Path = executable_path
        self.yaml_file_path: pathlib.Path = (
            yaml_file_path  # pathlib.Path to yaml file with conda compatible env specs.
        )

    def run_subprocess_in_env(self, env_name: str, cmd: list[str], check: bool = True):
        full_cmd = [self.executable, "run", "-n", env_name] + cmd
        subprocess.run(full_cmd, check=check)

    def create_environment(self) -> None:
        full_cmd = [self.executable, "env", "create", "--file", str(self.yaml_file_path), "-q"]
        subprocess.run(full_cmd, check=True)

    def remove_environment(self, env_name: str):
        full_cmd = [self.executable, "env", "remove", "--name", env_name]
        subprocess.run(full_cmd, check=True, env={"CONDA_YES": "true"})


class UvPackageManager(PackageManager):
    def __init__(self, executable_path: pathlib.Path):
        self.executable_path = executable_path

    def create_environment(self) -> None:
        subprocess.run(
            [str(self.executable_path), "sync"],
            check=True,
        )

    def run_subprocess_in_env(self, env_name: str, cmd: list[str], check: bool = True) -> None:
        subprocess.run(
            [str(self.executable_path), "run", *cmd],
            check=check,
        )


def get_package_manager(package_manager_option: str) -> PackageManager:
    match package_manager_option:
        case "uv":
            return get_uv_package_manager()
        case "conda":
            return get_conda_package_manager()
        case _:
            raise ValueError(f"Unsupported package manager {package_manager_option}")


def get_uv_package_manager() -> UvPackageManager:
    executable = shutil.which("uv")
    if executable is None:
        raise RuntimeError("uv is not installed or not on PATH.")
    return UvPackageManager(executable_path=pathlib.Path(executable))


def get_conda_package_manager() -> CondaLikePackageManager:
    system_env = os.environ
    if "MAMBA_EXE" in system_env:
        executable = pathlib.Path(system_env["MAMBA_EXE"])
    elif "CONDA_EXE" in system_env:
        if "mamba" in system_env["CONDA_EXE"]:
            executable_parent = pathlib.Path(system_env["CONDA_EXE"]).parent
            # conda.exe on windows, conda on unix
            # to be changed to mamba.exe on windows, mamba on unix
            executable_name_conda = pathlib.Path(system_env["CONDA_EXE"]).name
            executable = executable_parent.joinpath(executable_name_conda.replace("conda", "mamba"))
        else:
            executable = shutil.which("conda")

            if executable is None:
                raise RuntimeError("Could not determine conda-like package manager.")

            executable = pathlib.Path(executable)
    else:
        raise RuntimeError("Could not determine conda-like package manager.")

    return CondaLikePackageManager(
        executable_path=executable, yaml_file_path=pathlib.Path("environment.yaml")
    )


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
                    f"A relevant path {relevant_path} does not exist in temp dir {self.temp_files_dir}."  # noqa: E501
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
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)


def get_conditional_file_manager(
    package_manager_option: str, ci_cd_option: str, linter_option: str
) -> ConditionalFileManager:
    template_root_dir = pathlib.Path.cwd()
    temp_files_dir = template_root_dir.joinpath(".conditional_files")
    relevant_paths = []

    match package_manager_option:
        case "conda":
            relevant_paths.append("environment.yaml")

    match ci_cd_option.lower():
        case "github":
            relevant_paths.append(".github/workflows/ci.yml")
        case "azure devops":
            relevant_paths.append(".azure-pipelines.yml")
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
            pass
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

    print("Initializing conditional files")
    CONDITIONAL_FILE_MANAGER = get_conditional_file_manager(
        package_manager_option="{{cookiecutter.package_manager}}",
        ci_cd_option="{{cookiecutter.cicd_configuration}}",
        linter_option="{{cookiecutter.linter_name}}",
    )
    print("Copying...")
    CONDITIONAL_FILE_MANAGER.copy_chosen_files()
    print("Cleaning...")
    CONDITIONAL_FILE_MANAGER.clean_temp_dir()

    # setup environment
    print("Initializing environment using {{cookiecutter.package_manager}}")
    PACKAGE_MANAGER = get_package_manager(package_manager_option="{{cookiecutter.package_manager}}")
    PACKAGE_MANAGER.create_environment()
    PACKAGE_MANAGER.run_subprocess_in_env(
        env_name="{{cookiecutter.env_name}}", cmd=["pre-commit", "install", "--install-hooks"]
    )

    # Make sure all linting checks work after templating
    print("Checking files...")
    subprocess.run(["git", "add", "."], check=True)

    PACKAGE_MANAGER.run_subprocess_in_env(
        env_name="{{cookiecutter.env_name}}", cmd=["pre-commit", "run", "--all-files"], check=False
    )

    # add template files to git and create initial commit
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initialize repo from data science template"], check=True
    )
