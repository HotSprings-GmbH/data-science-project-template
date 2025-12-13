# pylint: disable=redefined-outer-name
# standard library imports
import itertools
import json
import os
import pathlib
import random
import uuid

# third party imports
import pytest
import yaml
from cookiecutter.main import cookiecutter

# local imports
from hooks.post_gen_project import get_package_manager

TEMPLATE_DIRECTORY = str(pathlib.Path(__file__).parent.parent)
PACKAGE_MANAGER = get_package_manager()


@pytest.fixture(scope="function")
def template_environment(tmp_path, request):
    env_name = f"pytest_{uuid.uuid4()}-env"
    cookiecutter(
        template=TEMPLATE_DIRECTORY,
        output_dir=str(tmp_path),
        no_input=True,
        extra_context={"env_name": env_name, **request.param},
    )
    yield tmp_path.joinpath("data-science-project"), env_name, request.param
    PACKAGE_MANAGER.remove_env(env_name=env_name)


def get_all_possible_configuration_permutations(n_samples: int | None = 5):
    """
    Generates all possible configurations from cookiecutter.json for all elements where
    the value is a list (i.e., user has >1 pre-defined option). By default, 5 random
    permutations will be selected from all permutations and then tested afterwards.
    :param number_of_envs: How many environments should be built/tested. Defaults to 5. Set to None to test exhaustively
    :return: list of number_of_envs permutations that were randomly selected from all possible permutations.
    """
    with open(f"{TEMPLATE_DIRECTORY}/cookiecutter.json", "r", encoding="utf-8") as f:
        cookiecutter_config = json.load(f)

    option_fields = {key: val for key, val in cookiecutter_config.items() if isinstance(val, list)}
    option_keys, option_vals = zip(*option_fields.items())
    all_permutations = [
        dict(zip(option_keys, permutation)) for permutation in itertools.product(*option_vals)
    ]

    if n_samples is not None:
        if n_samples > len(all_permutations):
            return all_permutations

        return random.sample(all_permutations, n_samples)

    return all_permutations


def validate_base_project_files(env_dir: pathlib.Path):
    """
    Validates that the environment directory was created and contains the expected files
    """
    expected_dirs = [".git/", "data/"]
    for expected_dir in expected_dirs:
        expected_dir_path = env_dir.joinpath(expected_dir)
        assert expected_dir_path.is_dir(), f"Did not find dir: {expected_dir_path}"

    # Linter & CI files checked separately

    expected_files = [
        ".commitlintrc.yaml",
        ".gitattributes",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".prettierrc",
        "check_commit_msgs.sh",
        "environment.yaml",
        "pyproject.toml",
        "README.md",
    ]

    for expected_file in expected_files:
        expected_file_path = env_dir.joinpath(expected_file)
        assert expected_file_path.is_file(), f"Did not find file: {expected_file_path}"


def validate_python_environment(env_dir: pathlib.Path) -> list[str]:
    with open(env_dir.joinpath("environment.yaml"), "r", encoding="utf-8") as f:
        python_deps: list[str] = yaml.safe_load(f)["dependencies"]

    assert "python=3.10.9" in python_deps, "Did not find python=3.10.9 in environment.yaml"

    python_deps_noversion = [i.split("=")[0] for i in python_deps]

    return python_deps, python_deps_noversion


def validate_cicd_configuration(env_dir: pathlib.Path, cicd_configuration: str):
    all_possible_cicd_configs = {"gitlab": ".gitlab-ci.yml"}

    if cicd_configuration == "none":
        for fname in all_possible_cicd_configs.values():
            config_path = env_dir.joinpath(fname)
            assert (
                not config_path.is_file()
            ), f"Expected not to find cicd config {config_path} for {cicd_configuration}"
    else:
        try:
            fname = all_possible_cicd_configs[cicd_configuration]
        except KeyError:
            raise NotImplementedError(  # pylint: disable=W0707
                f"No test implemented for cicd for {cicd_configuration}"
            )

        config_path = env_dir.joinpath(fname)
        assert (
            config_path.is_file()
        ), f"Did not find cicd config {config_path} for {cicd_configuration}"


def validate_linter_configuration(
    env_dir: pathlib.Path, python_packages: list[str], linter_name: str
):
    match linter_name:
        case "pylint":
            config_name = ".pylintrc"
        case "ruff":
            config_name = "ruff.toml"
        case _:
            raise NotImplementedError(f"No test implemented for linter {linter_name}")

    file_path = env_dir.joinpath(config_name)

    assert (
        linter_name in python_packages
    ), f"Did not find {linter_name} in environment.yaml but specified as linter"
    assert file_path.is_file(), f"Did not find linter config: {file_path} for {linter_name}"


def validate_jupyter_configuration(python_packages: list[str], install_jupyter: str):
    match install_jupyter:
        case "yes":
            assert (
                "jupyter" in python_packages
            ), "install_jupyter == yes but jupyter not in environment.yaml"
            assert (
                "nbqa" in python_packages
            ), "install_jupyter == yes but nbqa not in environment.yaml"
        case "no":
            assert (
                not "jupyter" in python_packages
            ), "install_jupyter == no but jupyter in environment.yaml"
            assert (
                not "nbqa" in python_packages
            ), "install_jupyter == no but nbqa in environment.yaml"
        case _:
            raise ValueError(f"{install_jupyter} is not an option for install_jupyter")


def validate_pre_commit(env_dir, env_name):
    """
    Runs pre-commit hooks in the created environment to ensure that all generated/templated files are compatible
    :param env_dir:
    :param env_name:
    :return:
    """
    cwd = os.getcwd()
    os.chdir(env_dir)
    PACKAGE_MANAGER.run_subprocess_in_env(env_name, ["pre-commit", "run", "--all-files"])
    os.chdir(cwd)


@pytest.mark.parametrize(
    "template_environment",
    get_all_possible_configuration_permutations(n_samples=5),
    indirect=["template_environment"],
)
def test_template(template_environment):
    env_dir, env_name, env_config = template_environment
    validate_base_project_files(env_dir)

    _, python_packages = validate_python_environment(env_dir)

    validate_cicd_configuration(env_dir, cicd_configuration=env_config.get("cicd_configuration"))

    validate_linter_configuration(
        env_dir, python_packages, linter_name=env_config.get("linter_name")
    )

    validate_jupyter_configuration(
        python_packages, install_jupyter=env_config.get("install_jupyter")
    )

    validate_pre_commit(env_dir, env_name)
