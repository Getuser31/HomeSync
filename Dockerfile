FROM postgres:16
LABEL authors="karlz"

ENV POSTGRES_USER=myuser \
    POSTGRES_PASSWORD=password \
    POSTGRES_DB=homesync