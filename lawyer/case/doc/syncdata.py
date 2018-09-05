# coding=utf8
import logging
import time
import db

while True:
    global row
    try:
        sql = '''SELECT `id`,lawyer_id,json_data_name,json_data_court,json_data_number,beautiful_html_view,beautiful_case_type,json_data_id from case_lawyer_schema where beautiful_html_status=%s and sync_status=%s order by createdate asc limit 1'''
        row = db.db_helper.fetch_one(sql, (db.BEAUTIFUL_HTML_STATUS_10, db.SYNC_STATUS_10,))
        if row is None:
            time.sleep(60)
            continue
        db.insert_or_update_lawyercase(row)
    except Exception as e:
        time.sleep(60)
        logging.exception("出现错误.")
    finally:
        logging.info(row)
