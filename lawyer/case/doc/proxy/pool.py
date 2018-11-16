# -*- coding: utf-8 -*-
# !/usr/bin/env python
import json
import logging
import os
import re
import sys
import threading
import time, datetime
import random
from wsgiref.simple_server import make_server

import requests

current_Path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_Path)[0]
sys.path.append(root_path)
from config import DOC_RETRY_COUNT, IP_PROXY_CACHE


class IpProxyItem(object):
    """
    代理信息
    """

    def __init__(self, proxies):
        """
        代理ip
        :param proxies:
        """
        self.proxies = proxies  # 存放代理ip容器
        self.fail_count = 0  # 该ip爬取失败次数
        self.success_count = 0  # 该ip爬取成功次数
        self.recent_fail_count = 0  # 该ip连续失败次数
        self.refresh = False  # 是否需要更新ip
        self.create_date = datetime.datetime.now()  # 该代理ip更新时间

    def success(self):
        """
        爬取成功
        :return:
        """
        self.recent_fail_count = 0
        self.success_count += 1
        if self.refresh:
            logging.info("########### IP重新置为可用{} ##################".format(str(self.proxies)))
            self.refresh = False

    def fail(self, multiple=1):
        """
        爬取失败
        :param multiple: 权重
        :return:
        """
        self.recent_fail_count += multiple
        self.fail_count += + 1
        if self.recent_fail_count >= DOC_RETRY_COUNT:  # 连续失败次数超过配置最大重试次数参数，需要更换ip
            if not self.refresh:
                self.refresh = True
                logging.info("===fail IP置为无效===:{}".format(self.proxies))

    def refresh(self):
        """
        此ip更新为无效
        :return:
        """
        logging.info("===refresh IP置为无效===:{}".format(self.proxies))
        self.refresh = True

    @staticmethod
    def build(number=1):
        """
        生成代理ip
        :param number: 需要生成的ip数量
        :return:
        """
        __ret = []
        ip_proxies = IpPort.get_proxies_at_once(number)
        for ip_proxy in ip_proxies:
            __ret.append(IpProxyItem(ip_proxy))
        return __ret

    def __str__(self):
        return "success_count={};recent_fail_count={};fail_count={};refresh={};proxies={};create_date={}".format(
            self.success_count,
            self.recent_fail_count,
            self.fail_count,
            self.refresh,
            str(self.proxies["http"]) if "http" in self.proxies else None,
            self.create_date,
        )


my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"

]


class ProxyPool(object):
    """
    代理池管理
    """
    _instance_lock = threading.Lock()
    _before_ip = {"http": "none"}
    _ip_proxy_cache = IP_PROXY_CACHE  # 代理池代理ip数量参数
    _ip_proxy_cache_detail = {}
    _count = 0

    @staticmethod
    def __before_init__():
        for _index in range(1, ProxyPool._ip_proxy_cache + 1):
            ProxyPool._ip_proxy_cache_detail["_ip_proxy_cache_key_{}".format(_index)] = None
        print(ProxyPool._ip_proxy_cache_detail)

    def __init__(self):
        ProxyPool.__before_init__()
        self.ip_pool = IpPort.proxies
        if not self.ip_pool:
            self.fail_count = 0

    def __new__(cls, *args, **kwargs):
        if not hasattr(ProxyPool, "_instance"):
            with ProxyPool._instance_lock:
                if not hasattr(ProxyPool, "_instance"):
                    ProxyPool._instance = object.__new__(cls, *args, **kwargs)
                    ProxyPool._instance.ip_pool = {}
                    logging.info("init............")
        return ProxyPool._instance

    @staticmethod
    def change_ip_proxy_cache(cache=IP_PROXY_CACHE):
        ProxyPool._ip_proxy_cache_detail.clear()
        ProxyPool._ip_proxy_cache = cache
        ProxyPool.__before_init__()

    @staticmethod
    def refresh(ip_proxy_item):
        """
        更新代理ip,无效
        :param ip_proxy_item:
        :return:
        """
        if isinstance(ip_proxy_item, IpProxyItem):
            ip_proxy_item.refresh()

    @staticmethod
    def validate_init_ip_proxy():
        """
        筛选去除无效ip,使用新ip.加入代理池
        :return:
        """
        update_key = []
        for key, value in ProxyPool._ip_proxy_cache_detail.items():
            logging.info("==={} [{}]".format(key, value))
            if not value or value.refresh:
                update_key.append(key)
                if hasattr(value, "create_date"):
                    if (datetime.datetime.now() - value.create_date).seconds < 120:  # 2内分钟不提取
                        logging.warning("[=*= 失败率过高=*=],暂时不提取新IP 【{}】".format(value))
                        update_key.remove(key)

        length = len(update_key)
        if length > 0:
            proxis = IpProxyItem.build(number=length)
            for key in update_key:
                if len(proxis) > 0:
                    ProxyPool._ip_proxy_cache_detail[key] = proxis.pop()

    @staticmethod
    def fail(ip_proxy_item, multiple=1):
        """
        更新代理ip爬取失败
        :param ip_proxy_item:
        :param multiple:
        :return:
        """
        ip_proxy_item.fail(multiple)

    @staticmethod
    def warn(ip_proxy_item, multiple=0.5):
        ip_proxy_item.fail(multiple)

    @staticmethod
    def success(ip_proxy_item):
        """
        更新代理爬取成功
        :param ip_proxy_item:
        :return:
        """
        ip_proxy_item.success()

    @staticmethod
    def extract_cache_ip_proxy_item() -> IpProxyItem:
        """
        从代理池拿ip
        :return:
        """
        ProxyPool._count = ProxyPool._count + 1
        _index = (ProxyPool._count % ProxyPool._ip_proxy_cache) + 1
        return ProxyPool._ip_proxy_cache_detail["_ip_proxy_cache_key_{}".format(_index)]

    @staticmethod
    def get_random_header() -> str:
        random_header = random.choice(my_headers)
        return random_header

    @staticmethod
    def check_proxy(proxy):
        if not proxy:
            raise NotIpProxyException(code=999, message='没有使用代理异常')


class NotIpProxyException(Exception):
    def __init__(self, code=999, message='没有使用代理异常', args=('没有使用代理异常',)):
        self.args = args
        self.message = message
        self.code = code


class IpPort(object):
    proxies = {}
    ip_config = {}
    cookie_dict = {}
    update = True  # 需要更新IP地址
    count = 0
    _time = time.time()
    __max_retry_count = DOC_RETRY_COUNT

    @staticmethod
    def random_ip_port():
        IpPort.count = IpPort.count + 1
        if IpPort.update or IpPort.count % IpPort.__max_retry_count == 0:
            IpPort.update = False
            ip_port = IpPort._get_ip().pop()
            logging.info("change ip_port=>" + ip_port)
            IpPort.proxies = {
                'http': 'http://{}'.format(ip_port),
                'https': 'https://{}'.format(ip_port),
            }
            IpPort.ip_config = {
                'ip_config': '{}'.format(ip_port),
            }
            IpPort.count = 0
        logging.info("IpPort count=" + str(IpPort.count))
        return IpPort

    @staticmethod
    def get_proxies_at_once(number):
        ip_port = IpPort._get_ip(number=number)
        __ret = []
        for it in ip_port:
            __ret.append({
                'http': 'http://{}'.format(it),
                'https': 'https://{}'.format(it),
            })
        return __ret

    @staticmethod
    def _get_ip(number):
        __ret = []
        try:
            # 'http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=5&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city='
            # "http://api3.xiguadaili.com/ip/?tid=555153033920990&&num=1&format=json&delay=1&filter=on&longlife=5&category=2"
            # "http://47.107.111.163:8123/download/doc/?order=cbda12cf21444c55a04c33deb4a9f938&json=1&sep=3"
            # "http://47.107.111.163:8123/list/context/?order=cbda12cf21444c55a04\c33deb4a9f938&json=1&sep=3"
            # "http://47.107.111.163:8123/list/context/?tset=123123"
            ret = requests.get("http://47.107.111.163:8123/download/doc_v3/number_{}_".format(number))
            logging.info(ret.text)
            dj = json.loads(ret.text)
            for it in dj['data']:
                __ret.append(it.get("IP"))
            # return dj['data'][0].get("ip") + ":" + str(dj['data'][0].get("port"))
            # return dj['data'][0].get("IP")
            # return dj['data'][0].get("ip") + ":" + str(dj['data'][0].get("port"))
            # return dj[0].get("host") + ":" + str(dj[0].get("port"))
        except Exception as e:
            logging.exception("error:")
            time.sleep(1)
        finally:
            return __ret

    @staticmethod
    def get_remote_list_ip():
        __ret = requests.get(
            # 'http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=5&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city='
            "http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=5&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city="
        )
        logging.info(__ret.text)
        return __ret.text

    @staticmethod
    def get_remote_doc_ip(
            url="http://api.ip.data5u.com/dynamic/get.html?order=cbda12cf21444c55a04c33deb4a9f938&json=1&sep=3"):
        # 'http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=5&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city='
        __text = '{"errorMsg":"没有代理"}'
        try:
            with requests.get(url=url) as ret:
                __text = ret.text
                logging.info(__text)
        except Exception:
            logging.error("===错误发生===")
        return __text


def get_remote_proxy_ip(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    path = environ['PATH_INFO']
    __ret = []

    if "download/doc_v2" in path:
        __ip = IpPort.get_remote_doc_ip(
            url="http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=3&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city=")
        __ip = __ip.encode("utf-8")
        __ret.append(__ip)
        logging.warning("download/doc_v2" + str(__ip))
    elif "download/doc_v3/number" in path:  # 指定数量
        __number_list = re.findall(r'number_(.*?)_', path)
        number = __number_list.pop()
        # mock = '''{"code":0,"success":true,"msg":"","data":[{"IP":"0.0.0.0","Port":8080,"ExpireTime":"2018-01-01 08:08:08","IpAddress":"湖南省益阳市 电信","ISP":"电信"},{"IP":"0.0.0.0","Port":8080,"ExpireTime":"2018-01-01 08:08:08","IpAddress":"湖南省益阳市 电信","ISP":"电信"}]}'''
        __url = "http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=3&qty={}&port=1&format=json&ss=5&css=&ipport=1&pro=&city=".format(
            number)
        __ip = IpPort.get_remote_doc_ip(url=__url)
        __ip = __ip.encode("utf-8")
        logging.warning("download/doc_v3" + str(__ip))
        __ret.append(__ip)
    elif "download/doc" in path:
        __ip = IpPort.get_remote_doc_ip().encode("utf-8")
        logging.warning("download/doc" + str(__ip))
        __ret.append(__ip)
        return __ret
    elif "/list/context" in path:
        __ip = IpPort.get_remote_list_ip().encode("utf-8")
        logging.warning("/list/context" + str(__ip))
        __ret.append(__ip)
    return __ret


if __name__ == "__main__":
    """
    获取IP
    """
    logging.warning("***get_remote_proxy_ip====master===start***")
    httpd = make_server("", 8123, get_remote_proxy_ip)
    httpd.serve_forever()
