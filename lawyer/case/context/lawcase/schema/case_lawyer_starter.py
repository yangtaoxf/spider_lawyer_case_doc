# coding=utf-8
# ------------------添加root_path
import os
import sys

current_Path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_Path)[0]
__root_path = root_path.split(sep="context")[0]
__root_path_1 = __root_path + "context" + os.sep
__root_path_2 = __root_path + "doc" + os.sep
print(__root_path_1, "========", __root_path_2)
sys.path.append(__root_path_1)
sys.path.append(__root_path_2)
# ------------------
from proxy.pool import ProxyPool
import asyncio
from lawcase.service import CasePlanSchema
from lawcase.bean import LawyerInfoBean
from lawcase.util.redis_task import RedisCaseLawyerTaskMasterHelper
from lawcase.config import LIST_CONTEXT_BATCH_NUM
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def remove_not_process_data(task_pool):
    logging.info("=*= 删除不需要爬取的律师队列 ===开始=*=")
    for _index in range(len(task_pool) - 1, -1, -1):  # 倒序循环
        data = task_pool[_index]
        if data and data.process == LawyerInfoBean.PROCESS_1:
            pass
        else:
            logging.info(data)
            task_pool.remove(data)
    logging.info("=*= 删除不需要爬取的律师队列 ===结束=*=")


if __name__ == '__main__':
    pool = ProxyPool()
    pool.change_ip_proxy_cache(1)  # 设置代理池一个ip
    task_pool = []
    while True:
        loop = asyncio.get_event_loop()
        pool.validate_init_ip_proxy()
        remove_not_process_data(task_pool)
        extract_num = LIST_CONTEXT_BATCH_NUM - len(task_pool)
        bean_list = RedisCaseLawyerTaskMasterHelper.extract_lawyer_info_bean_list(extract_num=extract_num)
        task_pool.extend(bean_list)
        if not task_pool:
            logging.info("=*=没有任务，休眠60秒=*=")
            time.sleep(60)
            continue
        loop.run_until_complete(asyncio.wait(
            [CasePlanSchema.proceed_schema(bean=bean_data) for bean_data in task_pool])
        )
