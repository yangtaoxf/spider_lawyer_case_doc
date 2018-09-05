# -*-coding:utf-8 -*-
import logging
import time
import urllib.parse as urlparse
import requests
import json
import db

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def get_linux_time():
    """
    获取linux 10位时间戳
    :return:
    """
    return time.time().__int__()


class ITSLaw(object):
    """
    无讼律师信息
    """

    #
    def __init__(self, lawyer_name, law_firm, cookie={}):
        """
        :parameter lawyer_name 律师姓名
        :parameter law_firm 律所信息
        """
        self.lawyer_name = lawyer_name
        self.law_firm = set()
        self.law_firm.add(law_firm)
        self.cookie = cookie
        self.profileDetailInfo = None
        self.companyName = None
        self.__spider_lawyer_profiles()
        self.__get_lawyer_detail()

    def __spider_lawyer_profiles(self):
        """
        爬取律师的名片信息
        :return: 律师的信息
        """
        _request_url = "https://www.itslaw.com/api/v1/profiles?startIndex=0&countPerPage=20&sortType=1&conditions=" + urlparse.quote(
            "searchWord+{}+1+{}".format(self.lawyer_name, self.lawyer_name))
        payload = {"startIndex": "0",
                   "countPerPage": "20",
                   "sortType": "1",
                   "conditions": "searchWord+{}+1+{}".format(self.lawyer_name, self.lawyer_name), }

        cookie_time = get_linux_time()
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008={}; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c={}; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008={}; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c={}'
                .format(cookie_time, cookie_time, cookie_time, cookie_time),
            'Host': 'www.itslaw.com',
            'If-Modified-Since': 'Mon, 26 Jul 1997 05:00:00 GMT',
            'Pragma': 'no-cache',
            'Referer': _request_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        logging.info(payload)
        logging.info(headers)
        res = requests.get(
            url=_request_url,
            data=payload, headers=headers, proxies={},
            timeout=15)
        logging.info(res.text)
        cookies = res.cookies
        logging.info(cookies)
        self.cookie['_t'] = cookies.get('_t')
        self.cookie['sessionId'] = cookies.get('sessionId')
        self.profiles = res.text
        self.lawyer_id = self.__get_lawyer_id()

    def __get_lawyer_id(self):
        """
        获取无诉案例律师id
        :return:
        """
        lawyer_id = None
        profile_search_result = json.loads(self.profiles).get("data").get("profileSearchResult").get("profiles")
        try:
            for it in profile_search_result:
                lawFirm = it.get("lawFirm")
                if lawFirm in self.law_firm:
                    lawyer_id = it.get("id")
        except Exception:
            logging.error(self.profiles)
            logging.exception("获取律师id出错了")
        return lawyer_id

    def __get_lawyer_detail(self):
        """
        爬取律师的详细信息
        :return: 律师的信息
        """
        if self.lawyer_id == None or self.lawyer_id == "":
            return
        _request_url = 'https://www.itslaw.com/api/v1/profiles/profile?profileId={}'.format(self.lawyer_id)
        payload = {"profileId": self.lawyer_id, }

        cookie_time = get_linux_time()
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'Hm_lvt_bc6f194cb44b24b9f44f1c8766c28008={}; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c={}; Hm_lpvt_bc6f194cb44b24b9f44f1c8766c28008={}; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c={}; _t={}; sessionId={}'
                .format(cookie_time, cookie_time, cookie_time, cookie_time, self.cookie.get("_t"),
                        self.cookie.get("sessionId")),
            'Host': 'www.itslaw.com',
            'If-Modified-Since': 'Mon, 26 Jul 1997 05:00:00 GMT',
            'Pragma': 'no-cache',
            'Referer': _request_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        res = requests.get(
            url=_request_url,
            data=payload, headers=headers, proxies={},
            timeout=15)
        logging.info(res.text)
        self.profileDetailInfo = res.text
        self.companyName = self.__proceed_workExperiences()

    def __proceed_workExperiences(self):
        """
        解析工作经历
        :return:
        """
        ret = []
        profileDetailInfo = json.loads(self.profileDetailInfo).get("workExperiences")
        workExperiences = None
        try:
            workExperiences = profileDetailInfo.get("data").get("profileDetailInfo").get("workExperiences")
        except Exception:
            logging.exception("exception:")
        if workExperiences is None:
            return ret
        for workExperience in workExperiences:
            companyName = workExperience.get("companyName")
            ret.append(companyName)
        return ret


def get_lawyers():
    """
    获需要处理的取律师
    :return:
    """
    ret = db.get_all_case_lawyer()
    logging.info(ret)
    return ret


if __name__ == '__main__':
    lawyers = get_lawyers()
    for it in lawyers:
        lawyer_id = it.get("id")
        law_firm = it.get("office")
        lawyer_name = it.get("realname")
        try:
            lawyer = ITSLaw(lawyer_name=lawyer_name, law_firm=law_firm)
            db.insert_case_lawyer_itslaw(lawyer_id, law_firm, lawyer.companyName, lawyer.profiles,
                                         lawyer.profileDetailInfo,
                                         lawyer_name)
            time.sleep(5)
        except Exception:
            logging.exception("插入出错了。")
