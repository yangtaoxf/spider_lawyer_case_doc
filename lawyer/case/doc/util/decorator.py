import logging
import functools
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

__all__ = ['log_cost_time', ]


def log_cost_time(describe=""):
    """
    统计方法耗时
    :param describe: 任务描述
    :return:
    """

    def wapper(func):
        @functools.wraps(func)
        def inner_wapper(*args, **kwargs):
            logging.info("===*=== [{}] [{}] 计时开始 ---*---".format(describe, func, ))
            starttime = datetime.datetime.now()
            ret = func(*args, **kwargs)
            endtime = datetime.datetime.now()
            cost_time_str = str((endtime - starttime).seconds)
            logging.info("---*--- [{}] [{}] 总耗时:{}s ===*===".format(describe, func, cost_time_str, ))
            return ret

        return inner_wapper

    return wapper


@log_cost_time(describe="测试数据")
def hello():
    logging.info("111111")

# hello()
