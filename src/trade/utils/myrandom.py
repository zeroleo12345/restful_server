import random


class MyRandom(object):
    __random_char = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'    # 62个字符

    @classmethod
    def random_string(cls, length):
        return ''.join(random.choice(cls.__random_char) for _ in range(length))
