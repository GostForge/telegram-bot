FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main 2>/dev/null || \
    poetry install --no-interaction --no-ansi --no-root

COPY bot/ bot/
COPY README.md ./

RUN poetry install --no-interaction --no-ansi --only-root

CMD ["python", "-m", "bot.main"]
