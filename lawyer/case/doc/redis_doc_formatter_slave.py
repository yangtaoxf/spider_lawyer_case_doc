# coding=utf8
import logging
import time

from dao.lawcase import CASE_DETAIL_STATE_20, CASE_DETAIL_STATE_19, BatchCaseDocDao, BatchCaseDetailDao, BatchComplexDao
from doc_formatter import DocContextJsParser
from util.decorator import log_cost_time
from util.redis_util import RedisCaseDocFormatMaster

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


class DTO(object):
    def __init__(self, doc_id, html, doc_javascript, state, master_domain, judge_year, province, court_level, msg,
                 content=""):
        self.doc_id = doc_id
        self.html = html
        self.doc_javascript = doc_javascript
        self.state = state
        self.master_domain = master_domain
        self.judge_year = judge_year
        self.province = province
        self.court_level = court_level
        self.msg = msg
        self.content = content

    def __str__(self):
        return self.doc_id

    def __repr__(self):
        return self.__str__()


class CaseDocFormatService(object):
    @staticmethod
    @log_cost_time("2、批量插入文档")
    def batch_insert_case_doc(success):
        return BatchCaseDocDao.batch_insert_case_doc(success)

    @staticmethod
    @log_cost_time("更新成功的数据")
    def batch_update_case_detail_success_case_doc(success):
        return BatchCaseDetailDao.batch_update_case_detail_success_case_doc(success)

    @staticmethod
    @log_cost_time("更新失败的数据")
    def batch_update_case_detail_fail_case_doc(fail):
        return BatchCaseDetailDao.batch_update_case_detail_fail_case_doc(fail)

    @staticmethod
    @log_cost_time("提取js脚本")
    def extract_doc_javascript(doc_id_list: list):
        return BatchComplexDao.extract_doc_javascript(doc_id_list)


@log_cost_time("*-* 批次 *-*")
def excecute(wait_doc_dict):
    success = []
    fail = []
    doc_id_list = extract_doc_id_list(wait_doc_dict)
    extract_doc_javascript = CaseDocFormatService.extract_doc_javascript(doc_id_list)
    while wait_doc_dict:
        data = wait_doc_dict.pop()
        parser = DocContextJsParser()
        doc_id = data['doc_id']
        logging.info("format doc_id={}".format(doc_id))
        doc_javascript = extract_doc_javascript.get(doc_id)
        doc_title = data['doc_title']
        doc_judge_date = data.get('doc_judge_date')
        doc_court = data.get('doc_court')
        result = parser.parse_convert_html(java_script=doc_javascript,
                                           doc_title=doc_title,
                                           doc_judge_date=doc_judge_date,
                                           doc_court=doc_court)
        if result.result:  # 解析成功
            dto = DTO(
                doc_id=doc_id,
                html=result.html,
                doc_javascript=doc_javascript,
                state=CASE_DETAIL_STATE_20,
                master_domain=result.master_domain,
                judge_year=result.judge_year,
                province=result.province,
                court_level=result.court_level,
                msg=result.msg,
                content=""
            )
            success.append(dto)
        else:
            dto = DTO(
                doc_id=doc_id,
                html=None,
                doc_javascript=None,
                state=CASE_DETAIL_STATE_19,
                master_domain=None,
                judge_year=None,
                province=None,
                court_level=None,
                msg=result.msg,
                content="",
            )
            fail.append(dto)
    if success:
        CaseDocFormatService.batch_insert_case_doc(success)
        CaseDocFormatService.batch_update_case_detail_success_case_doc(success)
    if fail:
        CaseDocFormatService.batch_update_case_detail_fail_case_doc(fail)


def extract_doc_id_list(wait_doc_dict) -> list:
    doc_id_list = []  # 文档id容器
    if wait_doc_dict:
        for data in wait_doc_dict:
            doc_id_list.append(data["doc_id"])
    return doc_id_list


PAUSE_STATE = ""  # 默认


def manager_pause():
    # minute = datetime.datetime.now().minute
    global PAUSE_STATE
    if not PAUSE_STATE:
        logging.info("===开始获取最新PAUSE_STATE的状态====")
        ret = BatchComplexDao.query_system_dict(data_type="spider",
                                                data_key="CASE_DETAIL_FORMAT_MASTER_WHERE_CONDITION_TIME")
        logging.info(ret)
        if ret:
            PAUSE_STATE = ret["state"]
    return PAUSE_STATE == "00"


if __name__ == "__main__":
    while True:
        if manager_pause():
            logging.info("=*= 管理员暂停 等待2分钟再重试 =*=")
            time.sleep(60 * 2)
            continue
        extract_num = 10
        wait_doc_dict = RedisCaseDocFormatMaster.extract_case_doc_format(extract_num=extract_num)
        if not wait_doc_dict:
            logging.info("RedisCaseDocFormatMaster.extract_case_doc_format 没有任务:等待[***5秒***]")
            time.sleep(5)
            continue
        logging.info("---------------begain---------------")
        excecute(wait_doc_dict)
        logging.info("===============end===============")
