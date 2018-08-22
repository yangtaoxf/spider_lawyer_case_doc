import db
import download


def proceed_doc_html():
    schema = db.get_case_lawyer_schema();
    html_view = download.download_doc(schema.get("json_data_id"))
    if html_view is not None and html_view != "":
        db.update_case_lawyer_schema(schema.get("lawyer_id"), html_view)


while True:
    proceed_doc_html()
