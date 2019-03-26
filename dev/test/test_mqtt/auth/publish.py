import time
import json
import sys
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client


def help():
    print("""
VerneMQ:
  websocket:
      python ./{0} -host 127.0.0.1 -port 8080 -transport websockets -client_id client_publisher -username publisher -password password -topic emqtt -qos 0 -payload HelloWorld
      
  tcp:
      python ./{0} -host 127.0.0.1 -port 1883 -transport tcp -client_id client_publisher -username publisher -password password -topic emqtt -qos 0 -payload HelloWorld
      
Emqx:
  websocket:
      python ./{0} -host 127.0.0.1 -port 8083 -transport websockets -client_id '' -username publisher -password password -topic emqtt -qos 0 -payload HelloWorld
      
  tcp:
      python ./{0} -host 127.0.0.1 -port 1883 -transport tcp -client_id '' -username publisher -password password -topic emqtt -qos 0 -payload HelloWorld
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

    def on_connect(self, client, userdata, flags, rc):
        # The callback for when the client receives a CONNACK response from the server.
        print(f'mqtt client connected, result code {rc}')
        self.is_connect = True

    def on_publish(self, client, userdata, result):
        print('data published')

    def on_disconnect(self, client, userdata, rc):
        print('mqtt client disconnect')
        self.disconnect()
        self.connect()

    def __init__(self, host, port, username, password, client_id, transport):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.transport = transport
        self.connect()

    def connect(self):
        # Host header needs to be set, port is not included in signed host header so should not be included here.
        # No idea what it defaults to but whatever that it seems to be wrong.
        self._client = mqtt_client.Client(client_id=self.client_id, transport=self.transport)
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect
        self._client.on_publish = self.on_publish
        self._client.username_pw_set(username=self.username, password=self.password)
        headers = {
            "Host": self.host,
        }
        self._client.ws_set_options(path="/mqtt", headers=headers)
        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_start()
        # self._client.max_inflight_messages_set(1)
        # self._client.max_queued_messages_set(1)
        for i in range(30):
            if self.is_connect:
                break
            time.sleep(0.1)
        if not self.is_connect:
            print(f'not connect!')
            exit()

    def publish(self, topic, payload, qos=0):
        payload = json.dumps({
            'team_uuid': '0xuuid1',
            'body': payload,
        })
        ret = self._client.publish(topic=topic, payload=payload, qos=qos)
        # print(f'rc: {ret.rc}, mid: {ret.mid}')
        # ret.wait_for_publish()
        # print(f'is_published: {ret.is_published()}')
        # assert ret.rc == mqtt_client.MQTT_ERR_SUCCESS

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()


def main(args):
    # """
    mqtt = Mqtt(args.host, args.port, args.username, args.password, args.client_id, args.transport)
    for i in range(3):
        mqtt.publish(topic=args.topic, payload=args.payload, qos=args.qos)
        time.sleep(70)
    """
    # 方法2:
    auth = {'username': args.username, 'password': args.password}
    payload = json.dumps({
        'team_uuid': '0xuuid1',
        'body': args.payload,
    })
    mqtt_publish.single(
        args.topic, payload=payload, qos=args.qos, hostname=args.host,
        port=args.port, client_id=args.client_id, auth=auth,
        transport=args.transport
    )
    """


if __name__ == "__main__":
    if len(sys.argv) == 1:
        help(), sys.exit()
    args = init_args()
    main(args)
