# coding=utf-8
import json
import logging
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import formatter

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def download_doc(doc_id):
    try:
        save_data_javascript_file(doc_id, IpPort.proxies)
        return proceed_data_javascript()
    except Exception as e:
        logging.error(e)


def download_doc_html(doc_id):
    format_page = None
    try:
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('--headless')
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument('--proxy-server=http://' + IpPort.ip_config.get("ip_config"))
        browser = webdriver.Chrome(chrome_options=chromeOptions)
        browser.delete_all_cookies()
        browser.get("http://wenshu.court.gov.cn/content/content?DocID={}&KeyWord=".format(doc_id))
        WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DivContent"]/div')))
        element = browser.find_element_by_xpath("//*[@id=\"DivContent\"]")
        page = element.get_attribute('innerHTML')
        if page is None or len(page) < 5:
            pass
        else:
            format_page = formatter.html_css_format(page)
        logging.info(format_page)
    except Exception as e:
        logging.error(e)
        logging.info(browser.page_source)
    finally:
        browser.quit()
    return format_page


# 执行javascript数据
def proceed_data_javascript():
    try:
        browser = webdriver.PhantomJS()
        browser.get(
            "file:///C:/Users/Administrator/PycharmProjects/spider_lawyer_case_doc/lawyer/case/doc/templete/doc_templete.html")
        WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DivContent"]/div')))
        element = browser.find_element_by_xpath("//*[@id=\"DivContent\"]")
        page = element.get_attribute('innerHTML')
        format_page = formatter.html_css_format(page)
        logging.info(format_page)
    except Exception as e:
        logging.error(e)
    finally:
        browser.quit()
    return format_page


# 获取javascript数据
def save_data_javascript_file(doc_id, proxies={}):
    payload = {"DocID": doc_id, }
    headers = {'Accept': 'text/javascript, application/javascript, */*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               # _gscu_2116842793=3352668046gxzw10; _gscbrs_2116842793=1; Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2=1535356506,1535357163,1535357263,1535358398;
               # vjkl5=e818651d29aff7a7ad9019118623720ec8b98995; Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2=1535358668; _gscs_2116842793=353572635yn8eq88|pv:11
               'Proxy - Connection': 'keep - alive',
               "Referer": "http://wenshu.court.gov.cn/content/content?DocID={}&KeyWord=".format(doc_id),
               'Host': 'wenshu.court.gov.cn',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest',
               }
    logging.info(payload)
    logging.info(headers)
    res = requests.post(url='http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}'.format(doc_id),
                        data=payload, headers=headers, proxies=proxies,
                        timeout=15)
    text = res.text
    logging.info(text)
    with open(r'C:\Users\Administrator\PycharmProjects\spider_lawyer_case_doc\lawyer\case\doc\templete\temp.js',
              'w', encoding='utf-8') as f:
        f.write('')
    try:
        res.close()
        time.sleep(1)
    except Exception as e:
        logging.error(e)

    if text.find("window.location.href") == -1:
        try:
            with open(r'C:\Users\Administrator\PycharmProjects\spider_lawyer_case_doc\lawyer\case\doc\templete\temp.js',
                      'w',
                      encoding='utf-8') as f:
                f.write('function init() {' + text + '}')
        except Exception as e:
            logging.error(e)
        return text


# wen_shu_js = "";
# with open("./js/wen_shu.js") as f:
#     wen_shu_js += f.read()
# uuid = execjs.compile(wen_shu_js).call('guid')
# logging.info(wen_shu_js)
#
#
# def get_uuid():
#     uuid = execjs.compile(wen_shu_js).call('guid')
#     return uuid


def post_get_vjkl5(guid, AJLX=None, WSLX=None, CPRQ='2018-08-16'):
    conditon = "&conditions=searchWord++CPRQ++%E8%A3%81%E5%88%A4%E6%97%A5%E6%9C%9F:{}%20TO%20{}"
    # conditons = "&conditions=searchWord++CPRQ++%E8%A3%81%E5%88%A4%E6%97%A5%E6%9C%9F:{}%20TO%20{}".format(CPRQ, CPRQ)
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Host': 'wenshu.court.gov.cn',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
               }
    payload = {"guid": guid, "sorttype": 1, "number": "",
               "conditions": 'searchWord  CPRQ  裁判日期:{} TO {}'.format(CPRQ, CPRQ)}  # 先写死
    res = requests.post(
        url="http://wenshu.court.gov.cn/list/list/?sorttype=1&number=&guid=" + guid + conditon.format(CPRQ, CPRQ),
        # url="http://www.sohu.com/",
        headers=headers,
        proxies=IpPort.proxies,
        data=payload,
        timeout=15,
    )
    print("http://wenshu.court.gov.cn/list/list/?sorttype=1&number=&guid=" + guid + conditon.format(CPRQ, CPRQ))
    logging.info(res.cookies)
    return res.cookies.get("vjkl5")


def init_cookies(doc_id):
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--proxy-server=http://' + IpPort.ip_config.get("ip_config"))
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    browser.delete_all_cookies()
    try:
        browser.get("http://wenshu.court.gov.cn/content/content?DocID={}&KeyWord=".format(doc_id))
        Hm_lvt = browser.get_cookie("Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2")['value']
        Hm_lpvt = browser.get_cookie("Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2")['value']
        _gscu_2116842793 = browser.get_cookie("_gscu_2116842793")['value']
        _gscbrs_2116842793 = browser.get_cookie("_gscbrs_2116842793")['value']
        Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2 = browser.get_cookie("Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2")['value']
        Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2 = browser.get_cookie("Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2")[
            'value']
        _gscs_2116842793 = browser.get_cookie("_gscs_2116842793")['value']
        logging.info(browser.get_cookies())
        cookie_dict = {
            '_gscu_2116842793': _gscu_2116842793,
            '_gscbrs_2116842793': _gscbrs_2116842793,
            'Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2': Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2,
            'Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2': Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2,
            '_gscs_2116842793': _gscs_2116842793,
        }
        logging.info(cookie_dict)
        return cookie_dict
    except Exception as e:
        logging.error(e)
    finally:
        browser.quit()


def init_cookies_v2():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--proxy-server=http://' + IpPort.ip_config.get("ip_config"))
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    browser.delete_all_cookies()
    global cookie_dict
    try:
        browser.get("http://wenshu.court.gov.cn")
        Hm_lvt = browser.get_cookie("Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2")['value']
        Hm_lpvt = browser.get_cookie("Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2")['value']
        gscu = browser.get_cookie("_gscu_2116842793")['value']
        gscs = browser.get_cookie("_gscs_2116842793")['value']
        cookie_dict = {
            'Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2': Hm_lvt,
            'Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2': Hm_lpvt,
            '_gscu_2116842793': gscu,
            '_gscs_2116842793': gscs,
        }
        logging.info(cookie_dict)
    finally:
        browser.quit()
    return cookie_dict


class IpPort(object):
    proxies = {}
    ip_config = {}
    cookie_dict = {}
    update = True  # 需要更新IP地址
    count = 0

    @staticmethod
    def random_ip_port():
        IpPort.count = IpPort.count + 1
        if IpPort.update or IpPort.count % 200 == 0:
            ip_port = IpPort._get_ip()
            logging.info("change ip_port=>" + ip_port)
            IpPort.proxies = {
                'http': 'http://{}'.format(ip_port),
                'https': 'https://{}'.format(ip_port),
            }
            IpPort.ip_config = {
                'ip_config': '{}'.format(ip_port),
            }
            IpPort.update = False
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
            'http://api.http.niumoip.com/v1/http/ip/get?p_id=406&s_id=1&u=AWJRM1FiAWQGMwwiUhxValp1DzNVbQsaUAdTVwQC&number=1&port=1&type=1&map=1&pro=0&city=0&pb=1&mr=3&cs=1')
        logging.info(ret.text)
        try:
            dj = json.loads(ret.text)
            return dj['data'][0].get("ip") + ":" + str(dj['data'][0].get("port"))
        except Exception as e:
            time.sleep(60)
