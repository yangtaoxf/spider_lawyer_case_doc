# coding=utf-8
import asyncio
import logging
import time

import download
from lawcase.bean import CaseLawyerDocBean
from lawcase.config import CaseLawyerDocConfig
from lawcase.util.redis_task import RedisCaseLawyerDocMaster
from proxy.pool import ProxyPool
from lawcase.dao import CaseLawyerDocDao

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

# def remove_not_process_data(task_pool):
#     logging.info("=*= 删除不需要爬取的律师队列 ===开始=*=")
#     for _index in range(len(task_pool) - 1, -1, -1):  # 倒序循环
#         data = task_pool[_index]
#         if data and data.process == LawyerInfoBean.PROCESS_1:
#             pass
#         else:
#             logging.info(data)
#             task_pool.remove(data)
#     logging.info("=*= 删除不需要爬取的律师队列 ===结束=*=")


task_pool = []


class CallBack(object):
    @staticmethod
    def callback_success(doc_id, java_script, ip_proxy_item):
        """
        :param ip_proxy_item:状态
        :param java_script:脚本
        :param doc_id
        :return:
        """
        # 保存html页面
        ip_proxy_item.success()
        task_pool.remove(doc_id)
        state = CaseLawyerDocBean.SYNC_STATUS_09
        if java_script is None or java_script == "":
            logging.info("=*= java_script没有值 =*=")
        elif "此篇文书不存在" in java_script:
            state = CaseLawyerDocBean.SYNC_STATUS_07
        elif "JSON.stringify" in java_script:
            state = CaseLawyerDocBean.SYNC_STATUS_10
        else:
            logging.warning("下载文书发生错误:->" + str(java_script))
        try:
            logging.info("===STATE: {} ***{}===".format(state, ip_proxy_item))
            CaseLawyerDocDao.update_sync_status(doc_id=doc_id, state=state, java_script=java_script)
        except Exception as e:
            logging.error(e)

    @staticmethod
    def callback_fail(doc_id):
        try:
            logging.info("===STATE: {} ***{}===".format("FAIL", "发生未识别的错误"))
            CaseLawyerDocDao.update_sync_status(doc_id=doc_id, state=CaseLawyerDocBean.SYNC_STATUS_09, )
        except Exception as e:
            logging.error(e)
        task_pool.remove(doc_id)


if __name__ == '__main__':
    pool = ProxyPool()
    pool.change_ip_proxy_cache(CaseLawyerDocConfig.IP_PROXY_CACHE_NUM__)  # 设置代理池一个ip
    while True:
        loop = asyncio.get_event_loop()
        pool.validate_init_ip_proxy()
        extract_num = CaseLawyerDocConfig.SPIDER_BATCH_NUM - len(task_pool)
        data_list = RedisCaseLawyerDocMaster.extract(extract_num=extract_num)
        task_pool.extend(data["doc_id"] for data in data_list)
        if not task_pool:
            logging.info("=*= 没有任务，休眠60秒 =*=")
            time.sleep(60)
            continue
        pool.validate_init_ip_proxy()
        loop.run_until_complete(
            asyncio.wait(
                [download.async_get_data_javascript_callback(doc_id, callback=CallBack) for doc_id in task_pool])
        )
