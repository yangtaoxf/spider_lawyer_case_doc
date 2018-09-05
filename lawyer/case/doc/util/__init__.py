import time


def get_linux_time():
    """
    获取linux 10位时间戳
    :return:
    """
    return time.time().__int__()
