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

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set git commit as environment variable
ENV GIT_COMMIT=$GIT_COMMIT

EXPOSE 9094

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9094", "app:create_app()"]