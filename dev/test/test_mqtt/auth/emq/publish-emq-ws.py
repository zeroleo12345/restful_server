import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

hostname = "127.0.0.1"
transport, port = 'websockets', 8083
topic = 'emqtt'
qos = 0
payload = 'Hello, EMQ!'
client_id = ''
username = 'user2'
password = 'password'
headers = {
    "Host": hostname,
}


# 方法1(推荐):
client = mqtt.Client(client_id=client_id, transport=transport)
client.username_pw_set(username=username, password=password)
# client.ws_set_options(path="/mqtt", headers=headers)
client.connect(hostname, port, 60)
client.publish(topic=topic, payload=payload, qos=qos)


# 方法2:
# auth = {'username': username, 'password': password}
# publish.single(
#     topic, payload=payload, qos=0, hostname=hostname,
#     port=port, client_id=client_id, auth=auth,
#     transport=transport
# )

