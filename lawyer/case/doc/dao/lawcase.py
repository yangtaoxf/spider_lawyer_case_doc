# coding=utf8
import datetime
import logging

import pymysql

import config
from config import TABLE_NAME_SUFFIX, WHERE_IDX_CONDITION
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


def refresh_system_dict():
    config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIME = fetch_one("""SELECT data_value from system_dict 
              where data_type='spider' 
                    and data_key='CASE_DETAIL_MASTER_WHERE_CONDITION_TIME'""")["data_value"]
    logging.info("config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIME=" + config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIME)
    t = datetime.datetime.strptime(config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIME, "%Y-%m-%d %H:%M:%S")
    config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIMEDELTA = fetch_one("""SELECT data_value from system_dict 
              where data_type='spider' 
                    and data_key='CASE_DETAIL_MASTER_WHERE_CONDITION_TIMEDELTA'""")["data_value"]
    if config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIMEDELTA and config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIME:
        t_new = t + datetime.timedelta(minutes=int(config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIMEDELTA))
        config.CASE_DETAIL_MASTER_WHERE_CONDITION_SQL = "and create_date between '{}' and '{}'".format(
            config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIME, t_new)

    #
    config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME = fetch_one("""SELECT data_value from system_dict 
              where data_type='spider' 
                    and data_key='CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME'""")["data_value"]
    logging.info("config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME=" +
                 config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME)
    t2 = datetime.datetime.strptime(config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME, "%Y-%m-%d %H:%M:%S")
    config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIMEDELTA = fetch_one("""SELECT data_value from system_dict 
              where data_type='spider' and data_key='CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIMEDELTA'""")[
        "data_value"]
    if config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME and config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIMEDELTA:
        t2_new = t2 + datetime.timedelta(minutes=int(config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIMEDELTA))
        config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_SQL = "and create_date between '{}' and '{}'".format(
            config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME, t2_new)
    logging.info("config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_SQL=" +
                 config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_SQL)
    #
    config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME = fetch_one("""SELECT data_value from system_dict 
              where data_type='spider' 
                    and data_key='CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME'""")["data_value"]
    logging.info("config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME=" +
                 config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME)
    t2 = datetime.datetime.strptime(config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME, "%Y-%m-%d %H:%M:%S")
    config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIMEDELTA = fetch_one("""SELECT data_value from system_dict 
              where data_type='spider' and data_key='CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIMEDELTA'""")[
        "data_value"]
    if config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME and config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIMEDELTA:
        t2_new = t2 + datetime.timedelta(minutes=int(config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIMEDELTA))
        config.CASE_PLAN_SCHEMA_DETAIL_MASTER_WHERE_CONDITION_SQL = "and create_date between '{}' and '{}'".format(
            config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME, t2_new)
    logging.info("config.CASE_PLAN_SCHEMA_DETAIL_MASTER_WHERE_CONDITION_SQL=" +
                 config.CASE_PLAN_SCHEMA_DETAIL_MASTER_WHERE_CONDITION_SQL)


def append_timedelta(data_type="spider", data_key="CASE_DETAIL_MASTER_WHERE_CONDITION_TIME",
                     interval=config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIMEDELTA):
    sql = """
            UPDATE system_dict 
                    SET data_value=date_add(DATE_FORMAT(data_value,%s),interval {} minute)
            WHERE data_type='{}' and data_key='{}'
    """.format(interval, data_type, data_key)
    logging.info(sql)
    update(sql, ('%Y-%m-%d %H:%i:%S',))


def append_timedelta_service():
    refresh_system_dict()
    append_timedelta(data_type="spider", data_key="CASE_DETAIL_MASTER_WHERE_CONDITION_TIME",
                     interval=config.CASE_DETAIL_MASTER_WHERE_CONDITION_TIMEDELTA)


def get_system_dict_case_detail_master_where_condition_sql():
    refresh_system_dict()
    return config.CASE_DETAIL_MASTER_WHERE_CONDITION_SQL


class SystemDict(object):
    @staticmethod
    def system_refresh_system_dict():
        refresh_system_dict()

    @staticmethod
    def system_append_timedelta(data_type, data_key, interval):
        append_timedelta(data_type, data_key, interval)


refresh_system_dict()
logging.warning(config.CASE_DETAIL_MASTER_WHERE_CONDITION_SQL)
CASE_DETAIL_STATE_00 = "00"
CASE_DETAIL_STATE_01 = "01"
CASE_DETAIL_STATE_03 = "03"  # 异常
CASE_DETAIL_STATE_07 = "07"  # 文档不存在
CASE_DETAIL_STATE_08 = "08"  # remind错误
CASE_DETAIL_STATE_09 = "09"  # 爬取失败
CASE_DETAIL_STATE_10 = "10"  # 爬取成功
CASE_DETAIL_STATE_10_NEW = "10_NEW"  # 爬取成功，javaScript数据放到case_doc表中
CASE_DETAIL_STATE_11 = "11"  # 正在格式化
CASE_DETAIL_STATE_11_NEW = "11_NEW"  # 正在格式化，javaScript数据已经放到case_doc表中
CASE_DETAIL_STATE_19 = "19"  # 格式化出现错误
CASE_DETAIL_STATE_20 = "20"  # 格式化成功,且入库成功
CASE_PLAN_SCHEMA_STATE_11 = 11  # 计划11正在队列中


class CaseDetailDao(object):
    task_pool = []
    _TASK_LIST = "task_set" + TABLE_NAME_SUFFIX
    DEAL_MIN_TASK_NUM = 60
    logging.info("_TASK_LIST=>" + _TASK_LIST)

    @staticmethod
    def init(count, task_pool):
        # from util.redis_util import extract_task_list
        _count = count
        __history_length = len(task_pool) if task_pool else 0
        # CaseDetailDao.init_task_list_push()
        logging.info("__history_length=" + str(__history_length))
        if __history_length < _count and __history_length < CaseDetailDao.DEAL_MIN_TASK_NUM:
            _count = _count - __history_length
            logging.info("_count=" + str(_count))
            ret_list = CaseDetailDao.extract_case_detail(key=CaseDetailDao._TASK_LIST, extract_num=_count)
            CaseDetailDao.task_pool = CaseDetailDao.task_pool + ret_list
        CaseDetailDao.task_pool.sort()
        logging.info(CaseDetailDao.task_pool)

    @staticmethod
    def extract_case_detail(key, extract_num=50):
        from util.redis_util import redis_client
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(data.decode("utf-8"))
            else:
                break
        return _ret

    @staticmethod
    def remove_doc_id(doc_id):
        CaseDetailDao.task_pool.remove(doc_id)

    @staticmethod
    def update_case_detail_when_case_doc(state, doc_id, remarks=None, master_domain=None, judge_year=None,
                                         province=None, court_level=None):
        if remarks:
            sql = '''UPDATE  case_detail{} SET state=%s,remarks=%s WHERE doc_id=%s'''.format(
                TABLE_NAME_SUFFIX)
            args = (state, remarks, doc_id,)
        else:
            sql = '''UPDATE  case_detail{} 
                        SET state=%s,case_type=%s,judge_year=%s,province=%s,court_level=%s
                    WHERE doc_id=%s'''.format(
                TABLE_NAME_SUFFIX)
            args = (state, master_domain, judge_year, province, court_level, doc_id,)
        return update(sql, args)

    @staticmethod
    def update_case_detail(doc_id, java_script=None, ip_proxy_item=None):
        """
        :param ip_proxy_item:状态
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
            state = CASE_DETAIL_STATE_10_NEW
        else:
            logging.warning("下载文书发生错误:->" + str(java_script))
        if "window.location.href" in java_script:
            state = CASE_DETAIL_STATE_08
        try:
            sql = '''UPDATE case_detail{} SET state=%s WHERE doc_id=%s'''.format(TABLE_NAME_SUFFIX)
            logging.info("===STATE: {} ***{}===".format(state, ip_proxy_item))
            update(sql, (state, doc_id,))
            CaseDocDao.insert_into_case_doc(doc_id=doc_id, java_script=java_script, content=None, html=None)
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
        FROM case_plan_schema{} WHERE state='10' ORDER BY schema_day,batch_count limit %s 
        '''.format(TABLE_NAME_SUFFIX)
        row = fetch_all(sql, batch_num)
        for data in row:
            update("UPDATE case_plan_schema{} SET state=%s {} WHERE rule_id=%s".format(TABLE_NAME_SUFFIX,
                                                                                       WHERE_IDX_CONDITION),
                   (CASE_PLAN_SCHEMA_STATE_11, data.get("rule_id")))
        logging.info(row)
        return row


class CasePlanSchemaDetailDao(object):

    @staticmethod
    def extract_case_plan_schema_detail(batch_num):
        from law_case_db import CASE_PLAN_SCHEMA_DETAIL_01
        SystemDict.system_refresh_system_dict()
        sql = '''
        SELECT 
            detail_id,
            rule_id,
            schema_day,
            state,
            json_text,
            create_date,
            update_date,
            remarks
        FROM case_plan_schema_detail{} WHERE state='00' {} limit {} 
        '''.format(TABLE_NAME_SUFFIX, config.CASE_PLAN_SCHEMA_DETAIL_MASTER_WHERE_CONDITION_SQL, batch_num)
        logging.info("extract_case_plan_schema_detail={}".format(sql))
        row = fetch_all(sql, ())
        if len(row) <= 0:
            SystemDict.system_append_timedelta(data_type="spider",
                                               data_key="CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIME",
                                               interval=config.CASE_PLAN_SCHEMA_DETAIL_MASTER_CONDITION_TIMEDELTA)
        for data in row:
            update("UPDATE case_plan_schema_detail{} SET state=%s WHERE detail_id=%s".format(TABLE_NAME_SUFFIX),
                   (CASE_PLAN_SCHEMA_DETAIL_01, data.get("detail_id")))
        logging.info("extract_case_plan_schema_detail{} batch_num={} OK=====".format(TABLE_NAME_SUFFIX, str(batch_num)))
        return row


class CaseDocDao(object):

    @staticmethod
    def extract_case_doc(batch_num):
        SystemDict.system_refresh_system_dict()
        sql = '''
                SELECT 
                    detail_id,
                    doc_id,
                    doc_javascript,
                    state,
                    doc_title,
                    doc_judge_date,
                    doc_court
                FROM case_detail{} WHERE state=%s {} limit %s 
                '''.format(TABLE_NAME_SUFFIX, config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_SQL, )
        logging.info("extract_case_doc sql={}".format(sql))
        row = fetch_all(sql, (CASE_DETAIL_STATE_10_NEW, batch_num,))
        logging.info("extract_case_doc =============")
        if len(row) <= 0:
            SystemDict.system_append_timedelta(data_type="spider",
                                               data_key="CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME",
                                               interval=config.CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIMEDELTA)
        for data in row:
            if data.get("doc_javascript"):
                data["exists"] = False
            else:
                data["doc_javascript"] = CaseDocDao.select_case_doc(doc_id=data["doc_id"]).get("java_script")
                data["exists"] = True
            update("UPDATE case_detail{} SET state=%s WHERE doc_id=%s".format(TABLE_NAME_SUFFIX),
                   (CASE_DETAIL_STATE_11_NEW, data.get("doc_id")))
        logging.info("extract_case_doc from case_detail{} table ***batch_num={}*** OK=====".
                     format(TABLE_NAME_SUFFIX, str(batch_num)))
        return row

    @staticmethod
    def select_case_doc(doc_id):
        sql = "SELECT java_script FROM `case_doc{}` WHERE doc_id=%s".format(TABLE_NAME_SUFFIX)
        row = fetch_one(sql, (doc_id,))
        return row

    @staticmethod
    def insert_into_case_doc(doc_id, content, html, java_script, exists=False):
        template_sql = '''INSERT INTO `case_doc{}`
         (`doc_id`,
          `content`,
          `html`,
          `java_script`,
          `create_time`,
          `update_time`
          )  VALUES (%s, %s, %s, %s, now(), now()) on DUPLICATE KEY UPDATE `java_script`=%s,`update_time`=now()'''.format(
            TABLE_NAME_SUFFIX)
        return insert(template_sql, (doc_id, content, html, java_script, java_script))

    # if exists:
    #     CaseDocDao.update_case_doc(content, html, doc_id, java_script)

    @staticmethod
    def update_case_doc(content, html, doc_id, java_script):
        __sql = ""
        __data = []
        if content:
            __sql += + "content=%s,"
            __data.append(content)
        if html:
            __sql += "html=%s,"
            __data.append(html)
        if java_script:
            __sql += "java_script=%s,"
            __data.append(__data)
        if not __sql:
            logging.warning("===没有数据，更新===")
            return
        template_sql = '''UPDATE `case_doc{}` SET {}update_time=now() WHERE doc_id=%s'''.format(TABLE_NAME_SUFFIX,
                                                                                                __sql)
        __data.append(doc_id)
        data = tuple(__data)
        logging.info("template_sql={}".format(template_sql))
        return update(template_sql, data)
