import time
import json
import sys
import paho.mqtt.publish as paho_mqtt_publish
import paho.mqtt.client as paho_mqtt_client


def help():
    print("""
VerneMQ:
  websocket:
      python ./{0} -host 127.0.0.1 -port 8080 -transport websockets -client_id subscriber -username subscriber -password password -topic emqtt -qos 0 -payload HelloWorld
      
  tcp:
      python ./{0} -host 127.0.0.1 -port 1883 -transport tcp -client_id subscriber -username subscriber -password password -topic emqtt -qos 0 -payload HelloWorld
      
Emqx:
  websocket:
      python ./{0} -host 127.0.0.1 -port 8083 -transport websockets -client_id '' -username subscriber -password password -topic emqtt -qos 0 -payload HelloWorld
      
  tcp:
      python ./{0} -host 127.0.0.1 -port 1883 -transport tcp -client_id '' -username subscriber -password password -topic emqtt -qos 0 -payload HelloWorld
    """.format(__file__))


def init_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', metavar='<host>', type=str, dest='host')
    parser.add_argument('-transport', choices=['tcp', 'websockets'], metavar='<transport>', type=str, dest='transport')
    parser.add_argument('-port', metavar='<port>', type=int, dest='port')
    parser.add_argument('-topic', metavar='<topic>', type=str, dest='topic')
    parser.add_argument('-qos', metavar='<qos>', type=int, dest='qos')
    parser.add_argument('-payload', metavar='<payload>', type=str, dest='payload')
    parser.add_argument('-client_id', metavar='<client_id>', type=str, dest='client_id')
    parser.add_argument('-username', metavar='<username>', type=str, dest='username')
    parser.add_argument('-password', metavar='<password>', type=str, dest='password')
    # parser.print_help = help
    return parser.parse_args()


class Mqtt(object):
    is_connect = False
    _client = None
    PUBLISH_MODE = 1
    SUBSCRIBE_MODE = 2

    def __init__(self, host, port, username, password, client_id, transport):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.transport = transport

    def connect(self):
        # Host header needs to be set, port is not included in signed host header so should not be included here.
        # No idea what it defaults to but whatever that it seems to be wrong.
        self._client = paho_mqtt_client.Client(client_id=self.client_id, clean_session=True, transport=self.transport)
        #
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect
        self._client.on_publish = self.on_publish
        self._client.on_message = self.on_message
        #
        self._client.username_pw_set(username=self.username, password=self.password)
        headers = {
            "Host": self.host,
        }
        self._client.ws_set_options(path="/mqtt", headers=headers)
        self._client.connect(self.host, self.port, keepalive=60)
        # self._client.max_inflight_messages_set(1)
        # self._client.max_queued_messages_set(1)

    def loop(self, mode):
        if mode == Mqtt.PUBLISH_MODE:
            self._client.loop_start()
        elif mode == Mqtt.SUBSCRIBE_MODE:
            self._client.loop_forever()
        #
        for i in range(30):
            if self.is_connect:
                break
            time.sleep(0.1)
        if not self.is_connect:
            print(f'not connect!')
            exit()

    def on_connect(self, client, userdata, flags, rc):
        # The callback for when the client receives a CONNACK response from the server.
        print(f'mqtt client connected, result code {rc}')
        self.is_connect = True

    def on_publish(self, client, userdata, result):
        print(f'data published, client: {client}, userdata: {userdata}, result: {result}')

    def on_message(self, client, userdata, msg):
        # The callback for when a PUBLISH message is received from the server.
        print(f'topic: {msg.topic}, payload: {msg.payload}')
        deserializer = json.loads(msg.payload)
        print(f'deserializer: {deserializer}, type: {type(deserializer)}')

    def on_disconnect(self, client, userdata, rc):
        print(f'mqtt client disconnect, client: {client}, userdata: {userdata}, rc: {rc}')
        self._client.loop_stop()
        self._client.disconnect()
        self.is_connect = False

    def publish(self, topic, payload, qos=0):
        ret = self._client.publish(topic=topic, payload=payload, qos=qos)
        print(f'rc: {ret.rc}, mid: {ret.mid}')
        # ret.wait_for_publish()
        # print(f'is_published: {ret.is_published()}')
        # assert ret.rc == paho_mqtt_client.MQTT_ERR_SUCCESS

    def subscribe(self, topic, qos=0):
        self._client.subscribe(topic=topic, qos=qos)


def main(args):
    mqtt = Mqtt(args.host, args.port, args.username, args.password, args.client_id, args.transport)
    mqtt.connect()
    mqtt.subscribe(topic=args.topic, qos=args.qos)
    mqtt.loop(mode=Mqtt.SUBSCRIBE_MODE)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        help(), sys.exit()
    args = init_args()
    main(args)
