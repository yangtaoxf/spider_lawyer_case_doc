# coding=utf8
import json
import logging
import time

from pymysql.err import IntegrityError

import law_case_db as task_db
from dao.lawcase import BatchCaseDetailDao
from util import decrypt_id, decrypt_id_array
from util.decorator import log_cost_time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


class ProcessorItemResult(object):
    """
    解析明细结果
    """
    CODE_03 = "03"  # 解析异常
    CODE_09 = "09"  # 解析出现失败
    CODE_10 = "10"  # 解析成功

    def __init__(self, detail_id):
        """
        :param doc_type:案件类型
        :param doc_judge_date:裁判日期
        :param doc_title:案件名称
        :param doc_id:文书ID
        :param doc_level:审判程序
        :param doc_num:案号
        :param doc_court:法院名称
        :param doc_reason:不公开理由
        :param code:初始化为:CODE_03-解析异常
        :param detail_id:解析文档id
        """
        self.doc_type = None
        self.doc_judge_date = None
        self.doc_title = None
        self.doc_id = None
        self.doc_level = None
        self.doc_num = None
        self.doc_court = None
        self.doc_reason = None
        self.schema_day = None
        self.rule_id = None
        self.encrypt_doc_id = None
        self.detail_id = detail_id
        self.code = self.CODE_03

    @staticmethod
    def build(doc_type=None, doc_judge_date=None, doc_title=None, schema_day=None, detail_id=None, rule_id=None,
              doc_id=None, doc_level=None, doc_num=None, doc_court=None, doc_reason=None, code=None,
              encrypt_doc_id=None):
        ret = ProcessorItemResult(detail_id=detail_id)
        ret.doc_type = doc_type
        ret.doc_judge_date = doc_judge_date
        ret.doc_title = doc_title
        ret.doc_id = doc_id
        ret.doc_level = doc_level
        ret.doc_num = doc_num
        ret.doc_court = doc_court
        ret.doc_reason = doc_reason
        ret.code = code
        ret.schema_day = schema_day
        ret.rule_id = rule_id
        ret.encrypt_doc_id = encrypt_doc_id
        return ret

    def success(self):
        return self.code == self.CODE_10

    def __str__(self):
        return self.doc_id

    def __repr__(self):
        return self.__str__()


class ProcessorBatchResult(object):
    """
    解析批次结果
    """
    CODE_03 = "03"  # 解析异常
    CODE_09 = "09"  # 解析出现失败
    CODE_10 = "10"  # 解析成功

    def __init__(self, detail_id, code=CODE_03):
        self.detail_id = detail_id
        self.code = code

    def success(self):
        return self.code == self.CODE_10

    def fail(self):
        return self.code == self.CODE_09

    def set_code(self, code):
        self.code = code

    def __str__(self):
        return self.detail_id

    def __repr__(self):
        return self.__str__()


class Result(object):

    def __init__(self, batch_result: ProcessorBatchResult, success_list: list):
        self.batch_result = batch_result
        self.success_list = success_list


class CaseDetailProcessor(object):
    """
    获取案例抓取计划
    """

    @staticmethod
    @log_cost_time(describe="-*- 批次执行 -*-")
    def proceed(case_plan_schema_detail_dict) -> Result:
        detail_id = case_plan_schema_detail_dict["detail_id"]
        schema_day = case_plan_schema_detail_dict["schema_day"]
        rule_id = case_plan_schema_detail_dict["rule_id"]
        json_text = case_plan_schema_detail_dict["json_text"]
        logging.info("detail_id=" + detail_id + ";schema_day=" + schema_day)
        batch_result = ProcessorBatchResult(detail_id=detail_id)
        success_list = []
        encrypt_doc_id_list = []  # key:解密前id
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
                    try:
                        doc_type = it.get("案件类型")
                        doc_judge_date = it.get("裁判日期")
                        doc_title = it.get("案件名称")
                        encrypt_doc_id = it.get("文书ID")

                        # _json_data_id = decrypt_id(run_eval, it.get("文书ID"))
                        doc_level = it.get("审判程序")
                        doc_num = it.get("案号")
                        doc_court = it.get("法院名称")
                        doc_reason = it.get("不公开理由")
                        encrypt_doc_id_list.append(it.get("文书ID"))
                        success = ProcessorItemResult.build(
                            doc_type=doc_type,
                            doc_judge_date=doc_judge_date,
                            doc_title=doc_title,
                            doc_level=doc_level,
                            doc_num=doc_num,
                            doc_court=doc_court,
                            doc_reason=doc_reason,
                            code=ProcessorItemResult.CODE_10,
                            detail_id=detail_id,
                            schema_day=schema_day,
                            rule_id=rule_id,
                            encrypt_doc_id=encrypt_doc_id
                        )
                        success_list.append(success)
                    except IntegrityError:
                        logging.exception("发生了错误 IntegrityError")
                    except Exception:
                        batch_result.set_code(ProcessorBatchResult.CODE_09)
                        logging.exception("发生了错误")
                # 批量解密文档id
                doc_id_dict = decrypt_id_array(run_eval, encrypt_doc_id_list)
                for __sucess in success_list:
                    __sucess.doc_id = doc_id_dict.get(__sucess.encrypt_doc_id)
                logging.info(success_list)
                if not batch_result.fail():  # 没有失败,更新为批次成功
                    batch_result.set_code(ProcessorBatchResult.CODE_10)
        except Exception:
            batch_result.set_code(ProcessorBatchResult.CODE_09)
            logging.exception("error==>")
        finally:
            return Result(batch_result, success_list)

    @staticmethod
    def call_back(batch_result: ProcessorBatchResult, success_list: list):
        if list:
            DecryptDocService.proceed_success_list(success_list)
        if batch_result:
            DecryptDocService.proceed_batch_result(batch_result)


class DecryptDocService(object):
    @staticmethod
    @log_cost_time(describe="更新解析结果")
    def proceed_batch_result(batch_result: ProcessorBatchResult):
        task_db.update_case_plan_schema_detail_state(batch_result.code, batch_result.detail_id)

    @staticmethod
    @log_cost_time(describe="批量插入解析成功数据")
    def proceed_success_list(success_list: list):
        BatchCaseDetailDao.batch_insert_case_detail(success_list)


if __name__ == "__main__":
    from util.redis_util import RedisCasePlanSchemaDetailMaster

    while True:
        try:
            logging.info("==============start================")
            case_plan_schema_detail_dict = RedisCasePlanSchemaDetailMaster.extract_case_plan_schema_detail(
                extract_num=1)
            if not case_plan_schema_detail_dict:
                logging.info("---没有任务,休眠5秒---")
                time.sleep(5)
                continue
            ret = CaseDetailProcessor.proceed(case_plan_schema_detail_dict.pop())
            CaseDetailProcessor.call_back(batch_result=ret.batch_result, success_list=ret.success_list)
            logging.info("===============end=================")
        except Exception as e:
            logging.exception("发生了错误")
            time.sleep(60)