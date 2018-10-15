# coding=utf8

import download
import asyncio
from dao.lawcase import CaseDetailDao
from proxy.pool import ProxyPool

if __name__ == '__main__':
    pool = ProxyPool()
    while True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            asyncio.wait(
                [download.async_get_data_javascript(CaseDetailDao()) for
                 _ in
                 range(4)])
        )
