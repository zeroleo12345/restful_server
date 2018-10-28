import random


class MyRandom(object):
    LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
    UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    DIGIT = '0123456789'

    @classmethod
    def random_string(cls, length, lowercase=True, uppercase=False):
        choices = cls.DIGIT
        if lowercase:
            choices += cls.LOWERCASE
        if uppercase:
            choices += cls.UPPERCASE

        return ''.join(random.choice(choices) for _ in range(length))

    @classmethod
    def random_digit(cls, length):
        return ''.join(random.choice(cls.DIGIT) for _ in range(length))
