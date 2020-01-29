class GlobalException(Exception):
    def __init__(self, data: dict, status=200):
        self.data = data
        self.status = status
