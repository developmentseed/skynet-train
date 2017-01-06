FROM python:2.7

# needed for `column` command
RUN apt-get update && apt-get install -y bsdmainutils

ADD . /workspace
WORKDIR /workspace

EXPOSE 8080

CMD ["monitor/start.sh"]
