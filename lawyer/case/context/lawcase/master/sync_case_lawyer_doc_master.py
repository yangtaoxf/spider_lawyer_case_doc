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
from lawcase.master import redis_sync_case_lawyer_doc_master
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )
if __name__ == "__main__":
    while True:
        redis_sync_case_lawyer_doc_master(batch_num=50)
        logging.info("=*= 休眠5秒 =*=")
        time.sleep(5)
