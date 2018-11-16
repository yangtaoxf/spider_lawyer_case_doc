# coding=utf-8
import ast
import logging

import redis

from lawcase.bean import LawyerInfoBean, CaseLawyerContextBean, CaseLawyerDocBean
from lawcase.config import TABLE_NAME_SUFFIX

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )
conn_pool = redis.ConnectionPool(host='120.76.138.153', port=6379, password="duowenlvshi~6379")
redis_client = redis.Redis(connection_pool=conn_pool)


# ----------------------------------------------------------------------
class RedisCaseLawyerTaskMaster(object):
    KEY = "case_lawyer" + TABLE_NAME_SUFFIX
    logging.info(
        "===[RedisCaseLawyerTaskMaster TABLE_NAME_SUFFIX is *{}* KEY is *{}*]===".format(TABLE_NAME_SUFFIX, KEY))

    @staticmethod
    def refresh_case_lawyer(key=KEY, batch_num=500):
        __size = redis_client.scard(key)
        print(key)
        logging.info("已经存在任务条数==>：" + str(__size))
        if __size >= batch_num:
            logging.info("存在条数大于==>" + str(batch_num) + "不新增任务；")
            return
        from lawcase.dao import CaseLawyerDao
        _ret = CaseLawyerDao.extract(batch_num=batch_num)
        for data in _ret:
            _data = str(data)
            redis_client.sadd(key, _data)
        logging.info("=*=refresh_case_lawyer after size is==>" + str(redis_client.scard(key)))
        logging.info("=*=refresh_case_lawyer=*= [OK]")

    @staticmethod
    def extract_case_lawyer(key=KEY, extract_num=50) -> list:
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret


class RedisCaseLawyerTaskMasterHelper(RedisCaseLawyerTaskMaster):
    """
    在Python中静态方法可以被继承
    注意和Java的区别
    """

    @staticmethod
    def extract_lawyer_info_bean_list(key=RedisCaseLawyerTaskMaster.KEY, extract_num=50) -> list:
        logging.info("=*= 添加新的律师待爬取案例队列 ===开始=*= ")
        _ret = []
        data_list = RedisCaseLawyerTaskMasterHelper.extract_case_lawyer(key=key, extract_num=extract_num)
        for data in data_list:
            if data:
                bean = LawyerInfoBean(lawyer_id=data["id"],
                                      lawyer_name=data["realname"],
                                      law_firm=data["office"],
                                      phone=data["phone"],
                                      process=data["process"],
                                      page_index=data["pageindex"],
                                      page=data["page"],
                                      )
                logging.info(bean)
                _ret.append(bean)
            else:
                break
        logging.info("=*= 添加新的律师待爬取案例队列 ===结束=*= ")
        return _ret


# ----------------------------------------------------------------------
class RedisCaseLawyerContextMaster(object):
    KEY = "case_lawyer_context" + TABLE_NAME_SUFFIX
    logging.info(
        "===[RedisCaseLawyerContextMaster TABLE_NAME_SUFFIX is *{}* KEY is *{}*]===".format(TABLE_NAME_SUFFIX, KEY))

    @staticmethod
    def refresh_case_lawyer_context(key=KEY, batch_num=500):
        __size = redis_client.scard(key)
        logging.info("已经存在任务条数==>：" + str(__size))
        if __size >= batch_num:
            logging.info("存在条数大于==>" + str(batch_num) + "不新增任务；")
            return
        from lawcase.dao import CaseLawyerContextDao
        _ret = CaseLawyerContextDao.extract(batch_num=batch_num)
        for data in _ret:
            _data = str({
                "id": data["id"],
                "lawyer_id": data["lawyer_id"],
                "json_batch_count": data["json_batch_count"],
                "page_json": data["page_json"],
                "index": data["index"],
                "pageNum": data["pageNum"],
                "status": data["status"],
            })
            redis_client.sadd(key, _data)
        logging.info("=*=refresh_case_lawyer_context after size =*= " + str(redis_client.scard(key)))
        logging.info("=*=refresh_case_lawyer_context === OK =*=")

    @staticmethod
    def extract_case_lawyer_context(key=KEY, extract_num=50) -> list:
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret


class RedisCaseLawyerContextMasterHelper(RedisCaseLawyerContextMaster):

    @staticmethod
    def wrapper(data) -> CaseLawyerContextBean:
        """
        包装实体bean
        :return:
        """
        ret = None
        if data:
            ret = CaseLawyerContextBean(id=data["id"],
                                        lawyer_id=data["lawyer_id"],
                                        json_batch_count=data["json_batch_count"],
                                        page_json=data["page_json"],
                                        index=data["index"],
                                        page_num=data["pageNum"],
                                        status=data["status"]
                                        )
        return ret


# ----------------------------------------------------------------------

class RedisCaseLawyerDocMaster(object):
    KEY = "case_lawyer_doc" + TABLE_NAME_SUFFIX
    logging.info(
        "===[RedisCaseLawyerDocMaster TABLE_NAME_SUFFIX is *{}* KEY is *{}*]===".format(TABLE_NAME_SUFFIX, KEY))

    @staticmethod
    def refresh(key=KEY, batch_num=500):
        __size = redis_client.scard(key)
        logging.info("已经存在任务条数==>：" + str(__size))
        if __size >= batch_num:
            logging.info("存在条数大于==>" + str(batch_num) + "不新增任务；")
            return
        from lawcase.dao import CaseLawyerDocDao
        _ret = CaseLawyerDocDao.extract(batch_num=batch_num)
        for data in _ret:
            _data = str({
                "doc_id": data["doc_id"],
                "spider_id": data["spider_id"],
                "lawyer_id": data["lawyer_id"],
                "sync_status": data["sync_status"],
            })
            redis_client.sadd(key, _data)
        logging.info("=*=RedisCaseLawyerDocMaster refresh after size =*= " + str(redis_client.scard(key)))
        logging.info("=*=RedisCaseLawyerDocMaster refresh === OK =*=")

    @staticmethod
    def extract(key=KEY, extract_num=50) -> list:
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret

    @staticmethod
    def wrapper(data) -> CaseLawyerDocBean:
        """
        包装实体bean
        :return:
        """
        ret = []

        """
                self.doc_id = doc_id
        self.lawyer_id = lawyer_id
        self.spider_id = spider_id
        self.sync_status = self.sync_status
        """
        if data:
            ret.append(CaseLawyerDocBean(doc_id=data["doc_id"],
                                         lawyer_id=data["lawyer_id"],
                                         spider_id=data["spider_id"],
                                         sync_status=data["sync_status"],
                                         ))
        return ret


# ----------------------------------------------------------------------
class RedisLocalDocFormatterMaster(object):
    KEY = "local_doc_formatter" + TABLE_NAME_SUFFIX
    logging.info(
        "===[RedisLocalDocFormatterMaster TABLE_NAME_SUFFIX is *{}* KEY is *{}*]===".format(TABLE_NAME_SUFFIX, KEY))

    @staticmethod
    def refresh(key=KEY, batch_num=500):
        __size = redis_client.scard(key)
        logging.info("已经存在任务条数==>：" + str(__size))
        if __size >= batch_num:
            logging.info("存在条数大于==>" + str(batch_num) + "不新增任务；")
            return
        from lawcase.dao import CaseLawyerDocDao
        _ret = CaseLawyerDocDao.formatter_extract(batch_num=batch_num)
        for data in _ret:
            _data = str({
                "doc_id": data["doc_id"],
                "spider_id": data["spider_id"],
                "lawyer_id": data["lawyer_id"],
                "sync_status": data["sync_status"],
                "java_script": data["java_script"],
                "json_data_name": data["json_data_name"],
                "json_data_date": data["json_data_date"],
                "json_data_court": data["json_data_court"],
            })
            redis_client.sadd(key, _data)
        logging.info("=*=RedisLocalDocFormatterMaster refresh after size =*= " + str(redis_client.scard(key)))
        logging.info("=*=RedisLocalDocFormatterMaster refresh === OK =*=")

    @staticmethod
    def extract(key=KEY, extract_num=50) -> list:
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret


# ----------------------------------------------------------------------
class RedisSyncCaseLawyerDocMaster(object):
    """
    同步已经下载的文档
    """
    KEY = "sync_case_lawyer_doc" + TABLE_NAME_SUFFIX
    logging.info(
        "===[RedisSyncCaseLawyerDocMaster TABLE_NAME_SUFFIX is *{}* KEY is *{}*]===".format(TABLE_NAME_SUFFIX, KEY))

    @staticmethod
    def refresh(key=KEY, batch_num=500):
        __size = redis_client.scard(key)
        logging.info("已经存在任务条数==>：" + str(__size))
        if __size >= batch_num:
            logging.info("存在条数大于==>" + str(batch_num) + "不新增任务；")
            return
        from lawcase.dao import CaseLawyerDocDao
        _ret = CaseLawyerDocDao.sync_doc_extract(batch_num=batch_num)
        for data in _ret:
            _data = str({
                "doc_id": data["doc_id"],
                "lawyer_id": data["lawyer_id"],
                "json_data_type": data["json_data_type"],
                "json_data_date": data["json_data_date"],
                "json_data_name": data["json_data_name"],
                "json_data_level": data["json_data_level"],
                "json_data_number": data["json_data_number"],
                "json_data_court": data["json_data_court"],
                "html": data["html"],
                "sync_status": data["sync_status"],
                "master_domain": data["master_domain"],
                "spider_id": data["spider_id"],
            })
            redis_client.sadd(key, _data)
        logging.info("=*=RedisSyncCaseLawyerDocMaster refresh after size =*= " + str(redis_client.scard(key)))
        logging.info("=*=RedisSyncCaseLawyerDocMaster refresh === OK =*=")

    @staticmethod
    def extract(key=KEY, extract_num=50) -> list:
        _ret = []
        for _ in range(extract_num):
            data = redis_client.spop(key)
            if data:
                _ret.append(ast.literal_eval(data.decode("utf-8")))
            else:
                break
        return _ret
