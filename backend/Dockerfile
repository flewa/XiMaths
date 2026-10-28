# API Django de XiMaths : gunicorn, fichiers statiques de l'admin servis par whitenoise.
# La même image sert au planificateur (python manage.py run_jobs --loop).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.10.7 /uv /usr/local/bin/uv

WORKDIR /app
# Les dépendances d'abord : cette couche reste en cache tant que le verrou ne change pas.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --group prod

COPY . .
RUN DJANGO_DEBUG=0 DJANGO_SECRET_KEY=collectstatic-only python manage.py collectstatic --noinput

RUN useradd --create-home --uid 1000 app && chown -R app /app
USER app

EXPOSE 8000
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-"]
