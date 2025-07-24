FROM python:3.11-slim

# Accept git commit as build argument
ARG GIT_COMMIT=unknown

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY ./backend .

# Create flask_session directory
RUN mkdir -p flask_session

RUN python database.py

# Set git commit as environment variable
ENV GIT_COMMIT=$GIT_COMMIT

EXPOSE 9094

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9094", "app:create_app()"]