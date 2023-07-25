# pylint: disable=redefined-outer-name
# standard library imports
import pathlib
import uuid

# third party imports
import pytest
from cookiecutter.main import cookiecutter

# local imports
from hooks.post_gen_project import get_package_manager

TEMPLATE_DIRECTORY = str(pathlib.Path(__file__).parent.parent)
PACKAGE_MANAGER = get_package_manager()


@pytest.fixture
def default_template(tmp_path):
    env_name_id = f"pytest_{uuid.uuid4()}-env"
    cookiecutter(
        template=TEMPLATE_DIRECTORY,
        output_dir=str(tmp_path),
        no_input=True,
        extra_context={"env_name": env_name_id},
    )
    yield tmp_path.joinpath("data-science-project")
    PACKAGE_MANAGER.remove_env(env_name=env_name_id)


def test_default_template(default_template):
    expected_dirs = [".git/", "data/"]
    for expected_dir in expected_dirs:
        expected_dir_path = default_template.joinpath(expected_dir)
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
        expected_file_path = default_template.joinpath(expected_file)
        assert expected_file_path.is_file(), f"Did not find file: {expected_file_path}"
