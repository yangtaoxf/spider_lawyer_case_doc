# coding=utf8

import download
import asyncio
from dao.lawcase import CaseDetailDao
from proxy.pool import ProxyPool
import copy
import logging
import time, datetime
from config import IP_PROXY_CACHE, IP_PROXY_FREE_CACHE, IP_PEER_DOC_WEIGHT

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def free_time(pool: ProxyPool):
    now_time = datetime.datetime.now()
    hours = now_time.strftime('%H')
    int_hours = int(hours)
    ip_proxy_cache = pool.get_ip_proxy_cache()
    if int_hours in (19, 20, 21, 22, 23, 1, 2, 3, 4, 5, 6, 7, 8):
        logging.info("=*= 空闲时间内 =*=")
        if ip_proxy_cache != IP_PROXY_FREE_CACHE:
            logging.info("=*= 空闲时间内 改变IP数量 =*=")
            pool.change_ip_proxy_cache(IP_PROXY_FREE_CACHE)
    else:
        logging.info("=*= 正常时间内 =*=")
        if ip_proxy_cache != IP_PROXY_CACHE:
            logging.info("=*= 正常时间内 改变IP数量 =*=")
            pool.change_ip_proxy_cache(IP_PROXY_CACHE)


if __name__ == '__main__':
    pool = ProxyPool()
    task_pool = []
    while True:
        loop = asyncio.get_event_loop()
        task_pool = copy.deepcopy(CaseDetailDao.task_pool)
        free_time(pool)
        CaseDetailDao.init(pool.get_ip_proxy_cache() * IP_PEER_DOC_WEIGHT, task_pool)
        if not CaseDetailDao.task_pool:
            logging.info("没有任务，休眠5秒")
            time.sleep(5)
            continue

        CaseDetailDao.task_pool = list(set(CaseDetailDao.task_pool))
        pool.validate_init_ip_proxy()
        loop.run_until_complete(
            asyncio.wait(
                [download.async_get_data_javascript(__doc_id) for __doc_id in CaseDetailDao.task_pool])
        )
