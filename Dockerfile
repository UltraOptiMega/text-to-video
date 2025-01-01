FROM python:3.9-alpine3.17

# Don't run as root
RUN adduser -D appuser && \
    # Set the working directory in the container
    mkdir -p /home/appuser/text-to-video && \
    chown appuser:appuser /home/appuser/text-to-video && \ 
    touch /tmp/gunicorn.log && \
    chown appuser:appuser /tmp/gunicorn.log && \
    apk update && apk add build-base ffmpeg chromium chromedriver libc6-compat  gcompat && \
    pip install --upgrade pip setuptools wheel && \
    # Use wget instead of curl since curl is external package in alpine
    # https://python-poetry.org/docs/#installation
    wget -O get-poetry.py https://install.python-poetry.org && \
    POETRY_HOME=/home/appuser/.poetry python3 get-poetry.py && \
    rm get-poetry.py

USER appuser

# Add Poetry to PATH
ENV PATH="/home/appuser/.poetry/bin:${PATH}"

WORKDIR /home/appuser/text-to-video

COPY --chown=appuser:appuser ./ .

# Install dependencies
RUN poetry install --no-root

EXPOSE 8000

# Run your Flask application using Gunicorn server for production
CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--preload", "--log-file", "/tmp/gunicorn.log", "--timeout", "180", "src:create_app()"]
