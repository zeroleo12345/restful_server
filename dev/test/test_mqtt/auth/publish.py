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


def main(args):
    """
    # 方法1(不推荐, 需要pdb停顿才能发送出去, 暂未定位到原因):
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print(f'Connected with result code {rc}')
        # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        # client.subscribe("$SYS/#")
        client.subscribe(topic=args.topic, qos=args.qos)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        print(f'topic: {msg.topic}, payload: {msg.payload}')

    # Host header needs to be set, port is not included in signed host header so should not be included here.
    # No idea what it defaults to but whatever that it seems to be wrong.
    headers = {
        "Host": args.host,
    }
    client = mqtt_client.Client(client_id=args.client_id, transport=args.transport)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=args.username, password=args.password)
    client.ws_set_options(path="/mqtt", headers=headers)
    client.connect(args.host, args.port, 60)
    #
    rc, mid = client.publish(topic=args.topic, payload=args.payload, qos=args.qos)
    print(f'rc: {rc}, mid: {mid}')
    assert rc == mqtt_client.MQTT_ERR_SUCCESS
    client.loop_forever()
    """

    # 方法2:
    auth = {'username': args.username, 'password': args.password}
    mqtt_publish.single(
        args.topic, payload=args.payload, qos=args.qos, hostname=args.host,
        port=args.port, client_id=args.client_id, auth=auth,
        transport=args.transport
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        help(), sys.exit()
    args = init_args()
    main(args)
