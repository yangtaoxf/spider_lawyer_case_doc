# coding=utf8
from doc_master import redis_case_doc_format_master
import time

if __name__ == "__main__":
    while True:
        redis_case_doc_format_master(2000)
        time.sleep(5)
