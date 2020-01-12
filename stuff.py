import time
import os
import paho.mqtt.client as paho
from miio import AirPurifierMiot

mqtt_username = os.environ.get('PURIFIER_MQTT_USERNAME')
mqtt_password = os.environ.get('PURIFIER_MQTT_PASSWORD')
mqtt_prefix = os.environ.get('PURIFIER_MQTT_PREFIX')
mqtt_broker = os.environ.get('PURIFIER_MQTT_BROKER_ADDRESS')
device_token = os.environ.get('PURIFIER_DEVICE_TOKEN')
device_ip = os.environ.get('PURIFIER_DEVICE_ADDRESS')

purifier = AirPurifierMiot(token=device_token, ip=device_ip)

def on_message(client, userdata, message):
    print("received message =", str(message.payload.decode("utf-8")), " on: ", message.topic)
    command = message.topic.rsplit('/',1)[1]
    payload = str(message.payload.decode("utf-8"))
    print(command)
    print (payload)
    if command == 'onoff':
        if payload == 'ON':
            purifier.on()
        elif payload == 'OFF':
            purifier.off()
        else:
            print('unknown')

client = paho.Client("mqttmiot-001")
client.username_pw_set(mqtt_username, mqtt_password)
client.on_message = on_message
client.connect(mqtt_broker)
client.subscribe(mqtt_prefix + "/onoff")  # subscribe
client.loop_start()


while True:
    status = purifier.status()
    print(status)
    client.publish(mqtt_prefix + "/onoffstate", 'ON' if purifier.status().is_on else 'OFF')
    client.publish(mqtt_prefix + "/aqi", purifier.status().aqi)
    client.publish(mqtt_prefix + "/average_aqi", purifier.status().average_aqi)
    client.publish(mqtt_prefix + "/fan_level", purifier.status().fan_level)
    client.publish(mqtt_prefix + "/mode", purifier.status().mode.name)
    time.sleep(1)

client.loop_stop()
client.disconnect()
