# build a streamlit image for running the streamlit app

# Use the official Python image
FROM python:3.11-slim
# copy the poetry files into the image
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    software-properties-common \
    && curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
	| tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
	&& echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
	| tee /etc/apt/sources.list.d/ngrok.list \
	&& apt update \
	&& apt install ngrok \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
# install poetry
RUN pip install poetry \
# install the dependencies
  && poetry config virtualenvs.create false \
    && poetry install --no-dev
# set PYTHONPATH for streamlit
#ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
# Verify Streamlit installation
#RUN streamlit --version

ARG NGROK_AUTH_TOKEN
RUN ngrok config add-authtoken $NGROK_AUTH_TOKEN

# copy the context into the image (esclude the files in .dockerignore)

COPY ./ ./
# expose the port
EXPOSE 8501
# run the streamlit app
#CMD ["streamlit", "run", "app.py"]
