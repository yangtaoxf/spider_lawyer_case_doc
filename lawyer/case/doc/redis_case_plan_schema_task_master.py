# coding=utf8
from doc_master import redis_case_plan_schema_task_master
import time

if __name__ == "__main__":
    while True:
        redis_case_plan_schema_task_master(500)
        time.sleep(5)
