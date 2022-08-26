# HSG Data Science Project Template

The HSG Data Science Project Template is a `cookiecutter` template to configure data science project repositories.
It features/configures:

-   a default `gitignore` file
-   a default `data/raw` folder tracked by `git-lfs`
-   line endings set to LF on check-in for text files (based on `git` heuristic for text file detection)
-   `pre-commit` checks including:
    -   code formatting of `python` and `.ipynb` files with `black`
    -   code linting of `python` and `.ipynb` files with `pylint`
    -   code formatting/checking for various configuration file types (e.g., `.yaml`)
    -   check of commit messages according to [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) specifications
-   configuration to run code formatting & linting with `gitlab` ci/cd pipelines

## Prerequisites

The template depends on the following software:

-   `mamba` (e.g., `miniforge` with `mamba` a.k.a. `mambaforge` [link](https://github.com/conda-forge/miniforge))
-   `python` (>= 3.7)
-   `cookiecutter` ([link](https://pypi.org/project/cookiecutter/))
-   `git`

## Usage Instructions

To setup a new project with the HSG data science template create the project repository in gitlab, run

```
cookiecutter https://github.com/HotSprings-GmbH/data-science-project-template
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

The projects created with this template are set up to run the formatting and linting checks configured
in `pylint` for every new commit pushed to `gitlab`. The CI/CD pipelines must be enabled within the gitlab repository settings (`Settings -> General -> Visibility, project features, permissions`).

## License

Licensed under the Apache License, Version 2.0 (the "License").
