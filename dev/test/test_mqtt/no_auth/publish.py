# import paho.mqtt.client as mqtt
# client = mqtt.Client()
# client.connect("127.0.0.1", 1883, 600)
# client.publish('emqtt', payload='Hello, EMQ!', qos=0)

import paho.mqtt.publish as publish
publish.single('emqtt', payload='Hello, EMQ!', qos=0)
