FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=manage.py
CMD flask db upgrade && flask seed && gunicorn -w 2 -b 0.0.0.0:8000 --access-logfile - --error-logfile - "wsgi:app"
