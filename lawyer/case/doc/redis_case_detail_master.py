# coding=utf8
from doc_master import redis_case_detail_master
import time

if __name__ == "__main__":
    while True:
        redis_case_detail_master(5000)
        time.sleep(5)
