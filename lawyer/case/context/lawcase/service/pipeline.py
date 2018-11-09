# coding=utf8
from formatter import Result
from lawcase.dao import CaseLawyerDocDao
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
