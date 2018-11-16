# coding=utf-8
import logging
import aiohttp
import execjs
import concurrent
from lawcase.config import PAGE_NUM, RETRY_NUM, MAX_PAGE_DATA_NUM
from lawcase.service import download
from proxy.pool import ProxyPool, NotIpProxyException
from aiohttp.client_exceptions import ClientProxyConnectionError as ClientProxyConnectionError
from aiohttp.client_exceptions import ClientOSError
from lawcase.bean import LawyerInfoBean
from lawcase.dao import CaseLawyerContextDao, CaseLawyerDao
import json
from lawcase.js import wen_shu_js

# 代理池
proxy_pool = ProxyPool()


class CasePlanSchema(object):
    """
    获取调度任务
    """
    __max_retry = RETRY_NUM  # 最大重试次数
    __page = PAGE_NUM  # 每页条数
    __max_data_num = MAX_PAGE_DATA_NUM  # 最大条数

    @staticmethod
    async def proceed_schema(bean):
        """
        下载任务
        :return:
        """
        if not bean:
            logging.warning("没有任务")
            return False
        if bean.page_index == 0:
            bean.page_index = 1
        try:
            json_text = None
            try:
                ip_proxy_item = proxy_pool.extract_cache_ip_proxy_item()
                ProxyPool.check_proxy(ip_proxy_item)  # 检查代理
                proxies = ip_proxy_item.proxies
                json_text = await _proceed_schema(param=bean.schema_search,
                                                  index=bean.page_index,
                                                  page=bean.page,
                                                  proxies=proxies)
            except AssertionError:
                proxy_pool.fail(ip_proxy_item, multiple=1)
                logging.error("===AssertionError===")
            except NotIpProxyException:
                logging.error("===没有获取使用ip===")
                proxy_pool.refresh(ip_proxy_item)
            except ClientProxyConnectionError:
                logging.error("ClientProxyConnectionError")
                proxy_pool.fail(ip_proxy_item, multiple=10)
            except ClientOSError:
                logging.error("ClientOSError")
                proxy_pool.fail(ip_proxy_item)
            except aiohttp.client_exceptions.ClientPayloadError:
                logging.error("ClientPayloadError")
                proxy_pool.fail(ip_proxy_item)
            except TimeoutError:
                logging.error("TimeoutError")
                proxy_pool.fail(ip_proxy_item)
            except concurrent.futures._base.TimeoutError:
                logging.error("concurrent_TimeoutError")
                proxy_pool.fail(ip_proxy_item)
            except aiohttp.client_exceptions.ServerDisconnectedError:
                logging.error("ServerDisconnectedError")
                proxy_pool.fail(ip_proxy_item, multiple=2)
            except Exception:
                proxy_pool.fail(ip_proxy_item, multiple=10)
                logging.exception("error=>:")
            # 检查内容是否正确
            success = False
            if not json_text:
                return
            elif "remind" in json_text:
                logging.info("[***---remind---***] param=" + bean.schema_search +
                             ";page=" + str(bean.page_index) + ";***")
                proxy_pool.fail(ip_proxy_item, multiple=5)
            elif "RunEval" in json_text:
                proxy_pool.success(ip_proxy_item)
                if "Count" in json_text:
                    success = True
                    logging.info("[***---success---***] param=" + bean.schema_search +
                                 ";page=" + str(bean.page_index) + ";***")
                else:
                    logging.info("[***--repeat---***] param=" + bean.schema_search +
                                 ";page=" + str(bean.page_index) + ";有RunEval值,但没有Count值***")
                    success = True
                    bean.process = LawyerInfoBean.PROCESS_5
            # 没有成功不解析
            if not success:
                return
            if '"[{\\' in json_text and bean.process != LawyerInfoBean.PROCESS_5:
                json_text = json_text.replace('\\"', '\"')[1:-1]  # 转移字符
                batch_count = int(json.loads(json_text)[0].get("Count"))
                CaseLawyerContextDao.insert_case_lawyer_context(bean.lawyer_id, json_text,
                                                                bean.page_index, batch_count,
                                                                bean.page)
            # 处理成功
            if bean.process == LawyerInfoBean.PROCESS_5:
                pass
            elif (bean.page_index * bean.page >= batch_count):
                bean.process = LawyerInfoBean.PROCESS_3
            elif bean.page_index * bean.page >= 200 and batch_count > 200:
                bean.process = LawyerInfoBean.PROCESS_4
            else:
                bean.page_index = bean.page_index + 1

        except:
            logging.exception("===处理失败===")
            bean.process = LawyerInfoBean.PROCESS_2  # 处理失败
        finally:
            CaseLawyerDao.update(bean.lawyer_id, bean.page_index, bean.process)

    @staticmethod
    def remove_complete_task(deal_task_pool=[]):
        logging.info("remove_complete_task from ====" + str(deal_task_pool))

        def condition(data={}):
            return not ("process" in data.keys() and data.get("process"))

        __deal_task_pool = list(filter(condition, deal_task_pool))
        return __deal_task_pool


async def _proceed_schema(param, proxies={}, index=1, page=20):
    guid = execjs.compile(wen_shu_js).call('guid')
    referer = "http://wenshu.court.gov.cn/list/list/?sorttype=1"
    async with aiohttp.ClientSession() as client:
        client.cookie_jar.clear()
        vjkl5 = await download.async_post_get_vjkl5_url(client, guid, proxies=proxies, url=referer)
        vl5x = execjs.compile(wen_shu_js).call('getkey', vjkl5)
        number = 'wens'
        json_text = await download.post_list_context_by_param(client, guid, vjkl5, vl5x, number, param,
                                                              index=index,
                                                              page=page,
                                                              _proxies=proxies
                                                              )
        return json_text
