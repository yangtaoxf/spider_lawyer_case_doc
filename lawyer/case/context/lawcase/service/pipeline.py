# coding=utf8
from formatter import Result
from lawcase.dao import CaseLawyerDocDao, LawyerCaseDao, CaseLawyerDocDao
from lawcase.config import DOC_VERSION
from lawcase.bean import CaseLawyerDocBean
import logging


class LocalDocFormatterPipeline(object):

    @staticmethod
    def process(result, task):
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
    def sync(lawyer_id, doc_id, html, caseType, casenum, title, court):
        logging.info("=*= 开始同步文档数据 doc_id={}=*=".format(doc_id))
        exist = LawyerCaseDao.exist(lawyer_id, doc_id)
        if exist:
            __id = exist.pop()["id"]
            logging.info("=*= 更新文档数据" + str(exist))
            LawyerCaseDao.update_by_id(id=__id, html=html)
        else:
            logging.info("=*= 新增文档数据" + str(exist))
            LawyerCaseDao.insert(lawyer_id, doc_id, html, caseType, casenum, title, court)
        # 更新同步成功
        SyncCaseLawyerDocPipeline.success(lawyer_id, doc_id)

    @staticmethod
    def success(lawyer_id, doc_id):
        logging.info("=*= 同步文档数据 成功 doc_id={}=*=".format(doc_id))
        CaseLawyerDocDao.sync_update_sync_status(doc_id=doc_id,
                                                 lawyer_id=lawyer_id,
                                                 status=CaseLawyerDocBean.SYNC_STATUS_30)
