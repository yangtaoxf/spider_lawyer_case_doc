# coding=utf-8
import logging
import time

from lawcase.service.process import LawCaseContextProcessor
from lawcase.util.redis_task import RedisLocalDocFormatterMaster
from lawcase.service.pipeline import LocalDocFormatterPipeline
from formatter import DocContextJsParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', filename="case_lawyer_context_starter.log")

if __name__ == '__main__':
    while True:
        data_list = RedisLocalDocFormatterMaster.extract(extract_num=1)
        if not data_list:
            logging.info("=*=没有任务，休眠60秒=*=")
            time.sleep(60)
            continue
        for data in data_list:
            print(data)
            result = DocContextJsParser.parse_convert_html(
                java_script=data["java_script"],
                doc_judge_date=data["json_data_date"],
                doc_title=data["json_data_name"],
                doc_court=data["json_data_court"],
            )
            LocalDocFormatterPipeline.process(result=result, task=data)
