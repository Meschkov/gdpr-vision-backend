# use slim instead of alpine image because
# alpine don´t use glibc so it is possible that some python pacakges need to
FROM python:3.10-slim
# Default port for Cloud Run
ENV PORT 8080
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
# Copy local code to the container image.
WORKDIR $APP_HOME
COPY . ./
# Install dependencies
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r ./requirements.txt
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app