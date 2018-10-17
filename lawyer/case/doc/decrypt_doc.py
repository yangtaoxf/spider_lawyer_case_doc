# coding=utf8
import logging
import time
import json
import law_case_db as task_db
from util import decrypt_id, _test, _value
from pymysql.err import IntegrityError

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', )


class CaseDetailProcessor(object):
    """
    获取案例抓取计划
    """

    def __init__(self):
        self.case_plan_schema_detail_dict = {}
        self.case_plan_schema_detail_dict = task_db.extract_case_plan_schema_detail()

    def proceed(self):
        detail_id = self.case_plan_schema_detail_dict.get("detail_id")
        schema_day = self.case_plan_schema_detail_dict.get("schema_day")
        rule_id = self.case_plan_schema_detail_dict.get("rule_id")
        json_text = self.case_plan_schema_detail_dict.get("json_text")
        deal_state = task_db.CASE_PLAN_SCHEMA_DETAIL_09
        try:
            if "RunEval" in json_text:
                if '"[{\\' in json_text:
                    page_data = json.loads(json_text.replace('\\"', '\"')[1:-1])  # 转移字符
                else:
                    page_data = json.loads(json_text)
                global run_eval
                run_eval = None
                for it in page_data:
                    if it.get("RunEval") is not None:
                        run_eval = it.get("RunEval")
                        if it.get("Count") is not None:
                            continue
                    doc_source = it.get("裁判要旨段原文")
                    doc_type = it.get("案件类型")
                    doc_judge_date = it.get("裁判日期")
                    doc_title = it.get("案件名称")
                    _json_data_id = decrypt_id(run_eval, it.get("文书ID"))
                    logging.info(_json_data_id)
                    doc_id = _json_data_id
                    doc_level = it.get("审判程序")
                    doc_num = it.get("案号")
                    doc_court = it.get("法院名称")
                    doc_reason = it.get("不公开理由")
                    try:
                        task_db.insert_case_detail(
                            (detail_id, "批量处理", doc_id, schema_day, rule_id, '00', doc_level, doc_num, doc_source,
                             doc_reason, doc_type, doc_judge_date, doc_title, doc_court))
                    except IntegrityError:
                        logging.exception("发生了错误 IntegrityError")
                        deal_state = task_db.CASE_PLAN_SCHEMA_DETAIL_03
                    except Exception:
                        deal_state = task_db.CASE_PLAN_SCHEMA_DETAIL_03
                        logging.exception("发生了错误")
                if deal_state != task_db.CASE_PLAN_SCHEMA_DETAIL_03:
                    deal_state = task_db.CASE_PLAN_SCHEMA_DETAIL_10
        except Exception:
            logging.exception("error==>")
        task_db.update_case_plan_schema_detail_state(deal_state, detail_id)


if __name__ == "__main__":
    while True:
        try:
            processor = CaseDetailProcessor()
            processor.proceed()
        except Exception as e:
            logging.exception("发生了错误")
            time.sleep(60)
