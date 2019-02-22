""" Reference:
        https://media.readthedocs.org/pdf/pika/latest/pika.pdf
        http://www.01happy.com/python-pika-rabbitmq-summary/
        心跳包每半个超时时间发送一次, 丢失了两个心跳包, 连接被认为不可抵达, 不同的客户端有不同的提,
        但tcp连接都会被关闭. 当客户端检测到RMQ节点不可抵达(根据心跳判定), 它需要重新连接.
        心跳机制可以被禁用: 设定超时间隔为0
a) Exclusive:排他队列,如果一个队列被声明为排他队列,该队列仅对首次声明它的连接可见,并在连接断开时自动删除. 这里需要注意三点:
    1. 排他队列是基于连接可见的,同一连接的不同信道是可以同时访问同一个连接创建的排他队列的.
    2. 如果一个连接已经声明了一个排他队列,其他连接是不允许建立同名的排他队列的,这个与普通队列不同.
    3. 即使该队列是持久化的,一旦连接关闭或者客户端退出,该排他队列都会被自动删除的.
这种队列适用于只限于一个客户端发送读取消息的应用场景.
b) Auto-delete:自动删除,如果该队列没有任何订阅的消费者的话,该队列会被自动删除.这种队列适用于临时队列.
c) Durable:持久化,这个会在后面作为专门一个章节讨论.
d) 如果用户仅想查询某一个队列是否已存在，不想建立该队列，仍然可以调用queue.declare, 
   只需将参数passive设为true,传给queue.declare,如果该队列已存在,则会返回true;如果不存在,则会返回Error,但是不会创建新的队列.
"""
import sys
import os
import time
import pika


# 1. 队列
def test_queue_send(connection, channel, persistent_properties):
    queue_name = 'queue'
    channel.queue_declare(queue=queue_name, durable=False) # 声明创建队列
    channel.basic_publish( exchange='', routing_key=queue_name, body='Hello World!', properties=persistent_properties )
    print(" [x] Sent 'Hello World!'")
    connection.close()


def test_queue_get(connection, channel, persistent_properties):
    queue_name = 'queue'
    channel.queue_declare(queue=queue_name, durable=False) # 声明创建队列

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % (body,))
    channel.basic_consume(callback, queue=queue_name, no_ack=True) # 读取queue消息
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    connection.close()


# Recv msg: (<Basic.GetOk(['delivery_tag=2', 'exchange=', 'message_count=0', 'redelivered=False', 'routing_key=queue'])>, <BasicProperties(['delivery_mode=2'])>, 'Hello World!')
# Recv msg: (None, None, None)
def test_queue_get_nonblock(connection, channel, persistent_properties):
    queue_name = 'queue'
    channel.queue_declare(queue=queue_name, durable=False) # 声明创建队列
    # 定义交换机
    channel.exchange_declare(exchange='messages_fanout', exchange_type='fanout', passive=False, durable=False, auto_delete=False) # 同时也关注广播!
    # channel.exchange_declare(exchange='messages_fanout', exchange_type='fanout') # 同时也关注广播!
    # 绑定到交换机上
    # arguments={ "x-message-ttl":10 }
    channel.queue_bind( exchange='messages_fanout', queue=queue_name ) # 同时也关注广播!
    i = 0
    while True:
        msg = channel.basic_get(queue=queue_name, no_ack=True) # 读取queue消息
        print('Recv msg:{}'.format(msg))
        time.sleep(5)
        i+=1
        if i == 3: channel.queue_unbind(queue=queue_name, exchange='messages_fanout')
    connection.close()


# 2. 广播
def test_exchange_fanout_send(connection, channel, persistent_properties):
    # 定义交换机
    target_exchange = 'messages_fanout3'
    channel.exchange_declare(exchange=target_exchange, exchange_type='fanout', passive=False, durable=False, auto_delete=False)
    # channel.exchange_declare(exchange='messages_fanout', exchange_type='fanout')
    # 将消息发送到交换机
    expiration = 3000 # 单位: 毫秒
    if expiration: properties = pika.BasicProperties(expiration=str(expiration))
    else: properties = pika.BasicProperties()
    channel.basic_publish( exchange=target_exchange, routing_key='', body='Hello World!', properties=properties )
    print(" [x] Sent Hello World!, expiration:{}".format(expiration))
    connection.close()


def test_exchange_fanout_get(connection, channel, persistent_properties):
    # 定义交换机
    channel.exchange_declare(exchange='messages_fanout1', exchange_type='fanout', passive=False, durable=False, auto_delete=False)
    channel.exchange_declare(exchange='messages_fanout2', exchange_type='fanout', passive=False, durable=False, auto_delete=False)
    channel.exchange_declare(exchange='messages_fanout3', exchange_type='fanout', passive=False, durable=False, auto_delete=False)

    # 选择1. 生成临时队列(不会触发持久化)
    # result = channel.queue_declare(exclusive=True); queue_name = result.method.queue
    # 选择2. fanout模式下多个消费者不能使用同一个队列
    queue_name = 'fanout_queue'; channel.queue_declare(queue=queue_name, durable=False)

    # 绑定queue到交换机上
    channel.queue_bind(exchange='messages_fanout1', queue=queue_name)
    channel.queue_bind(exchange='messages_fanout2', queue=queue_name)
    channel.queue_bind(exchange='messages_fanout3', queue=queue_name)
    
    def callback(ch, method, properties, body):
        print(" [x] Received %r" % (body,))
    # 1. 阻塞读
    # channel.basic_consume(callback, queue=queue_name, no_ack=True) # 读取queue消息
    # 2. 非阻塞读
    while True:
        msg = channel.basic_get(queue=queue_name, no_ack=True) # 读取queue消息
        print('Recv msg:{}'.format(msg))
        time.sleep(1)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    connection.close()


# 3. 路由
def test_exchange_direct_send(connection, channel, persistent_properties):
    # 定义交换机，设置类型为direct
    channel.exchange_declare(exchange='exchange_direct', exchange_type='direct', durable=False)
    # 定义三个路由键
    routings = ['info', 'warning', 'error']
    # 将消息依次发送到交换机，并设置路由键
    for routing_key in routings:
        message = '%s message.' % routing_key
        channel.basic_publish( exchange='exchange_direct', routing_key=routing_key, body=message, properties=persistent_properties )
        print(message)
    connection.close()


def test_exchange_direct_get(connection, channel, persistent_properties):
    # 定义交换机，设置类型为direct
    channel.exchange_declare(exchange='exchange_direct', exchange_type='direct', durable=False)
    # 从命令行获取路由键参数，如果没有，则设置为info
    routings = sys.argv[1:]
    if not routings:
        routings = ['info']
    
    # 生成临时队列(不会触发持久化)
    result = channel.queue_declare(exclusive=True) # 声明创建队列
    queue_name = result.method.queue
    # direct模式下多个消费者不能使用同一个队列
    # queue_name = 'direct_queue'; channel.queue_declare(queue=queue_name, durable=False)
    for routing_key in routings:
        # 绑定到交换机上，设置路由键
        channel.queue_bind( exchange='exchange_direct', queue=queue_name, routing_key=routing_key )
    
    def callback(ch, method, properties, body):
        print(" [x] Received %r" % (body,))
    
    channel.basic_consume(callback, queue=queue_name, no_ack=True) # 读取queue消息
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    connection.close()


# 4. 模糊路由
def test_exchange_topic_send(connection, channel, persistent_properties):
    # 定义交换机，设置类型为topic
    concern_exchange = 'ProcIdle' # 'exchange_topic'
    channel.exchange_declare(exchange=concern_exchange, exchange_type='topic', durable=False)
    # 定义路由键
    routings = ['happy.work', 'happy.life', 'sad.work', 'sad.life', 'door_wxid_jy8batoqm0so12']
    print('publish topic message:')
    # 将消息依次发送到交换机，并设定路由键
    for routing_key in routings:
        message = '%s message.' % routing_key
        # channel.basic_publish( exchange='exchange_topic', routing_key=routing_key, body=message, properties=persistent_properties )
        channel.basic_publish( exchange=concern_exchange, routing_key=routing_key, body=message )
        print(message)
    connection.close()


def test_exchange_topic_get(connection, channel, persistent_properties):
    """
        关心所有topic, routing key = '#'
    """
    # 定义交换机，设置类型为topic
    concern_exchange = 'ProcIdle' # 'exchange_topic'
    channel.exchange_declare(exchange=concern_exchange, exchange_type='topic', durable=False)
    # channel.exchange_declare(exchange='messages_fanout', exchange_type='fanout', passive=False, durable=False, auto_delete=False) # 同时也关注广播!
    # 从命令行获取路由参数，如果没有，则报错退出
    routings = sys.argv[1:]
    if not routings:
        print("Usage: %s [routing_key]..." % ( sys.argv[0], ))
        exit()
    # 生成临时队列(不会触发持久化)
    result = channel.queue_declare(exclusive=True) # 声明创建队列
    queue_name = result.method.queue
    # topic模式下多个消费者不能使用同一个队列
    # queue_name = 'topic_queue'; channel.queue_declare(queue=queue_name, durable=False)
    for routing_key in routings:
        # 绑定到交换机上，设置路由键
        print('concern routing_key:', routing_key)
        channel.queue_bind( exchange=concern_exchange, queue=queue_name, routing_key=routing_key )
    # channel.queue_bind( exchange='messages_fanout', queue=queue_name ) # 同时也关注广播!
    def callback(ch, method, properties, body):
        print(ch, method, properties, body)
        # print(" [x] Received %r" % (body,))
    # 1. 阻塞读
    # channel.basic_consume(callback, queue=queue_name, no_ack=True) # 读取queue消息
    # 2. 非阻塞读
    while True:
        msg = channel.basic_get(queue=queue_name, no_ack=True) # 读取queue消息
        print('Recv msg:{}'.format(msg))
        time.sleep(1)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    connection.close()


def help():
    print("""
python ./{0} test_queue_send
python ./{0} test_queue_get
python ./{0} test_queue_get_nonblock

python ./{0} test_exchange_fanout_send
python ./{0} test_exchange_fanout_get

python ./{0} test_exchange_direct_send
python ./{0} test_exchange_direct_get

python ./{0} test_exchange_topic_send
python ./{0} test_exchange_topic_get "#"
python ./{0} test_exchange_topic_get "happy.*"
python ./{0} test_exchange_topic_get "*.work"
    """.format(os.path.basename(__file__)))


def main(args):
    credentials = pika.PlainCredentials('guest', 'guest')
    # 貌似超过3倍heartbeat time才会超时, 断开链接. (并不是完全是), 默认值为60
    parameters = pika.ConnectionParameters(host='localhost', port=5672, virtual_host='/', credentials=credentials, heartbeat_interval=60)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    persistent_properties = pika.BasicProperties(delivery_mode=2)
    eval(args.function)(connection, channel, persistent_properties)


def init_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-hostname', metavar='<hostname>', type=str, dest='hostname')
    parser.add_argument('-port', metavar='<port>', type=int, dest='port')
    parser.add_argument('-function', metavar='<function>', type=str, dest='function')
    parser.add_argument('-username', metavar='<username>', type=str, dest='username')
    parser.add_argument('-password', metavar='<password>', type=str, dest='password')
    return parser.parse_args()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        help(), sys.exit()
    args = init_args()
    main(args)
