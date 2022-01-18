# Data Science Template Repository

Basic setup for a data science project.

## Requirements

`anaconda` or `miniconda`.

---

## Setup Instructions (Unix)

<ol>
<li>Create and enter directory for your new repository</li>
<li>Clone template repository</li>

```
git clone git@ac1-git1.umlaut.com:hsg/hsg/data-science/data-science-project-template.git .
```

<li>Read template version and remove its git history</li>

```
version_tag=`git describe --tags --abbrev=0`
rm -rf .git
rm .gitlab-ci.yml .releaserc.json README.md
```

<li>Initialize a new repository and push it</li>

```
git init
git add .
git commit -m "Initialize from data science template version ${version_tag}"
git remote add origin git@ac1-git1.umlaut.com:hsg/YOUR/NEW/PROJECT.git
```

<li>Configure tools</li>

```
env_name=YOUR_NEW_CONDA_ENV_NAME
conda env create -f environment.yml --name=${env_name}
conda activate $env_name
pre-commit install
pre-commit install --hook-type commit-msg
```

</ol>

---

## Setup Instructions (Windows)

<ol>
<li>Create and enter directory for your new repository</li>
<li>Clone template repository</li>

```
git clone git@ac1-git1.umlaut.com:hsg/hsg/data-science/data-science-project-template.git .
```

<li>Read template version and remove its git history</li>

```
@for /f "delims=" %i in ('git describe --tags --abbrev^=0') do @set version_tag=%i
rmdir /S /Q .git
del .gitlab-ci.yml .releaserc.json README.md
```

<li>Initialize a new repository and push it</li>

```
git init
git add .
git commit -m "Initialize from data science template version %version_tag%"
git remote add origin git@ac1-git1.umlaut.com:hsg/YOUR/NEW/PROJECT.git
```

<li>Configure tools</li>

```
set env_name=YOUR_NEW_CONDA_ENV_NAME
conda env create -f environment.yml --name=%env_name%
conda activate %env_name%
pre-commit install
pre-commit install --hook-type commit-msg
```

</ol>
