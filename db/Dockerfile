FROM postgres

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD example
ENV POSTGRES_DB sentimentapp

COPY dump.sql /docker-entrypoint-initdb.d/
