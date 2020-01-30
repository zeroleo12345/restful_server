import os


class PidFile:
    @classmethod
    def save_pid_to_file(cls, pid_path='/tmp/app.pid'):
        pid = os.getpid()
        with open(pid_path, 'w+') as f:
            f.write(str(pid))
