FROM --platform=linux/amd64 python:3.12-slim as base
RUN apt-get update && apt-get install --no-install-recommends -y build-essential 
RUN cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime \
    && echo "Asia/Seoul" > /etc/timezone
ENV PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME=$HOME/.poetry \
    POETRY_VERSION=1.8.4 \
    WORKDIR=/workspace 
ENV PATH="$POETRY_HOME/bin:$PATH"  \
    PYTHONPATH=$PYTHONPATH:$WORKDIR 
WORKDIR $WORKDIR

FROM base as poetry_installer
RUN apt-get install --no-install-recommends -y curl 
RUN curl -sSL https://install.python-poetry.org | python3 -

FROM base as dev
COPY --from=poetry_installer $POETRY_HOME $POETRY_HOME

FROM base as package_installer
COPY --from=poetry_installer $POETRY_HOME $POETRY_HOME
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --without dev 

FROM base as prod
COPY --from=package_installer /usr/local/bin /usr/local/bin
COPY --from=package_installer /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .