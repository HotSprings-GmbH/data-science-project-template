# pylint: disable=redefined-outer-name
# standard library imports
import os
import pathlib
import uuid

# third party imports
import pytest
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


def validate_base_project_files(env_dir):
    """
    Validates that the environment directory was created and contains the expected files
    """
    expected_dirs = [".git/", "data/"]
    for expected_dir in expected_dirs:
        expected_dir_path = env_dir.joinpath(expected_dir)
        assert expected_dir_path.is_dir(), f"Did not find dir: {expected_dir_path}"

    expected_files = [
        ".commitlintrc.yaml",
        ".gitattributes",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".prettierrc",
        ".pylintrc",
        "check_commit_msgs.sh",
        "environment.yaml",
        "pyproject.toml",
        "README.md",
    ]
    for expected_file in expected_files:
        expected_file_path = env_dir.joinpath(expected_file)
        assert expected_file_path.is_file(), f"Did not find file: {expected_file_path}"


def validate_gitlab_configuration(env_dir, expect_present=True):
    file_path = env_dir.joinpath(".gitlab-ci.yml")
    if expect_present:
        assert file_path.is_file(), f"Did not find file: {file_path}"
    else:
        assert not file_path.is_file(), f"Expected not to find file: {file_path}"


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
    [
        {},
        {"cicd_configuration": "gitlab"},
    ],
    indirect=["template_environment"],
)
def test_template(template_environment):
    env_dir, env_name, env_config = template_environment
    validate_base_project_files(env_dir)
    validate_gitlab_configuration(
        env_dir, expect_present=env_config.get("cicd_configuration") == "gitlab"
    )
    validate_pre_commit(env_dir, env_name)
