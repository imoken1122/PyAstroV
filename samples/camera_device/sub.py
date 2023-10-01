# python3.6

import random

from paho.mqtt import client as mqtt_client
import json
import numpy as np
import base64
import cv2
broker = 'localhost'
port = 1883
topic = "camera/responce"
# generate client ID with pub prefix randomly
client_id = f'test-1'
username = 'emqx'
password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        msg = json.loads(msg.payload.decode())
        print(" ================= Recieved=================")
        print("camera_idx : ", msg["camera_idx"])
        print("cmd: ", msg["cmd_idx"])
        if len(msg["data"]) < 200:
            print(msg["data"])
        else:
            frame = json.loads(msg["data"])["frame"]
            output=base64.b64decode(frame)

            image_array = np.frombuffer(output, np.uint8).reshape(2822,4144)
            print(image_array[:10])
            img = cv2.cvtColor(image_array, cv2.COLOR_BayerGR2BGR)
            print(img.shape)
            cv2.imwrite("test.png",img)
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
