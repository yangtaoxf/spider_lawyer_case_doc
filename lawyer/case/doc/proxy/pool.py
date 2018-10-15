# -*- coding: utf-8 -*-
# !/usr/bin/env python
import logging
import threading
import time
import requests
import json


class ProxyPool(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.ip_pool = IpPort.proxies
        if not self.ip_pool:
            self.refresh()

    def __new__(cls, *args, **kwargs):
        if not hasattr(ProxyPool, "_instance"):
            with ProxyPool._instance_lock:
                if not hasattr(ProxyPool, "_instance"):
                    ProxyPool._instance = object.__new__(cls, *args, **kwargs)
                    ProxyPool._instance.ip_pool = {}
                    logging.info("init............")
        return ProxyPool._instance

    def refresh(self, history="马上获取IP"):
        now = self.ip_pool.get("http")
        logging.info(history + ";====;" + str(now))
        if not now or history in now:
            IpPort.update = True
            IpPort.random_ip_port()
            logging.info("change IP:" + str(self.ip_pool))
            self.ip_pool = IpPort.proxies


class IpPort(object):
    proxies = {}
    ip_config = {}
    cookie_dict = {}
    update = True  # 需要更新IP地址
    count = 0
    _time = time.time()

    @staticmethod
    def random_ip_port():
        IpPort.count = IpPort.count + 1
        if IpPort.update or IpPort.count % 200 == 0:
            IpPort.update = False
            ip_port = IpPort._get_ip()
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
    def get_cookie_dict(doc_id):
        IpPort.cookie_dict = init_cookies(doc_id)
        return IpPort.cookie_dict

    @staticmethod
    def _get_ip():
        time.sleep(1)
        ret = requests.get(
            # 'http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=5&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city='
            "http://api.ip.data5u.com/dynamic/get.html?order=cbda12cf21444c55a04c33deb4a9f938&json=1&sep=3"
        )
        logging.info(ret.text)
        try:
            dj = json.loads(ret.text)
            # return dj['data'][0].get("ip") + ":" + str(dj['data'][0].get("port"))
            # return dj['data'][0].get("IP")
            return dj['data'][0].get("ip") + ":" + str(dj['data'][0].get("port"))
        except Exception as e:
            logging.exception("error:")
            time.sleep(60)
