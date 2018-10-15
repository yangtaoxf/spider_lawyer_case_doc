# coding=utf8
from dbtools.lawcase_settings import LawCaseConfig as Config

import pymysql
import logging
from proxy.pool import ProxyPool


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


class CaseDetailDao(object):
    def __init__(self):
        sql = '''
        SELECT 
            remarks,
            create_date,
            doc_id,
            update_date,
            state,
            doc_javascript
        FROM case_detail WHERE state=%s ORDER BY create_date limit 1 
        '''
        row = fetch_one(sql, (CASE_DETAIL_STATE_00,))
        update("UPDATE case_detail SET state=%s WHERE doc_id=%s", (CASE_DETAIL_STATE_01, row.get("doc_id")))
        logging.info(row)
        self.case_detail = row

    def update_case_detail(self, java_script=None):
        """
        :param state:状态
        :param java_script:脚本
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
            update(sql, (state, java_script, self.case_detail.get("doc_id"),))
        except Exception as e:
            logging.error(e)
