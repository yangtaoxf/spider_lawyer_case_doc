# coding=utf-8
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import requests
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )


def download_doc(doc_id):
    try:
        save_data_javascript_file(doc_id)
        return proceed_data_javascript()
    except Exception as e:
        # browser.quit()
        logging.error(e)


# 执行javascript数据
def proceed_data_javascript():
    try:
        browser = webdriver.PhantomJS()
        browser.get(
            "file:///C:/Users/Administrator/PycharmProjects/spider_lawyer_case_doc/lawyer/case/doc/templete/doc_templete.html")
        time.sleep(5)
        element = browser.find_element_by_xpath("//*[@id=\"DivContent\"]")
        page = element.get_attribute('innerHTML')
        logging.info(page)
    except Exception as e:
        logging.error(e)
    finally:
        browser.quit()
    return page


# 获取javascript数据
def save_data_javascript_file(doc_id, cookie_dict={}):
    payload = {"DocID": doc_id, }
    headers = {'Accept': 'text/javascript, application/javascript, */*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Cookie': 'gscu_2116842793={}; _gscbrs_2116842793=1; _gscs_2116842793=34907010se607e88|pv:1'.format(
                   cookie_dict.get("_gscu_2116842793"), cookie_dict.get("")),
               'Host': 'wenshu.court.gov.cn',
               'Referer': 'http://wenshu.court.gov.cn/content/content?DocID={}&KeyWord='.format(doc_id),
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest',
               }
    logging.info(payload)
    logging.info(headers)
    res = requests.get(url='http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}'.format(doc_id),
                       data=payload, headers=headers,
                       timeout=30)
    logging.info(res.text)
    try:
        with open(r'C:\Users\Administrator\PycharmProjects\spider_lawyer_case_doc\lawyer\case\doc\templete\temp.js',
                  'w',
                  encoding='utf-8') as f:
            f.write('function init() {' + res.text + '}')
        time.sleep(1)
    except Exception as e:
        logging.error(e)
    return res.text


def init_cookies():
    chromeOptions = webdriver.ChromeOptions()
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


init_cookies()
