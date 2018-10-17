# coding=utf-8
import json
import logging
import time
import requests
import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import aiohttp
from aiohttp.client_exceptions import ClientProxyConnectionError as ClientProxyConnectionError
import formatter
from proxy.pool import ProxyPool

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )

proxy_pool = ProxyPool()


def download_doc(doc_id):
    try:
        text = save_data_javascript_file(doc_id, IpPort.proxies, config.save_data_javascript_file_path)
        if text.find("此篇文书不存在!") > 0:
            return "文档不存在"
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
        logging.exception(e)
        page_source = browser.page_source
        if "文档不存在" in page_source or "此篇文书不存在" in page_source:
            format_page = "文档不存在"
        logging.info(page_source)
    finally:
        browser.quit()
    return format_page


# 执行javascript数据
def proceed_data_javascript(html=config.proceed_data_javascript_html, ):
    try:
        if "windows" in config.platform:
            browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
        else:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument("window-size=1024,768")
            chrome_options.add_argument("--no-sandbox")
            browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get(html)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DivContent"]/div')))
        element = browser.find_element_by_xpath("//*[@id=\"DivContent\"]")
        page = element.get_attribute('innerHTML')
        if page is None or len(page) < 5:
            pass
        else:
            format_page = formatter.html_css_format(page)
            logging.info(format_page)
    except Exception as e:
        logging.error(e)
    finally:
        browser.quit()
    return format_page


def get_data_javascript_file(doc_id, proxies={}):
    payload = {"DocID": doc_id, }
    headers = {'Accept': 'text/javascript, application/javascript, */*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
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
    try:
        res.close()
        time.sleep(1)
    except Exception as e:
        logging.error(e)
    return text


async def async_get_data_javascript(case_detail_dao):
    """
    获取javascript脚本内容
    :param case_detail_dao 文档id
    :return:
    """
    doc_id = case_detail_dao.case_detail.get("doc_id")
    async with aiohttp.ClientSession() as client:
        client.cookie_jar.clear()
        payload = {"DocID": doc_id, }
        headers = {'Accept': 'text/javascript, application/javascript, */*',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Proxy - Connection': 'keep - alive',
                   "Referer": "http://wenshu.court.gov.cn/content/content?DocID={}&KeyWord=".format(doc_id),
                   'Host': 'wenshu.court.gov.cn',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                   'X-Requested-With': 'XMLHttpRequest',
                   }
        logging.info(payload)
        logging.info(headers)
        proxy = proxy_pool.ip_pool.get("http")
        try:
            writ_content = await client.post(
                url='http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={}'.format(doc_id),
                proxy_headers=headers,
                data=payload,
                timeout=15,
                proxy=proxy)
            java_script = await writ_content.text()
            assert writ_content.status == 200
            # logging.info(java_script)
            case_detail_dao.update_case_detail(java_script)
        except AssertionError:
            proxy_pool.refresh(proxy)
        except ClientProxyConnectionError:
            proxy_pool.refresh(proxy)
        except Exception:
            proxy_pool.refresh(proxy)
            logging.exception("error=>:")


# 获取javascript数据
def save_data_javascript_file(doc_id, proxies={}, javascript_file=config.save_data_javascript_file_path):
    text = get_data_javascript_file(doc_id, proxies)
    _try = 0
    while _try <= 6 and text.find("此篇文书不存在!") > 0:
        logging.info("重试下载：" + doc_id)
        text = get_data_javascript_file(doc_id, proxies)
        _try = _try + 1
    with open(javascript_file, 'w', encoding='utf-8') as f:
        f.write('')
    if text.find("window.location.href") == -1:
        try:
            with open(javascript_file, 'w', encoding='utf-8') as f:
                f.write('function init() {' + text + '}')
        except Exception as e:
            logging.error(e)
        return text


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
            # 'http://47.96.139.87:8081/Index-generate_api_url.html?packid=7&fa=5&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city='
            "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=b6f79e2ceee94ab09c703e9efd54528d&count=1&expiryDate=0&format=1&newLine=2"
        )
        logging.info(ret.text)
        try:
            dj = json.loads(ret.text)
            # return dj['data'][0].get("ip") + ":" + str(dj['data'][0].get("port"))
            # return dj['data'][0].get("IP")
            {"code": "0", "msg": [{"port": "25402", "ip": "60.169.221.24"}]}
            return dj['msg'][0].get("ip") + ":" + str(dj['msg'][0].get("port"))
        except Exception as e:
            time.sleep(60)
