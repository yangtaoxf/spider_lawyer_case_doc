# coding=utf8
import logging

import pymysql

from dbtools.lawcase_settings import LawCaseConfig as Config
from proxy.pool import ProxyPool

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def connect():
    conn = Config.POOL.connection()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  # 以字典的方式 显示
    return conn, cursor


def connect_close(conn, cursor):
    cursor.close()
    conn.close()


def fetch_all(sql, args=()):
    conn, cursor = connect()
    cursor.execute(sql, args)
    record_list = cursor.fetchall()
    connect_close(conn, cursor)
    return record_list


def fetch_one(sql, args=()):
    conn, cursor = connect()
    cursor.execute(sql, args)
    result = cursor.fetchone()
    connect_close(conn, cursor)
    return result


def insert(sql, args):
    conn, cursor = connect()
    row = cursor.execute(sql, args)
    conn.commit()
    connect_close(conn, cursor)
    return row


def update(sql, args):
    conn, cursor = connect()
    row = cursor.execute(sql, args)
    conn.commit()
    connect_close(conn, cursor)
    return row


CASE_DETAIL_STATE_00 = "00"
CASE_DETAIL_STATE_01 = "01"
CASE_DETAIL_STATE_03 = "03"  # 异常
CASE_DETAIL_STATE_07 = "07"  # 文档不存在
CASE_DETAIL_STATE_08 = "08"  # remind错误
CASE_DETAIL_STATE_09 = "09"  # 爬取失败
CASE_DETAIL_STATE_10 = "10"  # 爬取成功

CASE_PLAN_SCHEMA_STATE_11 = 11  # 计划11正在队列中
_TASK_LIST = "task_list"


class CaseDetailDao(object):
    task_pool = []

    @staticmethod
    def init(count, task_pool):
        from util.redis_util import extract_task_list
        _count = count
        __history_length = len(task_pool) if task_pool else 0
        CaseDetailDao.init_task_list_push()
        logging.info("__history_length=" + str(__history_length))
        if __history_length < _count and __history_length < 50:
            _count = _count - __history_length
            logging.info("_count=" + str(_count))
            ret_list = extract_task_list(key=_TASK_LIST, start=0, end=_count)
            CaseDetailDao.task_pool = CaseDetailDao.task_pool + ret_list
        CaseDetailDao.task_pool.sort()
        logging.info(CaseDetailDao.task_pool)

    @staticmethod
    def init_task_list_push(length=500):
        from util.redis_util import task_list_push, task_list_length
        _length = task_list_length(_TASK_LIST)
        if _length > length:
            logging.info("不需要初始化任务队列：数量为" + str(_length))
            return
        __task_pool = []
        sql = '''
                    SELECT 
                        remarks,
                        create_date,
                        doc_id,
                        state
                    FROM case_detail WHERE state=%s limit %s 
                    '''
        row = fetch_all(sql, (CASE_DETAIL_STATE_00, length))
        for data in row:
            __doc_id = data.get("doc_id")
            update("UPDATE case_detail SET state=%s WHERE doc_id=%s", (CASE_DETAIL_STATE_01, __doc_id))
            __task_pool.append(__doc_id)
        task_list_push(key=_TASK_LIST, value=__task_pool)
        logging.info(__task_pool)

    @staticmethod
    def remove_doc_id(doc_id):
        CaseDetailDao.task_pool.remove(doc_id)

    @staticmethod
    def update_case_detail(doc_id, java_script=None):
        """
        :param state:状态
        :param java_script:脚本
        :param doc_id
        :return:
        """
        # 保存html页面
        state = CASE_DETAIL_STATE_03
        if java_script is None or java_script == "":
            state = CASE_DETAIL_STATE_09
        elif "此篇文书不存在" in java_script:
            CASE_DETAIL_STATE_07
        elif "JSON.stringify" in java_script:
            state = CASE_DETAIL_STATE_10
        else:
            logging.warning("下载文书发生错误:->" + str(java_script))
        if "window.location.href" in java_script:
            state = CASE_DETAIL_STATE_08
            ProxyPool().refresh()
        try:
            sql = '''UPDATE case_detail SET state=%s,doc_javascript=%s WHERE doc_id=%s'''
            logging.info("STATE=>" + state)
            update(sql, (state, java_script, doc_id,))
        except Exception as e:
            logging.error(e)


class CasePlanSchemaDao(object):

    @staticmethod
    def extract_case_plan_schema(batch_num):
        """
        返回待处理数据
        :return:
        """
        sql = '''
        SELECT 
            rule_id,
            batch_count,
            remarks,
            create_date,
            update_date,
            fail,
            page_index,
            repeat_count,
            schema_day,
            schema_search,
            total_count,
            state 
        FROM case_plan_schema WHERE state='10' ORDER BY schema_day,batch_count limit %s 
        '''
        row = fetch_all(sql, batch_num)
        for data in row:
            update("UPDATE case_plan_schema SET state=%s WHERE rule_id=%s",
                   (CASE_PLAN_SCHEMA_STATE_11, data.get("rule_id")))
        logging.info(row)
        return row
