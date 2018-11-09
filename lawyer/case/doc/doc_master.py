# coding=utf8


import logging
import threading
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def redis_case_plan_schema_task_master(batch_num=500):
    from util.redis_util import RedisCasePlanSchemaTaskMaster
    logging.info("===redis_case_plan_schema_task_master===start===")
    RedisCasePlanSchemaTaskMaster.refresh_case_plan_schema(RedisCasePlanSchemaTaskMaster.KEY, batch_num)  # 抓取任务队列
    logging.info("===redis_case_plan_schema_task_master====end===")


def redis_case_detail_master(batch_num):
    from util.redis_util import RedisCaseDetailMaster
    logging.info("====redis_case_detail_master===start===")
    RedisCaseDetailMaster.init_task_set_push(batch_num)
    logging.info("====redis_case_detail_master====end====")


def redis_case_plan_schema_detail_master(batch_num):
    from util.redis_util import RedisCasePlanSchemaDetailMaster
    logging.info("====redis_case_plan_schema_detail_master===start===")
    RedisCasePlanSchemaDetailMaster.refresh_case_plan_schema_detail(batch_num=batch_num)
    logging.info("====redis_case_plan_schema_detail_master====end====")


def redis_case_doc_format_master(batch_num):
    from util.redis_util import RedisCaseDocFormatMaster
    logging.info("====redis_case_doc_format_master===start===")
    RedisCaseDocFormatMaster.refresh_case_doc_format(batch_num=batch_num)
    logging.info("====redis_case_doc_format_master===start===")


if __name__ == "__main__":
    while True:
        try:
            thread1 = threading.Thread(target=redis_case_detail_master, args=(1500,))
            thread2 = threading.Thread(target=redis_case_plan_schema_task_master, args=(500,))
            thread3 = threading.Thread(target=redis_case_plan_schema_detail_master, args=(1000,))
            thread4 = threading.Thread(target=redis_case_doc_format_master, args=(1000,))
            thread1.start()
            thread2.start()
            thread3.start()
            thread4.start()
            thread1.join()
            thread2.join()
            thread3.join()
            thread4.join()
        except Exception as e:
            logging.exception("发生错误:->")
        time.sleep(5)
