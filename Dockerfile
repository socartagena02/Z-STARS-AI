FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY . .

CMD sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi:application"

CMD ["gunicorn", "core.wsgi:application"]