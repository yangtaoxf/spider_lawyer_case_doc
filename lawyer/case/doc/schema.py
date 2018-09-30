# coding=utf8
import logging

import db
import download
import doc_classification


def proceed_doc_html():
    schema = db.get_case_lawyer_schema();
    download.IpPort.random_ip_port()
    try:
        html_view = download.download_doc(schema.get("json_data_id"))
        html_source_js = None
        if html_view is not None and html_view != "":
            if "文档不存在" in html_view:
                db.update_fail_case_lawyer_schema(schema.get("json_data_id"))
                return
            case_type = doc_classification.match_field_code(schema.get("json_data_id"), schema.get("lawyer_id"),
                                                            schema.get("json_data_name"))
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
