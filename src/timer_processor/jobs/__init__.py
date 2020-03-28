class MetaClass(type):
    jobs = []

    def __new__(cls, name, bases, dct):
        # dct['a'] = 1      # 可用于设置属性值
        if 'start' not in dct:
            raise Exception('function start() need implement!')
        obj = type.__new__(cls, name, bases, dct)
        cls.jobs.append(obj)
        return obj
