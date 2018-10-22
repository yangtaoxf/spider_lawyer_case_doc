# coding=utf8


import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

if __name__ == "__main__":
    logging.info("master====begin==========")
    from util.redis_util import RedisCasePlanSchemaTaskMaster
    while True:
        try:
            RedisCasePlanSchemaTaskMaster.refresh_case_plan_schema(RedisCasePlanSchemaTaskMaster.KEY, 500)  # 抓取任务队列
        except Exception as e:
            logging.exception("发生错误:->")
        time.sleep(15)
