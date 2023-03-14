FROM minio/mc@sha256:6ffd76764e8ca484de12c6ecaa352db3d8efd5c9d44f393718b29b6600e0a559


ENV AWS_ACCESS_KEY_ID ""
ENV AWS_SECRET_ACCESS_KEY ""

ENTRYPOINT sh -c "/tmp/wait-for-it.sh minio:9000 && \
    /usr/bin/mc alias set minio http://minio:9000 ${AWS_ACCESS_KEY_ID} ${AWS_SECRET_ACCESS_KEY} &&  \
    /usr/bin/mc mb minio/data &&  \
    /usr/bin/mc mb minio/mlflow;  \
    exit 0;"
