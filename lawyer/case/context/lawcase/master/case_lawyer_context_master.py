# coding=utf-8
from lawcase.master import redis_case_lawyer_context_task_master
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )
if __name__ == "__main__":
    redis_case_lawyer_context_task_master(batch_num=10)
