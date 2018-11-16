# coding=utf8
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

if __name__ == "__main__":
    from formatter import DocContextJsParser
    from util.redis_util import RedisCaseDocFormatMaster
    from dao.lawcase import CaseDocDao, CaseDetailDao, CASE_DETAIL_STATE_20, CASE_DETAIL_STATE_19

    while True:
        wait_doc_dict = RedisCaseDocFormatMaster.extract_case_doc_format(extract_num=1)
        if not wait_doc_dict:
            logging.info("RedisCaseDocFormatMaster.extract_case_doc_format 没有任务:等待[***5秒***]")
            time.sleep(5)
            continue
        data = wait_doc_dict.pop()
        parser = DocContextJsParser()
        doc_id = data['doc_id']
        logging.info("format doc_id={}".format(doc_id))
        doc_javascript = data['doc_javascript']
        doc_title = data['doc_title']
        doc_judge_date = data.get('doc_judge_date')
        doc_court = data.get('doc_court')
        exists = data.get("exists")
        result = parser.parse_convert_html(java_script=doc_javascript,
                                           doc_title=doc_title,
                                           doc_judge_date=doc_judge_date,
                                           doc_court=doc_court)
        if result.result:  # 解析成功
            CaseDocDao.insert_into_case_doc(doc_id=doc_id,
                                            # content=result.content,
                                            content="",
                                            html=result.html,
                                            java_script=doc_javascript,
                                            )

            CaseDetailDao.update_case_detail_when_case_doc(state=CASE_DETAIL_STATE_20,
                                                           doc_id=doc_id,
                                                           master_domain=result.master_domain,
                                                           judge_year=result.judge_year,
                                                           province=result.province,
                                                           court_level=result.court_level
                                                           )
        else:
            CaseDetailDao.update_case_detail_when_case_doc(state=CASE_DETAIL_STATE_19,
                                                           doc_id=doc_id,
                                                           remarks=result.msg)
