import json
import tomllib
from pathlib import Path

import pytest
import yaml
from cookiecutter.main import cookiecutter

from hooks.post_gen_project import get_conditional_file_manager


@pytest.mark.parametrize("manager,linter", [("uv", "ruff"), ("conda", "pylint")])
def test_generated_configuration_regressions(tmp_path, monkeypatch, manager, linter):
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "cookiecutter.json").read_text())
    project = Path(
        cookiecutter(
            str(root),
            no_input=True,
            output_dir=str(tmp_path),
            accept_hooks=False,
            default_config={"replay_dir": str(tmp_path / "replay")},
            extra_context={
                "package_manager": manager,
                "linter_name": linter,
                "install_jupyter": "no",
                "cicd_configuration": "Azure DevOps",
            },
        )
    )
    monkeypatch.chdir(project)
    files = get_conditional_file_manager(manager, "Azure DevOps", linter)
    files.copy_chosen_files()
    files.clean_temp_dir()
    assert (project / "azure-pipelines.yml").is_file()
    hooks = yaml.safe_load((project / ".pre-commit-config.yaml").read_text())
    assert all(isinstance(repo["hooks"], list) and repo["hooks"] for repo in hooks["repos"])
    metadata = tomllib.loads((project / "pyproject.toml").read_text())
    if linter == "pylint":
        assert metadata["tool"]["black"]["line-length"] == config["_conventions"]["line_length"]
        assert metadata["tool"]["isort"]["line_length"] == config["_conventions"]["line_length"]
    if manager == "conda":
        environment = yaml.safe_load((project / "environment.yaml").read_text())
        dependencies = dict(dep.split("=", 1) for dep in environment["dependencies"])
        for package in ("black", "pylint"):
            assert dependencies[package] == config["_versions"][package]
