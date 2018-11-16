# coding=utf8
from lawcase.master import redis_local_doc_formatter_master
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )
if __name__ == "__main__":
    while True:
        redis_local_doc_formatter_master(batch_num=1000)
        logging.info("=*= =*=休眠5秒 =*=")
        time.sleep(5)
