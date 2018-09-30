import logging
import config
import dbtools.helper as db_helper

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def get_case_lawyer_schema():
    global row
    sub_order = config.case_lawyer_schema_order_by_sql
    try:
        sql = '''SELECT lawyer_id,json_data_id,json_data_name from case_lawyer_schema where beautiful_html_status={} {} limit 1'''.format(
            BEAUTIFUL_HTML_STATUS_00, sub_order)
        row = db_helper.fetch_one(sql)
    except Exception as e:
        logging.error(e)
    finally:
        logging.info(row)
    return row


# 未解析
BEAUTIFUL_HTML_STATUS_00 = '00'
# 下载失败
BEAUTIFUL_HTML_STATUS_09 = '09'
# 已经解析
BEAUTIFUL_HTML_STATUS_10 = '10'


# 保存html页面
def update_case_lawyer_schema(doc_id, case_type, html_view, html_source_js):
    try:
        sql = '''UPDATE case_lawyer_schema SET beautiful_html_status=%s,beautiful_html_view=%s,beautiful_case_type=%s,beautiful_html_source_js=%s where json_data_id=%s'''
        db_helper.update(sql, (BEAUTIFUL_HTML_STATUS_10, html_view, case_type, html_source_js, doc_id,))
    except Exception as e:
        logging.error(e)


# 失败时更新
def update_fail_case_lawyer_schema(doc_id):
    try:
        sql = '''UPDATE case_lawyer_schema SET beautiful_html_status={} where json_data_id=%s'''.format(
            BEAUTIFUL_HTML_STATUS_09)
        db_helper.update(sql, (doc_id,))
    except Exception as e:
        logging.error(e)


# 定义版本号
global SOURCEFROM
SOURCEFROM = 'CPWSWXB_201808_PYTHON'


def update_lawyercase(detail={}):
    match = False
    lawyer_id = detail.get("lawyer_id")
    caseType = detail.get("beautiful_case_type")
    content = detail.get("beautiful_html_view")
    sourceId = detail.get("json_data_id")
    sql = '''SELECT `id`,lawyer_id,sourceFrom from lawyerCase where lawyer_id=%s and sourceId=%s limit 1'''
    row = db_helper.fetch_one(sql, (lawyer_id, sourceId,))
    if row is None:
        return match
    match = True
    row = db_helper.update(
        '''UPDATE lawyerCase SET sourceFrom=%s,caseType=%s,content=%s  where lawyer_id=%s and sourceId=%s''',
        (SOURCEFROM, caseType, content, lawyer_id, sourceId,))
    logging.info("已经更新" + str(row) + str(detail))
    return match


SYNC_STATUS_10 = '10'
SYNC_STATUS_20 = '20'


def update_case_lawyer_schema_on_detail_sucess(detail={}):
    if detail is None:
        return
    id = detail.get("id")
    try:
        sql = '''UPDATE case_lawyer_schema SET sync_status=%s where `id`=%s'''
        row = db_helper.update(sql, (SYNC_STATUS_20, id,))
        logging.info(str(row))
    except Exception as e:
        logging.exception("error.")


def insert_or_update_lawyercase(detail={}):
    if detail is None:
        return
    if update_lawyercase(detail):
        pass
    else:
        template_sql = '''INSERT INTO `lawyercase`
            (`id`,
             `caseType`,
             `casenum`,
             `content`,
             `title`,
             `lawyer_id`, 
             `court`,
             `createDate`,
             `views`,
             `sourceFrom`,
             `sourceId`
              )  VALUES (%s, %s, %s, %s, %s, %s, %s, now(), 0, %s, %s)'''
        id = detail.get("id");
        caseType = detail.get("beautiful_case_type")
        casenum = detail.get("json_data_number")
        content = detail.get("beautiful_html_view")
        title = detail.get("json_data_name")
        lawyer_id = detail.get("lawyer_id")
        court = detail.get("json_data_court")
        sourceFrom = 'CPWSWXB_201808_PYTHON';  # 定义版本号
        sourceId = detail.get("json_data_id")
        db_helper.insert(template_sql, (id, caseType, casenum, content, title, lawyer_id, court, sourceFrom, sourceId,))
        logging.info("已经新增.")
    update_case_lawyer_schema_on_detail_sucess(detail)


def get_all_case_lawyer():
    try:
        sql = '''SELECT id,office,realname from case_lawyer'''
        ret = db_helper.fetch_all(sql)
        return ret
    except Exception as e:
        logging.exception(e)


def insert_case_lawyer_itslaw(lawyer_id, law_firm, companyName, profiles, profileDetailInfo, lawyer_name):
    print(str(profiles))
    print(str(profileDetailInfo))
    template_sql = '''INSERT INTO `case_lawyer_itslaw`
        (`lawyer_id`,
         `law_firm`,
         `companyName`,
         `profiles`,
         `profileDetailInfo`,
         `lawyer_name`
          )  VALUES (%s, %s, %s, %s, %s, %s)'''
    db_helper.insert(template_sql,
                     (lawyer_id, law_firm, companyName, "", "", lawyer_name,))


#######################################
# 处理案例数据分类
def extract_pending_doc():
    template_sql = '''
    SELECT `id`,lawyer_id,sourceFrom,title from lawyerCase where pending='00' ORDER BY lawyer_id DESC LIMIT 1000
    '''
    return db_helper.fetch_all(template_sql)


def extract_ads_field():
    template_sql = '''
    SELECT `id`,code,createDate,leval,isValid,`name`,pic,updateDate,sorted,selectType from ads_field 
    '''
    return db_helper.fetch_all(template_sql)


def extract_ads_fieldkey():
    template_sql = '''
    SELECT `id`,createDate,fieldCode,isValid,keyword,`updateDate` from ads_fieldkey 
    '''
    return db_helper.fetch_all(template_sql)


def update_pending_doc(doc_id, case_type):
    template_sql = '''
    UPDATE lawyerCase SET caseType=%s,pending='10' WHERE `id`=%s
    '''
    return db_helper.update(template_sql, (case_type, doc_id,))
#######################################
