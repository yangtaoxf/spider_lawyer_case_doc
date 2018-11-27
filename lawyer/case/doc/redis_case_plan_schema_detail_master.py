# coding=utf8
from doc_master import redis_case_plan_schema_detail_master
import time

if __name__ == "__main__":
    """
    解密文档
    """
    while True:
        redis_case_plan_schema_detail_master(1000)
        time.sleep(5)
