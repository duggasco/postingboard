FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY ./backend .

# Create flask_session directory
RUN mkdir -p flask_session

RUN python database.py

EXPOSE 9094

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9094", "app:create_app()"]