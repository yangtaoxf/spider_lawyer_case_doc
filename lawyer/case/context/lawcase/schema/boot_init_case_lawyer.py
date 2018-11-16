# coding=utf-8
# 每周定时刷新需要处理的律师信息
# ------------------添加root_path
import os
import sys
import logging
import time

current_Path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_Path)[0]
__root_path = root_path.split(sep="context")[0]
__root_path_1 = __root_path + "context" + os.sep
__root_path_2 = __root_path + "doc" + os.sep
print(__root_path_1, "========", __root_path_2)
sys.path.append(__root_path_1)
sys.path.append(__root_path_2)
# ------------------
from lawcase.dao import CaseLawyerDao

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', filename="case_lawyer_context_starter.log")

if __name__ == "__main__":
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    remark = "新增批次日期{}".format(date)
    logging.info("=*= boot_init_case_lawyer remark is[{}]=*=".format(remark))
    sql = """
    INSERT INTO case_lawyer_2018_11 (id,office,phone,realname,remark)
        SELECT c.id,c.law_firm,c.phone,c.real_name,'{}'
        FROM lawyer c where status = 4 and not exists(select 1 from case_lawyer_2018_11 d where c.id=d.id);
    """.format(remark)
    CaseLawyerDao.execute_sql(sql, ())
