# python 3.6

import random
import time

from paho.mqtt import client as mqtt_client
import json
import paho.mqtt.publish as mqtt_pub
import base64
broker = 'localhost'
port = 1883
topic = "camera/instr"
# generate client ID with pub prefix randomly
client_id = 'async-subscriber'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = []
    t = 0
    while t<13:
        topic = f"camera/instr"
        if t==0:
            msg = {
                "camera_idx":1,
                "cmd_idx" : 6,
                "data" : {"type": "0", "value": "100"}
            }
        elif t==5 : 

            msg = {
                "camera_idx":1,
                "cmd_idx" : 7,
                "data" : {"type": "0", "value": "100"}
            }
        elif t==2:
            msg= {
                #set roi format
                "camera_idx":1,
                 "cmd_idx" : 4,
                 "data":{"startx" : "0",
                         "starty" : "0",
                         "width" : "1000",
                         "height" : "1000",
                         "bin" : "1",
                         "img_type" : "0"
                 }
            }
        elif t==1:
            msg = {
                "camera_idx":1,
                "cmd_idx" : 5,
                "data" : {"ctrl_type": "1","value":"2000000"}
            }
        elif t==2:
            msg = {
                "camera_idx":1,
                "cmd_idx" : 2,
                "data" : {}
            }
        else:
            msg = {
                "camera_idx":0,
                "cmd_idx" : 1,
                "data" : {"type": "0", "value": "100"}
            }

        t += 1
        time.sleep(2)
        msg = json.dumps(msg)
        result = client.publish(topic, msg,2)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")



def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()
