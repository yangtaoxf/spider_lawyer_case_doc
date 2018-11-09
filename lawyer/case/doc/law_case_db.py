# coding=utf8
import uuid

import dbtools.law_case_helper as db_lawcase_helper
from config import TABLE_NAME_SUFFIX

# 解密文档
CASE_PLAN_SCHEMA_DETAIL_00 = "00"  # 初始状态
CASE_PLAN_SCHEMA_DETAIL_01 = "01"  # 正在处理
CASE_PLAN_SCHEMA_DETAIL_03 = "03"  # 处理过程中发生部分错误
CASE_PLAN_SCHEMA_DETAIL_09 = "09"  # 处理全部失败
CASE_PLAN_SCHEMA_DETAIL_10 = "10"  # 全部成功
CASE_PLAN_SCHEMA_DETAIL_11 = "11"  # 正在格式化


def insert_case_plan_schema_detail(rule_id, page_index, schema_day, json_text):
    template_sql = '''INSERT INTO `case_plan_schema_detail{}`
         (`detail_id`,
         `rule_id`,
         `page_index`,
          `schema_day`,
          `state`,
          `json_text`
           )  VALUES (%s, %s, %s, %s, %s, %s)'''.format(TABLE_NAME_SUFFIX)
    _id = str(uuid.uuid1())
    db_lawcase_helper.insert(template_sql,
                             (_id, rule_id, page_index, schema_day, CASE_PLAN_SCHEMA_DETAIL_00, json_text,))


def update_case_plan_schema_detail_state(state, detail_id):
    template_sql = '''UPDATE `case_plan_schema_detail{}` SET state=%s WHERE detail_id=%s'''.format(TABLE_NAME_SUFFIX)
    db_lawcase_helper.insert(template_sql, (state, detail_id,))


def insert_case_detail(*args):
    template_sql = """
    INSERT INTO case_detail{}(
                detail_id,
                remarks,
                doc_id,
                schema_day,
                rule_id,
                state,
                doc_level,
                doc_num,
                doc_reason,
                doc_type,
                doc_judge_date,
                doc_title,
                doc_court
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """.format(TABLE_NAME_SUFFIX)
    db_lawcase_helper.insert(template_sql, *args)
########################################
