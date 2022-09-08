FROM python:3.8-alpine

ENV DEBUG true

RUN mkdir /application
COPY . /application

WORKDIR /application

RUN apk add --no-cache tzdata bluez bluez-libs sudo bluez-deprecated

COPY start.sh /
RUN chmod +x /start.sh

VOLUME /application/config.yaml

ENTRYPOINT ["/bin/sh", "-c", "/start.sh"]

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
