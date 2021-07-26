# Data Science Template Repository

Basic setup for a data science project.


## Requirements

`anaconda` or `miniconda`.

## Setup Instructions (unix)

<ol>
<li>Create and enter directory for your new repository</li>
<li>Clone template repository</li>

```
git clone git@ac1-git1.umlaut.com:hsg/hsg/data-science/data-science-project-template.git .
```

<li>Set origin to point to new repository</li>

```
git remote set-url origin git@ac1-git1.umlaut.com:hsg/YOUR/NEW/PROJECT.git
```

<li>Configure tools</li>

```
env_name=YOUR_NEW_CONDA_ENV_NAME
conda env create -f environment.yml --name=${env_name}
conda activate $env_name
pre-commit install
```
</ol>
