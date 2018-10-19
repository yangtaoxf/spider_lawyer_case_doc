# coding=utf8

import download
import asyncio
from dao.lawcase import CaseDetailDao
from proxy.pool import ProxyPool
import copy
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

if __name__ == '__main__':
    pool = ProxyPool()
    task_pool = []
    while True:
        loop = asyncio.get_event_loop()
        task_pool = copy.deepcopy(CaseDetailDao.task_pool)
        CaseDetailDao.init(200, task_pool)
        loop.run_until_complete(
            asyncio.wait(
                [download.async_get_data_javascript(__doc_id) for __doc_id in CaseDetailDao.task_pool])
        )
