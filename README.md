# HSG Data Science Template

## Prerequisites

The template depends on the following software:

-   `mamba` (e.g., `miniforge` with `mamba` a.k.a. `mambaforge` [link](https://github.com/conda-forge/miniforge))
-   `python` (>= 3.7)
-   `cookiecutter` ([link](https://pypi.org/project/cookiecutter/))
-   `git`

## Usage Instructions

To setup a new project with the HSG data science template create the project repository in gitlab, run

```
cookiecutter https://ac1-git1.umlaut.com/hsg/hsg/data-science/data-science-templates/data-science-project-template.git
```

and fill out the needed information.

## Development Instructions

Checkout the repository, run

```
mamba env create -f environment.yaml
mamba activate data-science-project-template
pre-commit install
```

and start developing.

## Setup CI/CD pipelines in gitlab

The project is set up to run:

-   `pre-commit` checks on every new commit pushed to gitlab
-   `semantic-release` on every MR to main

To enable the CI/CD setup in gitlab please use the following steps:

-   enable `CI/CD` pipelines in `Settings -> General -> Visibility, project features, permissions`.
-   create a project access token named `GITLAB_TOKEN` in `Settings -> Access Tokens` with `Maintainer` role and `api` + `write_repository` scopes.
-   copy the token value appearing at the top of the page after the token creation
-   create a `masked` and `protected` variable called `GITLAB_TOKEN` in `CI/CD -> Variables` using the previously created token value
