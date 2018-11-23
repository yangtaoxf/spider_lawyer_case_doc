# coding=utf8

from lawcase.dao import CaseLawyerDocDao, LawyerCaseDao, CaseLawyerDocDao
from lawcase.config import DOC_VERSION
from lawcase.bean import CaseLawyerDocBean
from util.decorator import log_cost_time
import logging


class LocalDocFormatterPipeline(object):

    @staticmethod
    def process(result, task):
        from doc_formatter import Result
        assert isinstance(result, Result)
        assert isinstance(task, dict)
        logging.info(result)
        if result.result:  # 成功
            CaseLawyerDocDao.formatter_update(doc_id=task["doc_id"],
                                              html=result.html,
                                              master_domain=result.master_domain,
                                              sync_status=CaseLawyerDocBean.SYNC_STATUS_20)
        else:  # 失败
            CaseLawyerDocDao.formatter_update(doc_id=task["doc_id"],
                                              remark=result.msg,
                                              sync_status=CaseLawyerDocBean.SYNC_STATUS_19)


class SyncCaseLawyerDocPipeline(object):

    @staticmethod
    @log_cost_time(describe="*** 1、 同步任务节点 ***")
    def sync(lawyer_id, doc_id, html, caseType, casenum, title, court):
        logging.info("=*= 开始同步文档数据 doc_id={} =*=".format(doc_id))
        exist = SyncCaseLawyerDocPipeline.exist(lawyer_id, doc_id)
        if exist:
            __id = exist.pop()["id"]
            SyncCaseLawyerDocPipeline.update_by_id(id=__id, html=html)
        else:
            SyncCaseLawyerDocPipeline.insert(lawyer_id, doc_id, html, caseType, casenum, title, court)
        # 更新同步成功
        SyncCaseLawyerDocPipeline.success(lawyer_id, doc_id)

    @staticmethod
    @log_cost_time(describe="1.3 数据库同步")
    def success(lawyer_id, doc_id):
        CaseLawyerDocDao.sync_update_sync_status(doc_id=doc_id,
                                                 lawyer_id=lawyer_id,
                                                 status=CaseLawyerDocBean.SYNC_STATUS_30)

    @staticmethod
    @log_cost_time(describe="1.1 判断文档是否存在")
    def exist(lawyer_id, doc_id):
        return LawyerCaseDao.exist(lawyer_id, doc_id)

    @staticmethod
    @log_cost_time(describe="1.2 更新存在的文档")
    def update_by_id(id, html):
        return LawyerCaseDao.update_by_id(id, html)

    @staticmethod
    @log_cost_time(describe="1.2 插入新文档")
    def insert(lawyer_id, doc_id, html, caseType, casenum, title, court):
        return LawyerCaseDao.insert(lawyer_id, doc_id, html, caseType, casenum, title, court)
