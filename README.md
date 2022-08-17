# Data Science Template Repository

Basic setup for a data science project.

## Requirements

`Mamba`

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
rm .releaserc.json README.md
sed -i -e '/release/d' .gitlab-ci-stages.yml
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
env_name=YOUR_NEW_MAMBA_ENV_NAME
mamba env create --name=${env_name} -f environment.yml
mamba activate $env_name
pre-commit install
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
Set-Content -Path ".gitlab-ci-stages.yml" -Value (get-content -Path ".gitlab-ci-stages.yml" | Select-String -Pattern 'release' -NotMatch)
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
set env_name=YOUR_NEW_MAMBA_ENV_NAME
mamba env create --name=%env_name% -f environment.yml
mamba activate %env_name%
pre-commit install
```

</ol>
