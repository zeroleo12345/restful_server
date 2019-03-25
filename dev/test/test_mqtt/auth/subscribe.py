import json
import sys
import paho.mqtt.client as mqtt


def help():
    print("""
VerneMQ:
  websocket:
      python ./{0} -host 127.0.0.1 -port 8080 -transport websockets -client_id client_subscriber -username subscriber -password password -topic emqtt -qos 0 -payload HelloWorld
      
  tcp:
      python ./{0} -host 127.0.0.1 -port 1883 -transport tcp -client_id client_subscriber -username subscriber -password password -topic emqtt -qos 0 -payload HelloWorld
      
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


def main(args):
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print(f'Connected with result code {rc}')
        # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        # client.subscribe("$SYS/#")
        client.subscribe(topic=args.topic, qos=args.qos)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        print(f'topic: {msg.topic}, payload: {msg.payload}')
        deserializer = json.loads(msg.payload)
        print(f'deserializer: {deserializer}, type: {type(deserializer)}')

    # Host header needs to be set, port is not included in signed host header so should not be included here.
    # No idea what it defaults to but whatever that it seems to be wrong.
    client = mqtt.Client(client_id=args.client_id, clean_session=True, transport=args.transport)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=args.username, password=args.password)
    headers = {
        "Host": args.host,
    }
    client.ws_set_options(path="/mqtt", headers=headers)
    client.connect(args.host, args.port, 60)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a manual interface.
    client.loop_forever()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        help(), sys.exit()
    args = init_args()
    main(args)
