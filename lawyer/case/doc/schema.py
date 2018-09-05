# coding=utf8
import logging

import db
import download
import formatter


def proceed_doc_html():
    schema = db.get_case_lawyer_schema();
    download.IpPort.random_ip_port()
    try:
        html_view = download.download_doc(schema.get("json_data_id"))
        html_source_js = None
        if html_view is not None and html_view != "":
            case_type = formatter.lawyer_case_case_type(schema.get("json_data_name"), html_view)
            db.update_case_lawyer_schema(schema.get("json_data_id"), case_type, html_view, html_source_js)
        else:
            logging.error(html_view)
            download.IpPort.update = True
            db.update_fail_case_lawyer_schema(schema.get("json_data_id"))
    except Exception as e:
        logging.exception("错误")


while True:
    try:
        proceed_doc_html()
    except Exception:
        logging.exception("严重错误")
