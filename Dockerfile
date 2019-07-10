FROM simplifier/vonk:2.0.1

RUN apt-get update && apt-get install -y vim

COPY ./server/appsettings.json ./server/logsettings.json /app/
