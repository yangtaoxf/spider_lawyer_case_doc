# coding=utf-8
from proxy.pool import ProxyPool
import logging
import re


async def async_post_get_vjkl5_url(client, guid, proxies={}, url=""):
    """
    获取vjkl5值
    :param client:
    :param guid:
    :param proxies:
    :param url:
    :return:
    """
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Host': 'wenshu.court.gov.cn',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': ProxyPool.get_random_header(),
               }
    payload = {"guid": "",
               "sorttype": 1,
               "number": "",
               "conditions": 'searchWord 2 AJLX  案件类型:民事案件',
               }
    writ_content = await client.post(url=url,
                                     proxy_headers=headers,
                                     data=payload,
                                     timeout=10,
                                     proxy=proxies.get("http"))
    assert writ_content.status == 200
    vjkl5 = writ_content.cookies.get("vjkl5")
    _ret = re.findall('vjkl5=(.*?);', str(vjkl5))[0]
    logging.info(_ret)
    if writ_content:
        writ_content.close()
    return _ret


async def post_list_context_by_param(client, guid, vjkl5, vl5x, number, param, index=1, page=20, _proxies={}):
    from lawcase.config import LIST_CONTEXT_ORDER_BY, LIST_CONTEXT_ORDER_DIRECTION
    payload = {'Param': param,
               'Index': index,
               'Page': page,
               'Order': LIST_CONTEXT_ORDER_BY,
               'Direction': LIST_CONTEXT_ORDER_DIRECTION,
               'vl5x': vl5x,
               'number': number,
               'guid': guid,
               }
    headers = {'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Connection': 'keep-alive',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'Cookie': 'vjkl5=' + vjkl5,
               'Host': 'wenshu.court.gov.cn',
               'Origin': 'http://wenshu.court.gov.cn',
               'Referer': 'http://wenshu.court.gov.cn/list/list/?sorttype=1&number=&guid=' + guid,
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.0.1471.813 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest',
               }
    logging.info("*=*== _proxies=" + str(_proxies) + ";param=" + param + ";index=" + str(index) + " *=*==")
    _ret = await client.post(url='http://wenshu.court.gov.cn/List/ListContent',
                             proxy_headers=headers,
                             data=payload,
                             timeout=15,
                             proxy=_proxies.get("http"),
                             )
    assert _ret.status == 200
    ret_text = await _ret.text()
    if _ret:
        _ret.close()
    return ret_text
