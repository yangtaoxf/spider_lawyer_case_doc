# coding=utf8
import ast
import json
import logging

import redis
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

__all__ = ["task_list_push", "extract_task_list", "task_list_length", "RedisCasePlanSchemaTaskMaster",
           "set_size", "set_sadd", "RedisCaseDetailMaster", "RedisCasePlanSchemaDetailMaster", "redis_client",
           "RedisCaseDocFormatMaster"]
conn_pool = redis.ConnectionPool(host='120.76.138.153', port=6379, password="duowenlvshi~6379")
redis_client = redis.Redis(connection_pool=conn_pool)
from config import TABLE_NAME_SUFFIX, IP_PROXY_CACHE, IP_PROXY_CACHE_TIME, IP_PROXY_INSPECT_URL


def task_list_push(key, value):
    for _it in value:
        redis_client.lpush(key, _it)
    logging.info(str(key) + "大小：==>" + str(redis_client.llen(key)))


def task_list_length(key):
    return redis_client.llen(key)


def extract_task_list(key, start=0, end=200):
    ret_list = []
    for it in range(start, end):
        task = redis_client.rpop(key)
        if task:
            ret_list.append(task.decode("utf-8"))
    return ret_list


def set_size(key):
    return redis_client.scard(key)


def set_sadd(key, values):
    redis_client.sadd(key, values)


class RedisCasePlanSchemaTaskMaster(object):
    """
    RedisTaskMaster分布式任务派发
    """

    KEY = "case_plan_schema" + TABLE_NAME_SUFFIX

    @staticmethod
    def refresh_case_plan_schema(key=KEY, batch_num=500):
        __size = redis_client.scard(key)
        logging.info("已经存在任务条数==>：" + str(__size))
        if __size >= batch_num:
            logging.info("存在条数大于==>" + str(batch_num) + "不新增任务；")
            return
        from dao.lawcase import CasePlanSchemaDao
        _ret = CasePlanSchemaDao.extract_case_plan_schema(batch_num=batch_num)
        for data in _ret:
            _data = str({
                "page_index": data["page_index"],
                "batch_count": data["batch_count"],
                "rule_id": data["rule_id"],
                "schema_search": data["schema_search"],
                "schema_day": data["schema_day"]
            })
            redis_client.sadd(key, _data)
        logging.info("refresh_case_plan_schema after size is==>" + str(redis_client.scard(key)))
        logging.info("refresh_case_plan_schema==OK==")

    @staticmethod
    def extract_case_plan_schema(key=KEY, extract_num=50):
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret


class RedisCaseDetailMaster(object):
    from dao.lawcase import CaseDetailDao
    task_name = CaseDetailDao._TASK_LIST
    min_extract_task_count = 5000

    @staticmethod
    def init_task_set_push(length=1000):
        from util.redis_util import redis_client, task_list_length
        from dao.lawcase import CASE_DETAIL_STATE_00, CASE_DETAIL_STATE_01, fetch_all, update, \
            get_system_dict_case_detail_master_where_condition_sql, append_timedelta_service
        _length = redis_client.scard(RedisCaseDetailMaster.task_name)
        logging.info("RedisCaseDetailMaster " + RedisCaseDetailMaster.task_name + "队列已经存在的任务数量为：" + str(_length))
        logging.info("RedisCaseDetailMaster " + RedisCaseDetailMaster.task_name + "队列需要初始化的任务数量为：" + str(length))
        __extract_task_count = length - _length
        logging.info("__extract_task_count=" + str(__extract_task_count))
        if __extract_task_count <= 0:
            logging.info("不需要初始化任务队列")
            return
        __task_pool = []
        __extract_task_count = __extract_task_count if __extract_task_count >= RedisCaseDetailMaster.min_extract_task_count else RedisCaseDetailMaster.min_extract_task_count
        sql = '''
                    SELECT 
                        remarks,
                        create_date,
                        doc_id,
                        state
                    FROM case_detail{} WHERE state=%s {} limit {} 
                    '''.format(TABLE_NAME_SUFFIX,
                               get_system_dict_case_detail_master_where_condition_sql(),
                               __extract_task_count)
        logging.info("""init_task_set_push:
        {}
        """.format(sql))
        row = fetch_all(sql, (CASE_DETAIL_STATE_00,))
        logging.info("RedisCaseDetailMaster init_task_list_push extract OK======")
        count = 0
        if len(row) <= 0:
            append_timedelta_service()  # 增加偏移
        for data in row:
            __doc_id = data.get("doc_id")
            update("UPDATE case_detail{} SET state=%s WHERE doc_id=%s".format(TABLE_NAME_SUFFIX),
                   (CASE_DETAIL_STATE_01, __doc_id))
            if count % 10 == 0:
                logging.info("RedisCaseDetailMaster init_task_list_push{} 10 task OK======".format(TABLE_NAME_SUFFIX))
            redis_client.sadd(RedisCaseDetailMaster.task_name, __doc_id)
            __task_pool.append(__doc_id)
        logging.info(
            "RedisCaseDetailMaster " + RedisCaseDetailMaster.task_name + "队列新加__task_pool任务为:" + str(__task_pool)
        )


class RedisCasePlanSchemaDetailMaster(object):
    KEY = "case_plan_schema_detail" + TABLE_NAME_SUFFIX
    MIN_EXTRACT_BATCH_NUM = 50

    @staticmethod
    def refresh_case_plan_schema_detail(key=KEY, batch_num=500):
        __size = redis_client.scard(key)
        logging.info("RedisCasePlanSchemaDetailMaster " + key + "已经存在任务条数==>：" + str(__size))
        logging.info("RedisCasePlanSchemaDetailMaster " + key + "计划缓存任务条数==>：" + str(batch_num))
        __extract_batch_num = batch_num - __size
        logging.info("RedisCasePlanSchemaDetailMaster __extract_batch_num=" + str(__extract_batch_num))
        if __extract_batch_num <= 0:
            logging.info(
                "RedisCasePlanSchemaDetailMaster refresh_case_plan_schema_detail{} 不新增任务；".format(TABLE_NAME_SUFFIX))
            return
        from dao.lawcase import CasePlanSchemaDetailDao
        __extract_batch_num = RedisCasePlanSchemaDetailMaster.MIN_EXTRACT_BATCH_NUM \
            if __extract_batch_num < RedisCasePlanSchemaDetailMaster.MIN_EXTRACT_BATCH_NUM else __extract_batch_num
        _ret = CasePlanSchemaDetailDao.extract_case_plan_schema_detail(batch_num=__extract_batch_num)
        for data in _ret:
            _data = str({
                "detail_id": data["detail_id"],
                "schema_day": data["schema_day"],
                "rule_id": data["rule_id"],
                "json_text": data["json_text"],
            })
            redis_client.sadd(key, _data)
        logging.info("refresh_case_plan_schema after size is==>" + str(redis_client.scard(key)))
        logging.info("refresh_case_plan_schema==OK==")

    @staticmethod
    def extract_case_plan_schema_detail(key=KEY, extract_num=50):
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret


class RedisCaseDocFormatMaster(object):
    KEY = "case_doc_format" + TABLE_NAME_SUFFIX
    MIN_EXTRACT_BATCH_NUM = 100

    @staticmethod
    def refresh_case_doc_format(key=KEY, batch_num=MIN_EXTRACT_BATCH_NUM):
        __size = redis_client.scard(key)
        logging.info("RedisCaseDocFormatMaster " + key + "已经存在任务条数==>：" + str(__size))
        logging.info("RedisCaseDocFormatMaster " + key + "计划缓存任务条数==>：" + str(batch_num))
        __extract_batch_num = batch_num - __size
        logging.info("RedisCaseDocFormatMaster __extract_batch_num=" + str(__extract_batch_num))
        if __extract_batch_num <= 0:
            logging.info(
                "RedisCaseDocFormatMaster refresh_case_doc_format{} 不新增任务；".format(TABLE_NAME_SUFFIX))
            return
        from dao.lawcase import CaseDocDao
        if RedisCaseDocFormatMaster.MIN_EXTRACT_BATCH_NUM > batch_num:
            RedisCaseDocFormatMaster.MIN_EXTRACT_BATCH_NUM = batch_num

        __extract_batch_num = RedisCaseDocFormatMaster.MIN_EXTRACT_BATCH_NUM if \
            __extract_batch_num < RedisCaseDocFormatMaster.MIN_EXTRACT_BATCH_NUM else __extract_batch_num
        _ret = CaseDocDao.extract_case_doc(batch_num=__extract_batch_num)
        for data in _ret:
            _data = str({
                "doc_id": data["doc_id"],
                "doc_javascript": data["doc_javascript"],
                "detail_id": data["detail_id"],
                "doc_title": data["doc_title"],
                "doc_judge_date": data["doc_judge_date"],
                "doc_court": data["doc_court"],
                "exists": data["exists"],
            })
            redis_client.sadd(key, _data)

        logging.info("refresh_case_doc_format after size is==>" + str(redis_client.scard(key)))
        logging.info("refresh_case_doc_format==OK==")

    @staticmethod
    def extract_case_doc_format(key=KEY, extract_num=50):
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret


class RedisIpProxyPool(object):
    proxy_cache = IP_PROXY_CACHE
    cache_time = IP_PROXY_CACHE_TIME
    inspect_url = IP_PROXY_INSPECT_URL

    @staticmethod
    def extract_remote_ip():
        from proxy.pool import IpPort
        ret = IpPort.get_remote_doc_ip()
        dj = json.loads(ret)
        ip_port = dj['data'][0].get("ip") + ":" + str(dj['data'][0].get("port"))
        proxies = {
            'http': 'http://{}'.format(ip_port),
            'https': 'https://{}'.format(ip_port),
        }
        return proxies

    @staticmethod
    def inspect(proxies):
        payload = {}
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Proxy - Connection': 'keep - alive',
                   "Accept-Language": "zh-CN,zh;q=0.9",
                   "Cache-Control": "max-age=0",
                   'Host': "www.baidu.com",
                   "Upgrade-Insecure-Requests": "1",
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                   'Upgrade-Insecure-Requests': '1',
                   }
        from datetime import datetime
        before = datetime.now().microsecond
        res = requests.get(
            url='https://www.baidu.com/',
            data=payload,
            headers=headers,
            proxies=proxies,
            timeout=10,
            allow_redirects=False)
        logging.info(res.status_code)
        res.close()
        after = datetime.now().microsecond
        assert res.status_code == 200
        return before - after

    @staticmethod
    def inspect_court(proxies):
        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Host': 'wenshu.court.gov.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        from datetime import datetime
        before = datetime.now().microsecond
        res = requests.get(
            url='http://www.wenshu.court.gov.cn',
            data=payload,
            headers=headers,
            proxies=proxies,
            timeout=10,
            allow_redirects=False)
        logging.info(res.text)
        logging.info(res.status_code)
        res.close()
        after = datetime.now().microsecond

        assert res.status_code == 200
        return before - after

    @staticmethod
    def extract_cache_ip(num=1):
        pass

# proxies = RedisIpProxyPool.extract_remote_ip()
# print(RedisIpProxyPool.inspect(proxies))
# print(RedisIpProxyPool.inspect_court(proxies))
