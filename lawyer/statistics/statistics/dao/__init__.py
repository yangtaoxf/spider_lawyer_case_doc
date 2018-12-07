# coding=utf-8
from statistics.dbtools import db


class LawyerDao(object):
    @staticmethod
    def query_by_lawyer_id(lawyer_id):
        row = db.fetch_one("SELECT * FROM lawyer WHERE id=%s", (lawyer_id,))
        print(row)
        return row


# LawyerDao.query_by_lawyer_id(lawyer_id="4a423e0c02b9e7aa5acf2b4d06427ac1")
class SsdbOrderDao(object):
    # SELECT count(1) from ssdb_order WHERE lawyer_id = ""
    pass
