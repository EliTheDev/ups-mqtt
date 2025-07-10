import os
import subprocess
import time
from time import sleep, localtime, strftime
import datetime
from configparser import ConfigParser
import shutil
import paho.mqtt.client as mqtt

if not os.path.exists('conf/config.ini'):
    shutil.copy('config.ini', 'conf/config.ini')

# Load configuration file
config_dir = 'conf/config.ini'
config = ConfigParser(delimiters=('=', ), inline_comment_prefixes=('#'))
config.optionxform = str
config.read(config_dir)

cache = {}
model_name = "model"
base_topic = config['MQTT'].get('base_topic', 'ups')

ups_host = config['UPS'].get('hostname', 'localhost')
location = config['UPS'].get('location', 'north')
mqtt_host = config['MQTT'].get('hostname', 'localhost')
mqtt_port = config['MQTT'].getint('port', 1883)
mqtt_user = config['MQTT'].get('username', None)
mqtt_password = config['MQTT'].get('password', None)
interval = config['General'].getint('interval', 60)


# MQTT Client

client = mqtt.Client()
if mqtt_user and mqtt_password:
    client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_host, mqtt_port, keepalive=60)
client.loop_start()

def process():
    global cache
    global model_name
    ups = subprocess.run(["upsc", ups_host], stdout=subprocess.PIPE)
    lines = ups.stdout.decode('utf-8').split('\n')

    model_name = next((line.split(':', 1)[1].strip() for line in lines if line.startswith('ups.model:')), None).replace(' ', '_').replace('.','_')

    for line in lines:
        if not line.strip() or ':' not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().replace('.','_')
        value = value.strip()

        if cache.get(key) != value:
            topic = f"{base_topic}/{location}/ups/{model_name}/{key}"
            client.publish(topic, value, qos=1, retain=True)
            print(f"Published to {topic}: {value}")
            cache[key] = value

# sleep(5)
while True:
    process()
    sleep(interval)
