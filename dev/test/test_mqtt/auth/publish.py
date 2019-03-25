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


g_is_connect = False


def main(args):
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print(f'Connected with result code {rc}')
        global g_is_connect
        g_is_connect = True

    def on_publish(client, userdata, result):
        print(f'data published')
        pass

    # Host header needs to be set, port is not included in signed host header so should not be included here.
    # No idea what it defaults to but whatever that it seems to be wrong.
    client = mqtt_client.Client(client_id=args.client_id, transport=args.transport)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.username_pw_set(username=args.username, password=args.password)
    headers = {
        "Host": args.host,
    }
    client.ws_set_options(path="/mqtt", headers=headers)
    client.connect(args.host, args.port, 60)
    client.loop_start()
    client.max_inflight_messages_set(1)
    client.max_queued_messages_set(1)
    #
    payload = json.dumps({
        'team_uuid': '0xuuid1',
        'body': args.payload,
    })
    for i in range(10):
        if g_is_connect:
            break
        time.sleep(0.1)
    if not g_is_connect:
        print(f'not connect!')
        exit()
    for i in range(1):
        ret = client.publish(topic=args.topic, payload=payload, qos=args.qos)
        print(f'rc: {ret.rc}, mid: {ret.mid}')
        is_published = ret.is_published()
        if not is_published:
            ret.wait_for_publish()
        # print(f'is_published: {ret.is_published()}')
        assert ret.rc == mqtt_client.MQTT_ERR_SUCCESS
    # client.loop_stop()
    client.disconnect()

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
