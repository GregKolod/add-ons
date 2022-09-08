ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8


RUN apk add --no-cache tzdata bluez bluez-libs sudo bluez-deprecated

COPY start.sh /
RUN chmod +x /start.sh

VOLUME /application/config.yaml

ENTRYPOINT ["/bin/sh", "-c", "/start.sh"]
