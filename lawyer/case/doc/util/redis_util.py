# coding=utf8
import logging
import redis
import ast

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

__all__ = ["task_list_push", "extract_task_list", "task_list_length", "RedisCasePlanSchemaTaskMaster",
           "set_size", "set_sadd"]
conn_pool = redis.ConnectionPool(host='120.76.138.153', port=6379, password="duowenlvshi~6379")
redis_client = redis.Redis(connection_pool=conn_pool)


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
    KEY = "case_plan_schema"

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


RedisCasePlanSchemaTaskMaster.refresh_case_plan_schema(batch_num=1)
