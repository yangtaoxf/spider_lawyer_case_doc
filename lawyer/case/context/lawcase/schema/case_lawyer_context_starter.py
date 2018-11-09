# coding=utf-8
import logging
import time

from lawcase.service.process import LawCaseContextProcessor
from lawcase.util.redis_task import RedisCaseLawyerContextMasterHelper

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', filename="case_lawyer_context_starter.log")

if __name__ == '__main__':
    while True:
        bean_list = RedisCaseLawyerContextMasterHelper.extract_case_lawyer_context(extract_num=1)
        if not bean_list:
            logging.info("=*=没有任务，休眠60秒=*=")
            time.sleep(60)
            continue
        for data in bean_list:
            bean = RedisCaseLawyerContextMasterHelper.wrapper(data=data)
            LawCaseContextProcessor(bean=bean).proceed()
