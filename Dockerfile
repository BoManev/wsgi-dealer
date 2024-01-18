# ENV
ARG APPNAME="myapp"

# STAGE 1: Install project dependencies
FROM python:3.12 as deps
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --dev

# STAGE 2: 
FROM python:3.12 as main
ARG APPNAME
ENV LANG=C.UTF-8

RUN apt-get update \ 
	&& apt-get upgrade --assume-yes --no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*
COPY --from=deps /tmp/requirements.txt .
RUN python -m pip install --upgrade pip --no-cache-dir && \
    python -m pip install --requirement "requirements.txt" --no-cache-dir

RUN adduser --system --group --home /home/${APPNAME} ${APPNAME}
USER ${APPNAME}
# disable stderr/out from buffering
ENV PYTHONBUFFERED=1 
# disable bytecode writes
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/home/${APPNAME}

WORKDIR /home/${APPNAME}
# COPY ./alembic.ini .
# COPY ./alembic alembic/
COPY ./src ./src
COPY .env .
WORKDIR ./src
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-t 0", "app:app"]
