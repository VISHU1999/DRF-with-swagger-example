FROM python:3.10.4
# set work directory
WORKDIR /code
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies
RUN apt update
RUN apt install -y postgresql-client
RUN pip install --upgrade pip
COPY ./requirements.txt /code/requirements.txt
# RUN chmod +x /opt/app/requirements.txt
RUN pip install -r requirements.txt
# copy project
COPY . /code
COPY ./docker-entrypoint.sh /code/docker-entrypoint.sh
RUN chmod +x /code/docker-entrypoint.sh
ENTRYPOINT ["/code/docker-entrypoint.sh"]
