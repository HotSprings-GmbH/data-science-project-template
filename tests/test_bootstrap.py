"""Networked acceptance tests: pytest --bootstrap -m bootstrap.

Each case runs the actual Cookiecutter hook, then the generated CI tool commands.
Conda environments use unique names and are removed even when generation fails.
"""

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest
from conftest import ROOT
from cookiecutter.main import cookiecutter


@pytest.mark.bootstrap
@pytest.mark.parametrize("package_manager", ["uv", "conda"])
@pytest.mark.parametrize("linter,notebooks", [("ruff", "no"), ("pylint", "yes")])
def test_bootstrap(tmp_path, monkeypatch, package_manager, linter, notebooks):
    # A temporary HOME isolates Git configuration, Cookiecutter replay, and hook caches.
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Template Test")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "template@example.com")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Template Test")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "template@example.com")
    monkeypatch.setenv("PRE_COMMIT_HOME", str(tmp_path / "pre-commit"))
    env_name = f"template-test-{uuid.uuid4().hex}"
    executable = shutil.which(package_manager)
    assert executable, f"Install {package_manager} before running bootstrap tests"
    if package_manager == "conda":
        monkeypatch.setenv("CONDA_EXE", executable)
        monkeypatch.delenv("MAMBA_EXE", raising=False)
    project = tmp_path / "data-science-project"

    def run(args, check=True):
        return subprocess.run(args, cwd=project, check=check, text=True, capture_output=True)

    def tool(*args, check=True):
        prefix = (
            [executable, "run", "--no-sync"]
            if package_manager == "uv"
            else [executable, "run", "-n", env_name]
        )
        return run([*prefix, *args], check=check)

    try:
        cookiecutter(
            str(ROOT),
            no_input=True,
            output_dir=str(tmp_path),
            default_config={"replay_dir": str(tmp_path / "replay")},
            extra_context={
                "package_manager": package_manager,
                "env_name": env_name,
                "linter_name": linter,
                "install_jupyter": notebooks,
                "cicd_configuration": "GitHub",
            },
        )
        assert run(["git", "status", "--porcelain"]).stdout == ""
        assert run(["git", "branch", "--show-current"]).stdout.strip() == "main"
        assert (project / ".git/hooks/commit-msg").is_file()
        if package_manager == "uv":
            run([executable, "sync", "--locked", "--group", "dev"])
        sample = project / "example.py"
        sample.write_text('"""Example module."""\n\nANSWER = 42\n')
        if notebooks == "yes":
            (project / "example.ipynb").write_text(
                json.dumps(
                    {
                        "cells": [
                            {
                                "cell_type": "code",
                                "execution_count": None,
                                "metadata": {},
                                "outputs": [],
                                "source": ["ANSWER = 42\n"],
                            }
                        ],
                        "metadata": {},
                        "nbformat": 4,
                        "nbformat_minor": 5,
                    }
                )
            )
        run(["git", "add", "."])
        # Permit a first formatting pass; require a successful, stable second pass.
        tool("pre-commit", "run", "--hook-stage", "manual", "--all-files", check=False)
        run(["git", "add", "."])
        tool("pre-commit", "run", "--hook-stage", "manual", "--all-files")
        assert run(["git", "diff", "--exit-code"]).returncode == 0
        if notebooks == "yes":
            notebook = project / "example.ipynb"
            content = json.loads(notebook.read_text())
            content["cells"][0]["source"] = ["print(undefined_notebook_test_name)\n"]
            notebook.write_text(json.dumps(content))
            result = tool("pre-commit", "run", "--hook-stage", "manual", "--all-files", check=False)
            assert result.returncode != 0, result.stdout + result.stderr
            assert "undefined_notebook_test_name" in result.stdout + result.stderr
        sample.write_text('"""Broken example."""\n\nprint(undefined_template_test_name)\n')
        result = tool("pre-commit", "run", "--hook-stage", "manual", "--all-files", check=False)
        assert result.returncode != 0, result.stdout + result.stderr
        assert "undefined_template_test_name" in result.stdout + result.stderr
    finally:
        if package_manager == "conda":
            environments = subprocess.run(
                [executable, "env", "list", "--json"], check=True, text=True, capture_output=True
            )
            if any(Path(path).name == env_name for path in json.loads(environments.stdout)["envs"]):
                subprocess.run(
                    [executable, "env", "remove", "--name", env_name, "--yes"], check=True
                )
