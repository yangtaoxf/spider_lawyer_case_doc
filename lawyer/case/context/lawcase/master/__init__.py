import os
import sys


def init_sys_path():
    # ------------------添加root_path
    current_Path = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.split(current_Path)[0]
    __root_path = root_path.split(sep="context")[0]
    __root_path_1 = __root_path + "context" + os.sep
    __root_path_2 = __root_path + "doc" + os.sep
    print(__root_path_1, "========", __root_path_2)
    sys.path.append(__root_path_1)
    sys.path.append(__root_path_2)
    # ------------------


init_sys_path()

import logging


def redis_case_lawyer_task_master(batch_num):
    from lawcase.util.redis_task import RedisCaseLawyerTaskMaster
    logging.info("=*=duowen库=*=redis_case_lawyer_task_master===start===")
    RedisCaseLawyerTaskMaster.refresh_case_lawyer(batch_num=batch_num)
    logging.info("=*=duowen库=*=redis_case_lawyer_task_master====end====")


def redis_case_lawyer_context_task_master(batch_num):
    from lawcase.util.redis_task import RedisCaseLawyerContextMaster
    logging.info("=*=duowen库=*=redis_case_lawyer_context_task_master===start===")
    RedisCaseLawyerContextMaster.refresh_case_lawyer_context(batch_num=batch_num)
    logging.info("=*=duowen库=*=redis_case_lawyer_context_task_master====end====")


def redis_case_lawyer_doc_task_master(batch_num):
    from lawcase.util.redis_task import RedisCaseLawyerDocMaster
    logging.info("=*=duowen库=*=redis_case_lawyer_doc_task_master===start===")
    RedisCaseLawyerDocMaster.refresh(batch_num=batch_num)
    logging.info("=*=duowen库=*=redis_case_lawyer_doc_task_master====end====")


def redis_local_doc_formatter_master(batch_num):
    from lawcase.util.redis_task import RedisLocalDocFormatterMaster
    logging.info("=*=duowen库=*=redis_case_lawyer_doc_task_master===start===")
    RedisLocalDocFormatterMaster.refresh(batch_num=batch_num)
    logging.info("=*=duowen库=*=redis_case_lawyer_doc_task_master====end====")


def redis_sync_case_lawyer_doc_master(batch_num):
    from lawcase.util.redis_task import RedisSyncCaseLawyerDocMaster
    logging.info("=*=duowen库=*=redis_sync_case_lawyer_doc_master===start===")
    RedisSyncCaseLawyerDocMaster.refresh(batch_num=batch_num)
    logging.info("=*=duowen库=*=redis_sync_case_lawyer_doc_master====end====")
