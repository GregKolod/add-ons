#!/usr/bin/env python3
# coding=utf-8

"""MQTT Home Assistant auto discovery for rtl_433 events."""

# It is strongly recommended to run rtl_433 with "-C si" and "-M newmodel".

# Needs Paho-MQTT https://pypi.python.org/pypi/paho-mqtt

# Option: PEP 3143 - Standard daemon process library
# (use Python 3.x or pip install python-daemon)
# import daemon

from __future__ import print_function, with_statement

import json
import os
import time
import paho.mqtt.client as mqtt
import argparse
import logging
import re


MQTT_HOST = os.environ['MQTT_HOST']
MQTT_PORT = os.environ['MQTT_PORT']
MQTT_USERNAME = os.environ['MQTT_USERNAME']
MQTT_PASSWORD = os.environ['MQTT_PASSWORD']
MQTT_TOPIC = os.environ['MQTT_TOPIC']
DISCOVERY_PREFIX = os.environ['DISCOVERY_PREFIX']
DISCOVERY_INTERVAL = os.environ['DISCOVERY_INTERVAL']

BLACK_LIST = os.environ['BLACK_LIST']


# Convert number environment variables to int
MQTT_PORT = int(MQTT_PORT)
DISCOVERY_INTERVAL = int(DISCOVERY_INTERVAL)

discovery_timeouts = {}

mappings = {
    "temperature_C": {
        "device_type": "sensor",
        "object_suffix": "T",
        "config": {
            "device_class": "temperature",
            "name": "Temperature",
            "unit_of_measurement": "°C",
            "value_template": "{{ value|float|round(1) }}",
            "state_class": "measurement"
        }
    },
    "temperature_1_C": {
        "device_type": "sensor",
        "object_suffix": "T1",
        "config": {
            "device_class": "temperature",
            "name": "Temperature 1",
            "unit_of_measurement": "°C",
            "value_template": "{{ value|float|round(1) }}",
            "state_class": "measurement"
        }
    },
    "temperature_2_C": {
        "device_type": "sensor",
        "object_suffix": "T2",
        "config": {
            "device_class": "temperature",
            "name": "Temperature 2",
            "unit_of_measurement": "°C",
            "value_template": "{{ value|float|round(1) }}",
            "state_class": "measurement"
        }
    },
    "temperature_F": {
        "device_type": "sensor",
        "object_suffix": "F",
        "config": {
            "device_class": "temperature",
            "name": "Temperature",
            "unit_of_measurement": "°F",
            "value_template": "{{ value|float|round(1) }}",
            "state_class": "measurement"
        }
    },

    # This diagnostic sensor is useful to see when a device last sent a value,
    # even if the value didn't change.
    # https://community.home-assistant.io/t/send-metrics-to-influxdb-at-regular-intervals/9096
    # https://github.com/home-assistant/frontend/discussions/13687
    "time": {
        "device_type": "sensor",
        "object_suffix": "UTC",
        "config": {
            "device_class": "timestamp",
            "name": "Timestamp",
            "entity_category": "diagnostic",
            "enabled_by_default": False,
            "icon": "mdi:clock-in"
        }
    },

    "battery_ok": {
        "device_type": "sensor",
        "object_suffix": "B",
        "config": {
            "device_class": "battery",
            "name": "Battery",
            "unit_of_measurement": "%",
            "value_template": "{{ float(value) * 99 + 1 }}",
            "state_class": "measurement",
            "entity_category": "diagnostic"
        }
    },

    "humidity": {
        "device_type": "sensor",
        "object_suffix": "H",
        "config": {
            "device_class": "humidity",
            "name": "Humidity",
            "unit_of_measurement": "%",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },
    "humidity_1": {
        "device_type": "sensor",
        "object_suffix": "H1",
        "config": {
            "device_class": "humidity",
            "name": "Humidity 1",
            "unit_of_measurement": "%",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },
    "humidity_2": {
        "device_type": "sensor",
        "object_suffix": "H2",
        "config": {
            "device_class": "humidity",
            "name": "Humidity 2",
            "unit_of_measurement": "%",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "moisture": {
        "device_type": "sensor",
        "object_suffix": "H",
        "config": {
            "device_class": "humidity",
            "name": "Moisture",
            "unit_of_measurement": "%",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "pressure_hPa": {
        "device_type": "sensor",
        "object_suffix": "P",
        "config": {
            "device_class": "pressure",
            "name": "Pressure",
            "unit_of_measurement": "hPa",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "pressure_kPa": {
        "device_type": "sensor",
        "object_suffix": "P",
        "config": {
            "device_class": "pressure",
            "name": "Pressure",
            "unit_of_measurement": "kPa",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "wind_speed_km_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "wind_avg_km_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "wind_avg_mi_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind Speed",
            "unit_of_measurement": "mi/h",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "wind_avg_m_s": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind Average",
            "unit_of_measurement": "km/h",
            "value_template": "{{ (float(value|float) * 3.6) | round(2) }}",
            "state_class": "measurement"
        }
    },

    "wind_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value|float) * 3.6 }}",
            "state_class": "measurement"
        }
    },

    "gust_speed_km_h": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "wind_speed",
            "name": "Gust Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "wind_max_km_h": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind max speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "wind_max_m_s": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind max",
            "unit_of_measurement": "km/h",
            "value_template": "{{ (float(value|float) * 3.6) | round(2) }}",
            "state_class": "measurement"
        }
    },

    "gust_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "wind_speed",
            "name": "Gust Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value|float) * 3.6 }}",
            "state_class": "measurement"
        }
    },

    "wind_dir_deg": {
        "device_type": "sensor",
        "object_suffix": "WD",
        "config": {
            "name": "Wind Direction",
            "unit_of_measurement": "°",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "rain_mm": {
        "device_type": "sensor",
        "object_suffix": "RT",
        "config": {
            "device_class": "precipitation",
            "name": "Rain Total",
            "unit_of_measurement": "mm",
            "value_template": "{{ value|float|round(2) }}",
            "state_class": "total_increasing"
        }
    },

    "rain_rate_mm_h": {
        "device_type": "sensor",
        "object_suffix": "RR",
        "config": {
            "device_class": "precipitation_intensity",
            "name": "Rain Rate",
            "unit_of_measurement": "mm/h",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "rain_in": {
        "device_type": "sensor",
        "object_suffix": "RT",
        "config": {
            "device_class": "precipitation",
            "name": "Rain Total",
            "unit_of_measurement": "mm",
            "value_template": "{{ (float(value|float) * 25.4) | round(2) }}",
            "state_class": "total_increasing"
        }
    },

    "rain_rate_in_h": {
        "device_type": "sensor",
        "object_suffix": "RR",
        "config": {
            "device_class": "precipitation_intensity",
            "name": "Rain Rate",
            "unit_of_measurement": "mm/h",
            "value_template": "{{ (float(value|float) * 25.4) | round(2) }}",
            "state_class": "measurement"
        }
    },

    "tamper": {
        "device_type": "binary_sensor",
        "object_suffix": "tamper",
        "config": {
            "device_class": "safety",
            "force_update": "true",
            "payload_on": "1",
            "payload_off": "0",
            "entity_category": "diagnostic"
        }
    },

    "alarm": {
        "device_type": "binary_sensor",
        "object_suffix": "alarm",
        "config": {
            "device_class": "safety",
            "force_update": "true",
            "payload_on": "1",
            "payload_off": "0",
            "entity_category": "diagnostic"
        }
    },

    "rssi": {
        "device_type": "sensor",
        "object_suffix": "rssi",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}",
            "state_class": "measurement",
            "entity_category": "diagnostic"
        }
    },

    "snr": {
        "device_type": "sensor",
        "object_suffix": "snr",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}",
            "state_class": "measurement",
            "entity_category": "diagnostic"
        }
    },

    "noise": {
        "device_type": "sensor",
        "object_suffix": "noise",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}",
            "state_class": "measurement",
            "entity_category": "diagnostic"
        }
    },

    "depth_cm": {
        "device_type": "sensor",
        "object_suffix": "D",
        "config": {
            "name": "Depth",
            "unit_of_measurement": "cm",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "power_W": {
        "device_type": "sensor",
        "object_suffix": "watts",
        "config": {
            "device_class": "power",
            "name": "Power",
            "unit_of_measurement": "W",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },
  
    "energy_kWh": {
        "device_type": "sensor",
        "object_suffix": "kwh",
        "config": {
            "device_class": "power",
            "name": "Energy",
            "unit_of_measurement": "kWh",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },
  
    "current_A": {
        "device_type": "sensor",
        "object_suffix": "A",
        "config": {
            "device_class": "power",
            "name": "Current",
            "unit_of_measurement": "A",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },
  
    "voltage_V": {
        "device_type": "sensor",
        "object_suffix": "V",
        "config": {
            "device_class": "power",
            "name": "Voltage",
            "unit_of_measurement": "V",
            "value_template": "{{ value|float }}",
            "state_class": "measurement"
        }
    },

    "light_lux": {
        "device_type": "sensor",
        "object_suffix": "lux",
        "config": {
            "name": "Outside Luminance",
            "unit_of_measurement": "lux",
            "value_template": "{{ value|int }}",
            "state_class": "measurement"
        }
    },
    "lux": {
        "device_type": "sensor",
        "object_suffix": "lux",
        "config": {
            "name": "Outside Luminance",
            "unit_of_measurement": "lux",
            "value_template": "{{ value|int }}",
            "state_class": "measurement"
        }
    },

    "uv": {
        "device_type": "sensor",
        "object_suffix": "uv",
        "config": {
            "name": "UV Index",
            "unit_of_measurement": "UV Index",
            "value_template": "{{ value|int }}",
            "state_class": "measurement"
        }
    },
    "uvi": {
        "device_type": "sensor",
        "object_suffix": "uvi",
        "config": {
            "name": "UV Index",
            "unit_of_measurement": "UV Index",
            "value_template": "{{ value|int }}",
            "state_class": "measurement"
        }
    },

    "storm_dist": {
        "device_type": "sensor",
        "object_suffix": "stdist",
        "config": {
            "name": "Lightning Distance",
            "unit_of_measurement": "mi",
            "value_template": "{{ value|int }}",
            "state_class": "measurement"
        }
    },

    "strike_distance": {
        "device_type": "sensor",
        "object_suffix": "stdist",
        "config": {
            "name": "Lightning Distance",
            "unit_of_measurement": "mi",
            "value_template": "{{ value|int }}",
            "state_class": "measurement"
        }
    },

    "strike_count": {
        "device_type": "sensor",
        "object_suffix": "strcnt",
        "config": {
            "name": "Lightning Strike Count",
            "value_template": "{{ value|int }}",
            "state_class": "total_increasing"
        }
    },

    "consumption_data": {
        "device_type": "sensor",
        "object_suffix": "consumption",
        "config": {
            "name": "SCM Consumption Value",
            "value_template": "{{ value|int }}",
            "state_class": "total_increasing",
        }
    },
  
    "consumption": {
        "device_type": "sensor",
        "object_suffix": "consumption",
        "config": {
            "name": "SCMplus Consumption Value",
            "value_template": "{{ value|int }}",
            "state_class": "total_increasing",
        }
    },

    "channel": {
        "device_type": "device_automation",
        "object_suffix": "CH",
        "config": {
           "automation_type": "trigger",
           "type": "button_short_release",
           "subtype": "button_1",
        }
    },

    "button": {
        "device_type": "device_automation",
        "object_suffix": "BTN",
        "config": {
           "automation_type": "trigger",
           "type": "button_short_release",
           "subtype": "button_1",
        }
    },

}
def mqtt_connect(client, userdata, flags, rc):
    """Callback for MQTT connects."""
    print("MQTT connected: " + mqtt.connack_string(rc))
    client.publish("/".join([MQTT_TOPIC, "status"]), payload="online", qos=0, retain=True)
    if rc != 0:
        print("Could not connect. Error: " + str(rc))
    else:
        client.subscribe("/".join([MQTT_TOPIC, "events"]))


def mqtt_disconnect(client, userdata, rc):
    """Callback for MQTT disconnects."""
    print("MQTT disconnected: " + mqtt.connack_string(rc))


def mqtt_message(client, userdata, msg):
    """Callback for MQTT message PUBLISH."""
    try:
        # Decode JSON payload
        data = json.loads(msg.payload.decode())
        # print("DATA  ", data)
        bridge_event_to_hass(client, msg.topic, data)

    except json.decoder.JSONDecodeError:
        print("JSON decode error: " + msg.payload.decode())
        return


def sanitize(text):
    """Sanitize a name for Graphite/MQTT use."""
    return (text
            .replace(" ", "_")
            .replace("/", "_")
            .replace(".", "_")
            .replace("&", ""))

def rtl_433_device_info(data, topic_prefix):
    """Return rtl_433 device topic to subscribe to for a data element, based on the
    rtl_433 device topic argument, as well as the device identifier"""

    path_elements = []
    id_elements = []
    last_match_end = 0
    # The default for args.device_topic_suffix is the same topic structure
    # as set by default in rtl433 config
    for match in re.finditer(TOPIC_PARSE_RE, args.device_topic_suffix):
        path_elements.append(args.device_topic_suffix[last_match_end:match.start()])
        key = match.group(2)
        if key in data:
            # If we have this key, prepend a slash if needed
            if match.group(1):
                path_elements.append('/')
            element = sanitize(str(data[key]))
            path_elements.append(element)
            id_elements.append(element)
        elif match.group(3):
            path_elements.append(match.group(3))
        last_match_end = match.end()

    path = ''.join(list(filter(lambda item: item, path_elements)))
    id = '-'.join(id_elements)
    return (f"{topic_prefix}/{path}", id)
    
def publish_config(mqttc, topic, model, object_id, mapping, key=None):
    """Publish Home Assistant auto discovery data."""
    global discovery_timeouts

    device_type = mapping["device_type"]
    object_suffix = mapping["object_suffix"]
    object_name = "-".join([object_id, object_suffix])

    path = "/".join([args.discovery_prefix, device_type, object_id, object_name, "config"])

    # check timeout
    now = time.time()
    if path in discovery_timeouts:
        if discovery_timeouts[path] > now:
            logging.debug("Discovery timeout in the future for: " + path)
            return False

    discovery_timeouts[path] = now + args.discovery_interval

    config = mapping["config"].copy()

    # Device Automation configuration is in a different structure compared to
    # all other mqtt discovery types.
    # https://www.home-assistant.io/integrations/device_trigger.mqtt/
    if device_type == 'device_automation':
        config["topic"] = topic
        config["platform"] = 'mqtt'
    else:
        readable_name = mapping["config"]["name"] if "name" in mapping["config"] else key
        config["state_topic"] = topic
        config["unique_id"] = object_name
        config["name"] = readable_name
    config["device"] = { "identifiers": [object_id], "name": object_id, "model": model, "manufacturer": "rtl_433" }

    if args.force_update:
        config["force_update"] = "true"

    if args.expire_after:
        config["expire_after"] = args.expire_after

    logging.debug(path + ":" + json.dumps(config))

    mqttc.publish(path, json.dumps(config), retain=args.retain)

    return True

def bridge_event_to_hass(mqttc, topic_prefix, data):
    """Translate some rtl_433 sensor data to Home Assistant auto discovery."""

    if "model" not in data:
        # not a device event
        logging.debug("Model is not defined. Not sending event to Home Assistant.")
        return
    
    if data["model"] in BLACK_LIST:
        # filtruj niechciane modele w protokole
        return        
        

    model = sanitize(data["model"])

    skipped_keys = []
    published_keys = []

    base_topic, device_id = rtl_433_device_info(data, topic_prefix)
    if not device_id:
        # no unique device identifier
        logging.warning("No suitable identifier found for model: ", model)
        return

    if args.ids and "id" in data and data.get("id") not in args.ids:
        # not in the safe list
        logging.debug("Device (%s) is not in the desired list of device ids: [%s]" % (data["id"], ids))
        return

    # detect known attributes
    for key in data.keys():
        if key in mappings:
            # topic = "/".join([topicprefix,"devices",model,instance,key])
            topic = "/".join([base_topic, key])
            if publish_config(mqttc, topic, model, device_id, mappings[key], key):
                published_keys.append(key)
        else:
            if key not in SKIP_KEYS:
                skipped_keys.append(key)

    if "secret_knock" in data.keys():
        for m in secret_knock_mappings:
            topic = "/".join([base_topic, "secret_knock"])
            if publish_config(mqttc, topic, model, device_id, m, "secret_knock"):
                published_keys.append("secret_knock")

    if published_keys:
        logging.info("Published %s: %s" % (device_id, ", ".join(published_keys)))

        if skipped_keys:
            logging.info("Skipped %s: %s" % (device_id, ", ".join(skipped_keys)))



def rtl_433_bridge():
    """Run a MQTT Home Assistant auto discovery bridge for rtl_433."""
    mqttc = mqtt.Client()
    mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqttc.on_connect = mqtt_connect
    mqttc.on_disconnect = mqtt_disconnect
    mqttc.on_message = mqtt_message

    mqttc.will_set("/".join([MQTT_TOPIC, "status"]), payload="offline", qos=0, retain=True)
    mqttc.connect_async(MQTT_HOST, MQTT_PORT, 60)
    mqttc.loop_start()

    while True:
        time.sleep(1)


def run():
    """Run main or daemon."""
    # with daemon.DaemonContext(files_preserve=[sock]):
    #  detach_process=True
    #  uid
    #  gid
    #  working_directory
    
    rtl_433_bridge()


if __name__ == "__main__":

    run()
