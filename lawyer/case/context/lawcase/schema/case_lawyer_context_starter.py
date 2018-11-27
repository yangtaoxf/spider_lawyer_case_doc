# coding=utf-8
# ------------------添加root_path
import os
import sys

current_Path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_Path)[0]
__root_path = root_path.split(sep="context")[0]
__root_path_1 = __root_path + "context" + os.sep
__root_path_2 = __root_path + "doc" + os.sep
print(__root_path_1, "========", __root_path_2)
sys.path.append(__root_path_1)
sys.path.append(__root_path_2)
# ------------------
import logging
import time
from lawcase.service.process import LawCaseContextProcessor
from lawcase.util.redis_task import RedisCaseLawyerContextMasterHelper
from multiprocessing import cpu_count, Pool

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', filename="case_lawyer_context_starter.log")

if __name__ == '__main__':
    # __cpu_count = cpu_count()
    while True:
        # logging.info("=*= 系统cpu个数是:" + str(__cpu_count))
        bean_list = RedisCaseLawyerContextMasterHelper.extract_case_lawyer_context(extract_num=1)
        if not bean_list:
            logging.info("=*=没有任务，休眠60秒=*=")
            time.sleep(60)
            continue
        logging.info("=*= batch proceed begain =*=")
        pool = Pool(1)
        for data in bean_list:
            bean = RedisCaseLawyerContextMasterHelper.wrapper(data=data)
            pool.apply_async(LawCaseContextProcessor.proceed, args=(bean,))
        pool.close()
        pool.join()
        logging.info("=*= batch proceed end =*=")
