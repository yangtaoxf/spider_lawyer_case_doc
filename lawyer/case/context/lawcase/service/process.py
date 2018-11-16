# coding=utf-8
import json
import logging
import time
import os
import sys

current_Path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_Path)[0]
sys.path.append(root_path)
from pymysql.err import IntegrityError
from util import decrypt_id
from lawcase.dao import CaseLawyerDocDao, CaseLawyerContextDao
from lawcase.bean import CaseLawyerContextBean


class LawCaseContextProcessor(object):
    """
    获取案例抓取计划
    """

    # def __init__(self, bean):
    #     self.context_bean = bean

    @staticmethod
    def proceed(context_bean):
        if not context_bean:
            logging.warning("=*= LawCaseContextProcessor proceed没有数据,休眠 5秒 =*=")
            time.sleep(5)
            return
        assert isinstance(context_bean, CaseLawyerContextBean)

        spider_id = context_bean.id
        lawyer_id = context_bean.lawyer_id
        json_text = context_bean.page_json
        logging.info("spider_id={} lawyer_id={} bean={}".format(spider_id, lawyer_id, str(context_bean)))
        try:
            if "RunEval" in json_text:
                if '"[{\\' in json_text:
                    page_data = json.loads(json_text.replace('\\"', '\"')[1:-1])  # 转移字符
                else:
                    page_data = json.loads(json_text)
                run_eval = None
                batch_count = 0
                for it in page_data:
                    if it.get("RunEval") is not None:
                        run_eval = it.get("RunEval")
                        if it.get("Count") is not None:
                            batch_count = it.get("Count")
                        continue
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
                    args = (
                        doc_id, spider_id, lawyer_id, batch_count, doc_type, doc_judge_date,
                        doc_title, doc_level, doc_num, doc_court,
                    )
                    try:
                        CaseLawyerDocDao.insert(args)
                    except IntegrityError:
                        logging.exception("发生了错误 IntegrityError")
                    except Exception:
                        context_bean.status = CaseLawyerContextBean.STATUS_09
                        logging.exception("发生了错误")
                if context_bean.status == CaseLawyerContextBean.STATUS_01:
                    context_bean.status = CaseLawyerContextBean.STATUS_10
        except Exception:
            logging.exception("=*= 严重未知错误 =*=")
            context_bean.status = CaseLawyerContextBean.STATUS_09
        finally:
            CaseLawyerContextDao.update_state(state=context_bean.status, _id=context_bean.id)

    def __str__(self):
        return "[LawCaseContextProcessor context_bean]=*= {}".format(str(self.context_bean))

    def __repr__(self):
        return self.__str__()
