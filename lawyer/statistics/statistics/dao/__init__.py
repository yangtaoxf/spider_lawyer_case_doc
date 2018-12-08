# coding=utf-8
from statistics.dbtools import db


class LawyerDao(object):
    @staticmethod
    def query_by_lawyer_id(lawyer_id):
        row = db.fetch_one("SELECT * FROM lawyer WHERE id=%s", (lawyer_id,))
        print(row)
        return row

    @staticmethod
    def extract_all_lawyer_id():
        row = db.fetch_all("SELECT id FROM lawyer limit 10", ())
        print(row)
        return row


# LawyerDao.query_by_lawyer_id(lawyer_id="4a423e0c02b9e7aa5acf2b4d06427ac1")
class SsdbOrderDao(object):
    # SELECT count(1) from ssdb_order WHERE lawyer_id = ""

    @staticmethod
    def count(lawyer_id):
        row = {}
        if lawyer_id:
            row = db.fetch_one('SELECT count(1) as count from ssdb_order WHERE lawyer_id = %s', (lawyer_id,))
            print(row, lawyer_id)
        return row


class AjhzOrderDao(object):
    @staticmethod
    def distribute_count(lawyer_id):
        row = {}
        if lawyer_id:
            row = db.fetch_one('SELECT count(1) as count from ajhz_order WHERE lawyerA_id = %s', (lawyer_id,))
        return row

    @staticmethod
    def accept_count(lawyer_id):
        row = {}
        if lawyer_id:
            row = db.fetch_one('SELECT count(1) as count from ajhz_order WHERE lawyerB_id = %s', (lawyer_id,))
        return row


class LawyerCaseDao(object):
    @staticmethod
    def group(lawyer_id):
        row = {}
        if lawyer_id:
            row = db.fetch_all(
                'SELECT caseType,count(1) as count from lawyercase WHERE lawyer_id = %s GROUP BY caseType',
                (lawyer_id,))
            print(row, lawyer_id)
        return row
