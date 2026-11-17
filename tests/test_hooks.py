import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from hooks import post_gen_project as hook


@pytest.mark.parametrize("option", ["uv", "conda"])
def test_bootstrap_stops_before_commit_on_validation_failure(monkeypatch, option):
    manager = Mock()
    manager.run_subprocess_in_env.side_effect = [
        None,
        None,
        subprocess.CalledProcessError(1, "lint"),
    ]
    monkeypatch.setattr(hook, "get_package_manager", Mock(return_value=manager))
    run = Mock()
    monkeypatch.setattr(hook.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        hook.bootstrap_project(option, "isolated-env", "https://example.com/project.git")
    assert not any(call.args[0][:2] == ["git", "commit"] for call in run.call_args_list)
    assert manager.run_subprocess_in_env.call_args.kwargs["env_name"] == "isolated-env"


def test_installation_failure_does_not_run_hooks_or_commit(monkeypatch):
    manager = Mock()
    manager.create_environment.side_effect = subprocess.CalledProcessError(1, "install")
    monkeypatch.setattr(hook, "get_package_manager", Mock(return_value=manager))
    run = Mock()
    monkeypatch.setattr(hook.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        hook.bootstrap_project("uv", "isolated-env", "https://example.com/project.git")
    manager.run_subprocess_in_env.assert_not_called()
    assert not any(call.args[0][:2] == ["git", "commit"] for call in run.call_args_list)


@pytest.mark.parametrize(
    "option,expected",
    [
        ("uv", ["/tools/uv", "run", "python", "--version"]),
        ("conda", [Path("/tools/conda"), "run", "-n", "test-env", "python", "--version"]),
    ],
)
def test_manager_runs_in_selected_environment(monkeypatch, option, expected):
    run = Mock()
    monkeypatch.setattr(hook.subprocess, "run", run)
    manager = (
        hook.UvPackageManager(Path("/tools/uv"))
        if option == "uv"
        else hook.CondaLikePackageManager(Path("/tools/conda"), Path("environment.yaml"))
    )
    manager.run_subprocess_in_env("test-env", ["python", "--version"])
    run.assert_called_once_with(expected, check=True)


def test_missing_uv_has_actionable_error(monkeypatch):
    monkeypatch.setattr(hook.shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError, match="uv is not installed"):
        hook.get_package_manager("uv")


def test_invalid_manager_is_rejected():
    with pytest.raises(ValueError, match="Unsupported package manager"):
        hook.get_package_manager("unsupported")


def test_missing_conditional_file_does_not_delete_staging(tmp_path, monkeypatch):
    staging = tmp_path / ".conditional_files"
    staging.mkdir()
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match="does not exist"):
        hook.prepare_project("conda", "none", "ruff")
    assert staging.exists()
