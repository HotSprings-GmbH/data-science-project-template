# Data Science Template Repository

Basic setup for a data science project.

Requirements: `anaconda` or `miniconda`.

Install and configure tools:

<ol>
<li> Replace `CHOOSE_YOUR_ENV_NAME` in environment.yaml</li>
<li> Run the following instruction:</li>
</ol>

```
conda env create -f environment.yml
ENV_NAME=$(grep "name: " environment.yml | cut -f2 -d: | sed 's/.$//')
conda activate $ENV_NAME
pre-commit install
```
