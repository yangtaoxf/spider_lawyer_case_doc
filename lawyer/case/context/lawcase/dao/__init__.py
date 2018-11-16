# coding=utf8
import logging

import pymysql

from lawcase.config import DuoWenConfig as Config, TABLE_NAME_SUFFIX, DOC_VERSION
import uuid
from lawcase.bean import LawyerInfoBean, CaseLawyerContextBean, CaseLawyerDocBean

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


class CaseLawyerDao(object):
    logging.info("===[CaseLawyerDao TABLE_NAME_SUFFIX is case_lawyer_schema_before{}]===".format(TABLE_NAME_SUFFIX))

    @staticmethod
    def execute_sql(sql, args):
        return update(sql, args)

    @staticmethod
    def update(lawyer_id, index, process):
        template_sql = '''update `case_lawyer{}` set `pageindex`=%s,process=%s,updatedate=now()  where `id`= %s'''.format(
            TABLE_NAME_SUFFIX);
        update(template_sql, (index, process, lawyer_id,))

    @staticmethod
    def extract(batch_num):
        """
        返回待处理数据
        :return:
        """
        sql = '''
        SELECT 
            id,
            casenum,
            office,
            phone,
            realname,
            remarks,
            fail,
            pageindex,
            process,
            repeatcont,
            remark,
            page
        FROM case_lawyer{} WHERE process='{}' limit {}
        '''.format(TABLE_NAME_SUFFIX, CaseLawyerContextBean.STATUS_00, batch_num)
        logging.info("[CaseLawyerDao extract sql] = {}".format(sql))
        row = fetch_all(sql, ())
        for data in row:
            update("UPDATE case_lawyer{} SET process=%s  WHERE id=%s".format(TABLE_NAME_SUFFIX),
                   (LawyerInfoBean.PROCESS_1, data.get("id")))
            data["process"] = LawyerInfoBean.PROCESS_1  # 更新队列状态
        logging.info(row)
        return row


class CaseLawyerContextDao(object):
    logging.info("===[CaseLawyerContextDao TABLE_NAME_SUFFIX is {}]===".format(TABLE_NAME_SUFFIX))

    @staticmethod
    def extract(batch_num):
        sql = '''
        SELECT 
            `id`,
            `lawyer_id`,
            `json_batch_count`,
            `page_json`,
            `index`,
            `pageNum`,
            `status` 
        FROM case_lawyer_context{} WHERE status='{}' limit {}
        '''.format(TABLE_NAME_SUFFIX, CaseLawyerContextBean.STATUS_00, batch_num)
        logging.info("[CaseLawyerContextDao extract sql] = {}".format(sql))
        row = fetch_all(sql, ())
        for data in row:
            CaseLawyerContextDao.update_state(state=CaseLawyerContextBean.STATUS_01, _id=data.get("id"))
            data["status"] = CaseLawyerContextBean.STATUS_01  # 更新队列状态
        return row

    @staticmethod
    def update_state(_id, state):
        update("UPDATE case_lawyer_context{} SET status=%s  WHERE id=%s".format(TABLE_NAME_SUFFIX), (state, _id))

    @staticmethod
    def insert_case_lawyer_context(lawyer_id, page_json, index, batch_count, pageNum=20):
        template_sql = '''INSERT INTO `case_lawyer_context{}`
             (`id`,
              `lawyer_id`,
              `page_json`,
              `json_batch_count`,
              `index`,
              `pageNum`
               )  VALUES (%s, %s, %s, %s, %s,%s)'''.format(TABLE_NAME_SUFFIX)
        id = str(uuid.uuid1())
        insert(template_sql, (id, lawyer_id, page_json, batch_count, index, pageNum,))


class CaseLawyerDocDao(object):
    logging.info("===[CaseLawyerDoc TABLE_NAME_SUFFIX is {}]===".format(TABLE_NAME_SUFFIX))

    @staticmethod
    def insert(*args):
        template_sql = '''INSERT INTO `case_lawyer_doc{}` 
             (`doc_id`,
              `spider_id`,
              `lawyer_id`,
              `json_batch_count`,
              `json_data_type`,
              `json_data_date`,
              `json_data_name`,
              `json_data_level`,
              `json_data_number`,
              `json_data_court` 
               )  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''.format(TABLE_NAME_SUFFIX)
        insert(template_sql, *args)

    @staticmethod
    def extract(batch_num):
        sql = '''
               SELECT 
                   `doc_id`,
                   `spider_id`,
                   `lawyer_id`,
                   `sync_status` 
               FROM case_lawyer_doc{} WHERE sync_status='{}' limit {}
               '''.format(TABLE_NAME_SUFFIX, CaseLawyerDocBean.SYNC_STATUS_00, batch_num)
        logging.info("[CaseLawyerDocDao extract sql] = {}".format(sql))
        row = fetch_all(sql, ())
        for data in row[0:]:
            doc_id = data.get("doc_id")
            lawyer_id = data.get("lawyer_id")
            ret = LawyerCaseDao.exist(doc_id=doc_id, lawyer_id=lawyer_id)

            if ret and ret[0]["sourceFrom"] and "PYTHON" in ret[0]["sourceFrom"]:  # 以前抓取过
                logging.info("[=*= 文档已经存在 =*=]doc_id={} lawyer_id={}".format(doc_id, lawyer_id))
                CaseLawyerDocDao.update_sync_status(state=CaseLawyerDocBean.SYNC_STATUS_0E, doc_id=data.get("doc_id"))
                row.remove(data)
                continue  # 跳过
            CaseLawyerDocDao.update_sync_status(state=CaseLawyerDocBean.SYNC_STATUS_01, doc_id=data.get("doc_id"))
            data["sync_status"] = CaseLawyerDocBean.SYNC_STATUS_01  # 更新队列状态
        logging.info(row)
        return row

    @staticmethod
    def formatter_extract(batch_num):
        sql = '''
               SELECT 
                   `doc_id`,
                   `spider_id`,
                   `lawyer_id`,
                   `sync_status`,
                   `java_script`,
                   `json_data_name`,
                   `json_data_date`,
                   `json_data_court` 
               FROM case_lawyer_doc{} WHERE sync_status='{}' limit {}
               '''.format(TABLE_NAME_SUFFIX, CaseLawyerDocBean.SYNC_STATUS_10, batch_num)
        logging.info("[CaseLawyerContextDao formatter_extract sql] = {}".format(sql))
        row = fetch_all(sql, ())
        for data in row:
            CaseLawyerDocDao.update_sync_status(state=CaseLawyerDocBean.SYNC_STATUS_11, doc_id=data.get("doc_id"))
            data["sync_status"] = CaseLawyerDocBean.SYNC_STATUS_11  # 更新队列状态
        return row

    @staticmethod
    def formatter_update(doc_id, sync_status, master_domain=None, html=None, remark=None, ):
        args = []
        __sql = ""
        if html:
            __sql += "html=%s,"
            args.append(html)
        if remark:
            __sql += "remark=%s,"
            args.append(remark)
        if master_domain:
            __sql += "master_domain=%s,"
            args.append(master_domain)
        # ---
        sql = "UPDATE case_lawyer_doc{} SET {}sync_status=%s  WHERE doc_id=%s".format(TABLE_NAME_SUFFIX, __sql)
        logging.info("formatter_update sql = {}".format(sql))
        args.append(sync_status)
        args.append(doc_id)
        update(sql, tuple(args))

    @staticmethod
    def update_sync_status(doc_id, state, java_script=None):
        if java_script:
            update(
                "UPDATE case_lawyer_doc{} SET sync_status=%s,java_script=%s  WHERE doc_id=%s".format(TABLE_NAME_SUFFIX),
                (state, java_script, doc_id,))
        else:
            update(
                "UPDATE case_lawyer_doc{} SET sync_status=%s WHERE doc_id=%s".format(TABLE_NAME_SUFFIX),
                (state, doc_id))

    @staticmethod
    def sync_doc_extract(batch_num):
        sql = '''
               SELECT 
                   `doc_id`,
                   `lawyer_id`,
                   `json_data_type`,
                   `json_data_date`,
                   `json_data_name`,
                   `json_data_level`,
                   `json_data_number`,
                   `json_data_court`,
                   `html`,
                   `sync_status`,
                   `master_domain`,
                   `spider_id` 
               FROM case_lawyer_doc{} WHERE sync_status='{}' limit {}
               '''.format(TABLE_NAME_SUFFIX, CaseLawyerDocBean.SYNC_STATUS_20, batch_num)
        logging.info("[CaseLawyerContextDao sync_doc_extract sql] = {}".format(sql))
        row = fetch_all(sql, ())
        for data in row:
            doc_id = data.get("doc_id")
            lawyer_id = data.get("lawyer_id")
            update("UPDATE case_lawyer_doc{} SET sync_status=%s WHERE doc_id=%s and lawyer_id=%s".format(
                TABLE_NAME_SUFFIX),
                (CaseLawyerDocBean.SYNC_STATUS_21, doc_id, lawyer_id,)
            )
            data["sync_status"] = CaseLawyerDocBean.SYNC_STATUS_21  # 更新队列状态
        logging.info(row)
        return row

    @staticmethod
    def sync_update_sync_status(doc_id, lawyer_id, status):
        update(
            "UPDATE case_lawyer_doc{} SET sync_status=%s WHERE doc_id=%s and lawyer_id=%s".format(TABLE_NAME_SUFFIX),
            (status, doc_id, lawyer_id))


class LawyerCaseDao(object):

    @staticmethod
    def exist(lawyer_id, doc_id) -> list:
        args = []
        __sql = ""
        if lawyer_id:
            __sql += "lawyer_id=%s and "
            args.append(lawyer_id)
        if doc_id:
            __sql += "sourceId=%s and "
            args.append(doc_id)
        # ---
        sql = '''
               SELECT 
                   `id`,
                   `sourceFrom`
               FROM lawyercase WHERE {} 1=1 
               '''.format(__sql)
        row = fetch_all(sql, tuple(args))
        return row

    @staticmethod
    def insert(lawyer_id, doc_id, html, caseType, casenum, title, court):
        template_sql = '''INSERT INTO `lawyercase` 
             (`id`,
              `caseType`,
              `casenum`,
              `content`,
              `title`,
              `lawyer_id`,
              `court`,
              `createDate`,
              `views`,
              `sourceFrom`,
              `sourceId`,
              `updateDate`
               )  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), 0, %s, %s, now())'''.format(TABLE_NAME_SUFFIX)
        __id = LawyerCaseDao.__build_id(lawyer_id=lawyer_id, doc_id=doc_id)
        insert(template_sql, (__id, caseType, casenum, html, title, lawyer_id, court, DOC_VERSION, doc_id,))

    @staticmethod
    def __build_id(lawyer_id, doc_id):
        """
        构建新的数据库id
        :param lawyer_id:
        :param doc_id:
        :return:
        """
        return "{}+{}".format(lawyer_id, doc_id)

    @staticmethod
    def update_by_id(id, html):
        return update("UPDATE lawyercase SET `content`=%s,sourceFrom=%s,updateDate=now() WHERE `id`=%s",
                      (html, DOC_VERSION, id,))
