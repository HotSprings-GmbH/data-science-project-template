FROM python:3.9.15

RUN pip install mlflow boto3 pymysql cryptography

COPY ./scripts/wait-for-it.sh /tmp/wait-for-it.sh

CMD /tmp/wait-for-it.sh mlflow-db:3306 && mlflow server --backend-store-uri mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mlflow-db:3306/${MYSQL_DATABASE} --default-artifact-root s3://mlflow/ --host 0.0.0.0
