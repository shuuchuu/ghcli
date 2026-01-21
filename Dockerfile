FROM python:3.14-slim-trixie AS base
WORKDIR /app
FROM base AS uv
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/
COPY uv.lock pyproject.toml /app/
RUN uv export --frozen --no-dev --no-emit-project -o requirements.txt
FROM base
COPY --from=uv /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./pyproject.toml ./README.md ./src ./
RUN pip install .
CMD ["ghcli"]