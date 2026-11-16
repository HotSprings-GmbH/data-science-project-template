import json
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

from hooks.post_gen_project import prepare_project

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "cookiecutter.json").read_text())


def pytest_addoption(parser):
    parser.addoption("--bootstrap", action="store_true", help="Run networked installation tests")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--bootstrap"):
        for item in items:
            if "bootstrap" in item.keywords:
                item.add_marker(
                    pytest.mark.skip(reason="requires --bootstrap and installed managers")
                )


@pytest.fixture
def render_project(tmp_path, monkeypatch):
    def render(context):
        project = Path(
            cookiecutter(
                str(ROOT),
                output_dir=str(tmp_path),
                no_input=True,
                accept_hooks=False,
                extra_context=context,
                default_config={"replay_dir": str(tmp_path / "replay")},
            )
        )
        monkeypatch.chdir(project)
        prepare_project(
            context.get("package_manager", CONFIG["package_manager"][0]),
            context.get("cicd_configuration", CONFIG["cicd_configuration"][0]),
            context.get("linter_name", CONFIG["linter_name"][0]),
        )
        return project

    return render
