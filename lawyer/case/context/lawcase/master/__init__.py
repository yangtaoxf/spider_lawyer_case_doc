
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
