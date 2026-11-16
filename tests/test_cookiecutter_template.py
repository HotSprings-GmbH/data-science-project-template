import itertools
import json
import tomllib

import pytest
import yaml
from conftest import CONFIG
from packaging.requirements import Requirement

OPTIONS = ("package_manager", "install_jupyter", "linter_name", "cicd_configuration")
CASES = [
    dict(zip(OPTIONS, values, strict=True))
    for values in itertools.product(*(CONFIG[key] for key in OPTIONS))
]
CI_FILES = {
    "GitHub": ".github/workflows/ci.yml",
    "GitLab": ".gitlab-ci.yml",
    "Azure DevOps": "azure-pipelines.yml",
}


@pytest.mark.parametrize("context", CASES, ids=lambda c: "-".join(c.values()))
def test_generated_project_contract(render_project, context):
    project = render_project(context)
    assert (project / "data/raw/.gitkeep").is_file()
    assert not (project / ".conditional_files").exists()
    assert not (project / ".git").exists()  # Rendering must not bootstrap the project.
    for filename in (
        "README.md",
        ".gitignore",
        ".gitattributes",
        ".commitlintrc.yaml",
        ".prettierrc",
        "check_commit_msgs.sh",
    ):
        assert (project / filename).is_file(), filename
    for name, filename in CI_FILES.items():
        assert (project / filename).exists() == (context["cicd_configuration"] == name)
    assert (project / ".pylintrc").exists() == (context["linter_name"] == "pylint")
    assert (project / "environment.yaml").exists() == (context["package_manager"] == "conda")

    for path in project.rglob("*"):
        assert "cookiecutter." not in str(path.relative_to(project))
        if not path.is_file():
            continue
        text = path.read_text()
        assert "cookiecutter." not in text, path
        assert "{%" not in text, path
        if path.suffix == ".toml":
            tomllib.loads(text)
        elif path.suffix in (".yaml", ".yml"):
            yaml.safe_load(text)
        elif path.suffix in (".json", ".ipynb") or path.name == ".prettierrc":
            json.loads(text)

    metadata = tomllib.loads((project / "pyproject.toml").read_text())
    if context["linter_name"] == "pylint":
        assert metadata["tool"]["black"]["line-length"] == CONFIG["_conventions"]["line_length"]
        assert metadata["tool"]["isort"]["line_length"] == CONFIG["_conventions"]["line_length"]
    else:
        assert metadata["tool"]["ruff"]["line-length"] == CONFIG["_conventions"]["line_length"]
    expected = {"pre-commit": CONFIG["_versions"]["pre_commit"]}
    tools = ["ruff"] if context["linter_name"] == "ruff" else ["black", "pylint"]
    if context["install_jupyter"] == "yes":
        tools += ["jupyter", "nbqa"]
    expected.update({tool: CONFIG["_versions"][tool] for tool in tools})
    if context["package_manager"] == "uv":
        dependencies = [Requirement(dep) for dep in metadata["dependency-groups"]["dev"]]
        assert {dep.name: str(dep.specifier) for dep in dependencies} == {
            name: f"=={version}" for name, version in expected.items()
        }
        assert metadata["project"]["requires-python"] == f">={CONFIG['_versions']['python']}"
    else:
        environment = yaml.safe_load((project / "environment.yaml").read_text())
        assert dict(dep.split("=", 1) for dep in environment["dependencies"]) == {
            **expected,
            "python": CONFIG["_versions"]["python"],
        }
        assert environment["name"] == "data-science-project-env"

    hooks_config = yaml.safe_load((project / ".pre-commit-config.yaml").read_text())
    hooks = {hook["id"] for repo in hooks_config["repos"] for hook in repo["hooks"]}
    assert {"black", "pylint"}.issubset(hooks) == (context["linter_name"] == "pylint")
    notebook_hook = f"nbqa-{context['linter_name']}"
    assert (notebook_hook in hooks) == (context["install_jupyter"] == "yes")
    if context["cicd_configuration"] == "GitHub":
        assert "${{ github.ref_name }}" in (project / CI_FILES["GitHub"]).read_text()


def test_custom_project_values(render_project):
    project = render_project(
        {
            "project_name": "Customer Analytics",
            "env_name": "custom-env",
            "project_description": "Analyse customer behaviour.",
            "package_manager": "conda",
        }
    )
    assert project.name == "customer-analytics"
    assert "Analyse customer behaviour." in (project / "README.md").read_text()
    assert (
        tomllib.loads((project / "pyproject.toml").read_text())["project"]["name"] == project.name
    )
    assert yaml.safe_load((project / "environment.yaml").read_text())["name"] == "custom-env"
