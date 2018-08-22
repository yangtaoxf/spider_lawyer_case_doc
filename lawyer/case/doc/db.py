import pymysql.cursors
import pymysql
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

'''
get case_lawyer_schema table data to crawling
'''
db_config = {
    'host': "120.76.138.153",
    'port': 3307,
    'user': 'root',
    'password': 'faduceshi123!@#',
    'db': "duowen",
    'charset': 'utf8',
}


def get_case_lawyer_schema():
    try:
        connection = pymysql.connect(host=db_config.get("host"), port=db_config.get("port"), user=db_config.get("user"),
                                     password=db_config.get("password"), db=db_config.get("db"),
                                     charset=db_config.get("utf8"))
        cursor = connection.cursor()
        sql = '''SELECT lawyer_id,json_data_id from case_lawyer_schema where beautiful_html_status={} order by createdate asc limit 1'''.format(
            BEAUTIFUL_HTML_STATUS_00)
        cursor.execute(sql)
        row = cursor.fetchone()
        schema = {"lawyer_id": row[0], "json_data_id": row[1], }
    except Exception as e:
        logging.error(e)
    finally:
        connection.close()
    logging.info(schema)
    return schema


# 未解析
BEAUTIFUL_HTML_STATUS_00 = '00'
# 已经解析
BEAUTIFUL_HTML_STATUS_10 = '10'


# 保存html页面
def update_case_lawyer_schema(lawyer_id, html_view):
    try:
        connection = pymysql.connect(host=db_config.get("host"), port=db_config.get("port"), user=db_config.get("user"),
                                     password=db_config.get("password"), db=db_config.get("db"),
                                     charset=db_config.get("utf8"))
        cursor = connection.cursor()
        sql = '''UPDATE case_lawyer_schema SET beautiful_html_status={},beautiful_html_view=%s where beautiful_html_status={} and lawyer_id=%s'''.format(
            BEAUTIFUL_HTML_STATUS_10, BEAUTIFUL_HTML_STATUS_00)
        cursor.execute(sql, (html_view, lawyer_id,))
        connection.commit()
        logging.info(cursor.fetchall())
    except Exception as e:
        logging.error(e)
    finally:
        connection.close()
