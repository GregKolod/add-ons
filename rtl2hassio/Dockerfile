ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

#
# First install software packages needed to compile RTL-SDR and rtl_433
#
# Copied with minor edits from https://github.com/hertzg/rtl_433_docker/blob/master/images/alpine/build-context/Dockerfile
RUN apk add --no-cache --virtual .buildDeps \
    build-base \
    libusb-dev \
    librtlsdr-dev \
    cmake \
    git

WORKDIR /build

RUN git clone https://github.com/merbanan/rtl_433
WORKDIR ./rtl_433

# Build a specific commit or tag.
ARG rtl433GitRevision=latest
RUN git checkout ${rtl433GitRevision}
WORKDIR ./build
RUN cmake ..
RUN make -j 4

WORKDIR /build/root
WORKDIR /build/rtl_433/build
RUN make DESTDIR=/build/root/ install

FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --no-cache libusb \
    librtlsdr \
    sed
WORKDIR /root
COPY --from=builder /build/root/ /

RUN  apk add --no-cache libusb mosquitto-clients jq
    
    
    
    
WORKDIR /data

RUN apk add --no-cache python3 && \
    apk add --no-cache py-pip

#
# Define environment variables
# 
# Use this variable when creating a container to specify the MQTT broker host.
ENV MQTT_HOST "localhost"
ENV MQTT_PORT 1883
ENV MQTT_USERNAME ""
ENV MQTT_PASSWORD ""
ENV MQTT_RETAIN "True"
ENV MQTT_TOPIC rtl_433
ENV PROTOCOL "-R 12"
ENV DISCOVERY_PREFIX homeassistant
ENV DISCOVERY_INTERVAL 600
ENV BLACK_LIST "Oregon-CM180"





#
# Install Paho-MQTT client
#
RUN pip3 install paho-mqtt

#
# Blacklist kernel modules for RTL devices
#
COPY rtl.blacklist.conf /etc/modprobe.d/rtl.blacklist.conf

#
# Copy scripts, make executable
#
COPY entry.sh rtl_433_mqtt_hass.py /scripts/
RUN chmod +x /scripts/entry.sh
RUN chmod +x /scripts/rtl_433_mqtt_hass.py
#
# Execute entry script
#
ENTRYPOINT [ "/scripts/entry.sh" ]
