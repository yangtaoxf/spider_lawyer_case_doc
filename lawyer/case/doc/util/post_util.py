# coding=utf8
import random
import logging
import requests

my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"

]


def get_random_header() -> str:
    random_header = random.choice(my_headers)
    return random_header


def post_get_vjkl5_url(guid, url="http://wenshu.court.gov.cn/list/list/?sorttype=1", _proxies={}):
    """
    获取vjkl5值
    :param guid:
    :param url:
    :param _proxies:
    :return:
    """
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Host': 'wenshu.court.gov.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': get_random_header(),
    }
    payload = {"guid": "",
               "sorttype": 1,
               "number": "",
               "conditions": 'searchWord 2 AJLX  案件类型:民事案件',
               }  # 先写死
    res = requests.post(
        url=url,
        headers=headers,
        proxies=_proxies,
        data=payload,
        timeout=15,
    )
    logging.info(res.cookies)
    return res.cookies.get("vjkl5")
