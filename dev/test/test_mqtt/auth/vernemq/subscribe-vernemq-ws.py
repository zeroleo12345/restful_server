import paho.mqtt.client as mqtt
from urllib.parse import urlparse

hostname = "127.0.0.1"
transport, port = 'websockets', 8080
topic = 'emqtt'
qos = 0
payload = 'Hello, EMQ!'
client_id = 'client_id1'
username = 'user1'
password = 'password'
# Host header needs to be set, port is not included in signed host header so should not be included here.
# No idea what it defaults to but whatever that it seems to be wrong.
headers = {
    "Host": hostname,
}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe(topic=topic, qos=qos)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client(client_id=client_id, transport=transport)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=username, password=password)
client.ws_set_options(path="/mqtt", headers=headers)
client.connect(hostname, port, 60)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a manual interface.
client.loop_forever()
