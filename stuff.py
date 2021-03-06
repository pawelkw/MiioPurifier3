import time
import os
import paho.mqtt.client as paho
from miio import AirPurifierMiot
from miio.airpurifier_miot import OperationMode

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
    elif command == 'fan_level_cmd':
        purifier.set_fan_level(int(payload))
    elif command == 'night_cmd':
        if payload == 'ON':
            purifier.set_mode(OperationMode.Silent)
    elif command == 'favorite_cmd':
        if payload == 'ON':
            purifier.set_mode(OperationMode.Favorite)
    elif command == 'auto_cmd':
        if payload == 'ON':
            purifier.set_mode(OperationMode.Auto)

client = paho.Client("mqttmiot-001")
client.username_pw_set(mqtt_username, mqtt_password)
client.on_message = on_message
client.connect(mqtt_broker)
client.subscribe(mqtt_prefix + "/onoff")  # subscribe)
client.subscribe(mqtt_prefix + "/fan_level_cmd")  # subscribe
client.subscribe(mqtt_prefix + "/night_cmd")  # subscribe
client.subscribe(mqtt_prefix + "/favorite_cmd")  # subscribe
client.subscribe(mqtt_prefix + "/auto_cmd")  # subscribe
client.loop_start()


while True:
    status = purifier.status()
    print(status)
    client.publish(mqtt_prefix + "/onoffstate", 'ON' if purifier.status().is_on else 'OFF')
    client.publish(mqtt_prefix + "/aqi", purifier.status().aqi)
    client.publish(mqtt_prefix + "/average_aqi", purifier.status().average_aqi)
    client.publish(mqtt_prefix + "/fan_level", purifier.status().fan_level)
    client.publish(mqtt_prefix + "/mode", purifier.status().mode.name)
    client.publish(mqtt_prefix + "/night", 'ON' if purifier.status().mode == OperationMode.Silent else 'OFF')
    client.publish(mqtt_prefix + "/favorite", 'ON' if purifier.status().mode == OperationMode.Favorite else 'OFF')
    client.publish(mqtt_prefix + "/auto", 'ON' if purifier.status().mode == OperationMode.Auto else 'OFF')
    client.publish(mqtt_prefix + "/fan", 'ON' if purifier.status().mode == OperationMode.Fan else 'OFF')
    time.sleep(1)

client.loop_stop()
client.disconnect()
