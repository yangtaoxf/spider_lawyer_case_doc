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

from lawcase.service.pipeline import SyncCaseLawyerDocPipeline
from lawcase.util.redis_task import RedisSyncCaseLawyerDocMaster

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

if __name__ == '__main__':
    while True:
        data_list = RedisSyncCaseLawyerDocMaster.extract(extract_num=1)
        if not data_list:
            logging.info("=*=没有任务，休眠60秒=*=")
            time.sleep(60)
            continue
        for data in data_list:
            SyncCaseLawyerDocPipeline.sync(lawyer_id=data["lawyer_id"],
                                           doc_id=data["doc_id"],
                                           html=data["html"],
                                           caseType=data["master_domain"],
                                           casenum=data["json_data_number"],
                                           title=data["json_data_name"],
                                           court=data["json_data_court"],
                                           )
