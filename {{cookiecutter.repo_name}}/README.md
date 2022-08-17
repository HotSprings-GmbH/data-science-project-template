# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Usage instructions:

To activate the mamba environment run:

```
mamba activate {{cookiecutter.env_name}}
```

## Setup CI/CD pipelines in gitlab

With the current configuration the project is set up to run `pre-commit` checks on every new commit pushed to gitlab.
The CI/CD pipelines must be enabled within the gitlab repository settings (`Settings -> General -> Visibility, project features, permissions`).
