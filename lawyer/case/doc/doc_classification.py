import logging

import db
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

ads_field = db.extract_ads_field()
ads_field_key = db.extract_ads_fieldkey()


def proceed_pending_doc():
    """
    处理重新分类的doc文档
    :return:
    """
    docs = db.extract_pending_doc()
    for doc in docs:
        ret_field_code = '239'  # 默认其他
        doc_id = doc.get("id")
        lawyer_id = doc.get("lawyer_id")
        title = doc.get("title")
        logging.info('开始分类文档id=%s;所属律师id=%s;文档标题为title:%s' % (doc_id, lawyer_id, title))
        match = False
        for it in ads_field_key:
            keyword = it['keyword']
            field_code = it['fieldCode']
            if title is not None and keyword in title:
                logging.info('标题匹配成功 field_code=%s;keyword=%s;title=%s' % (field_code, keyword, title,))
                ret_field_code = field_code
                match = True
                break
        if not match:
            logging.info("没有匹配到关键字，归类到“其他”.")
        db.update_pending_doc(doc_id=doc_id, case_type=ret_field_code)
    time.sleep(1)
    return len(docs)


def match_field_code(doc_id, lawyer_id, title):
    """
    匹配擅长领域
    :param title: 标题
    :param doc_id: 文档id
    :param lawyer_id: 律师id
    :return:
    """
    logging.info('开始分类文档id=%s;所属律师id=%s;文档标题为title:%s' % (doc_id, lawyer_id, title))
    match = False
    for it in ads_field_key:
        keyword = it['keyword']
        field_code = it['fieldCode']
        if title is not None and keyword in title:
            logging.info('标题匹配成功 field_code=%s;keyword=%s;title=%s' % (field_code, keyword, title,))
            ret_field_code = field_code
            match = True
            break
    if not match:
        ret_field_code = "239"
        logging.info("没有匹配到关键字，归类到“其他”.")
    return ret_field_code


# while True:
#     length = proceed_pending_doc()
#     if length == 0:
#         break
#     time.sleep(1)
