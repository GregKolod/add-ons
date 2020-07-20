ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

#
# First install software packages needed to compile RTL-SDR and rtl_433
#
RUN apk add --no-cache --virtual build-deps alpine-sdk cmake git libusb-dev && \
    mkdir /tmp/src && \
    cd /tmp/src && \
    git clone git://git.osmocom.org/rtl-sdr.git && \
    mkdir /tmp/src/rtl-sdr/build && \
    cd /tmp/src/rtl-sdr/build && \
    cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON -DCMAKE_INSTALL_PREFIX:PATH=/usr/local && \
    make && \
    make install && \
    chmod +s /usr/local/bin/rtl_* && \
    cd /tmp/src/ && \
    git clone https://github.com/merbanan/rtl_433 && \
    cd rtl_433/ && \
    mkdir build && \
    cd build && \
    cmake ../ && \
    make && \
    make install && \
    apk del build-deps && \
    rm -r /tmp/src && \
    apk add --no-cache libusb mosquitto-clients jq
    
    
    
    
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
ENV MQTT_TOPIC rtl_433
ENV PROTOCOL "-R 12"
ENV DISCOVERY_PREFIX homeassistant
ENV DISCOVERY_INTERVAL 600





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
