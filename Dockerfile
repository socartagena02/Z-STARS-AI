FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m django
RUN SECRET_KEY=dummy \
    ALLOWED_HOSTS=localhost \
    TWO_FACTOR_KEY=dummy \
    PSEUDONYM_KEY=dummy \
    python manage.py collectstatic --noinput

RUN chown -R django:django /app

USER django

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT"]

EXPOSE 8000