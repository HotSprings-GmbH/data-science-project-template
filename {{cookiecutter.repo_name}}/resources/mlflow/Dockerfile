FROM python:3.9.15

ENV HOME="/root"
WORKDIR ${HOME}
RUN apt-get install -y git
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"

ENV PYTHON_VERSION=3.9.15
RUN pyenv install ${PYTHON_VERSION}
RUN pyenv global ${PYTHON_VERSION}

COPY ./resources/mlflow/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./scripts/wait-for-it.sh /tmp/wait-for-it.sh

CMD /tmp/wait-for-it.sh mlflow-db:3306 && mlflow server --backend-store-uri mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mlflow-db:3306/${MYSQL_DATABASE} --default-artifact-root s3://mlflow/ --host 0.0.0.0
