# coding=utf-8
from lawcase.config import PAGE_NUM


class LawyerInfoBean(object):
    """
    律师案例爬取信息
    """
    PROCESS_0 = 0  # 未处理
    PROCESS_1 = 1  # 处理中
    PROCESS_2 = 2  # 处理失败
    PROCESS_3 = 3  # 处理成功
    PROCESS_4 = 4  # 处理部分成功,超过200条记录,需要特殊处理
    PROCESS_5 = 5  # 没有返回正确的数据

    def __init__(self, lawyer_id, lawyer_name, law_firm, phone, process, page_index=1, page=PAGE_NUM):
        self.lawyer_id = lawyer_id
        self.lawyer_name = lawyer_name
        self.law_firm = law_firm
        self.phone = phone
        self.process = process
        self.page_index = page_index
        self.page = page

    def __str__(self):
        return "[lawyer_name={} law_firm={} process={} page_index={} page={} lawyer_id={} phone={}]".format(
            self.lawyer_name, self.law_firm, self.process, self.page_index, self.page, self.lawyer_id, self.phone)

    def __repr__(self):
        return self.__str__()

    @property
    def schema_search(self):
        """
        组装搜索条件
        :return:
        """
        return "律所:{},律师:{}".format(self.law_firm, self.lawyer_name)

    @staticmethod
    def mock_data():
        return LawyerInfoBean(lawyer_id="012632c8aa51ee98c1c1d8472daee9b5", lawyer_name="黄晓伟", law_firm="江苏博爱星律师事务所",
                              phone="13358162629", process=LawyerInfoBean.PROCESS_1)


class CaseLawyerContextBean(object):
    """
    律师加密目录文档
    """
    STATUS_00 = "00"  # 未解析状态
    STATUS_01 = "01"  # 正在解析
    STATUS_09 = "09"  # 解析失败
    STATUS_10 = "10"  # 解析入库成功

    def __init__(self, id, lawyer_id, json_batch_count, page_json, index, page_num, status):
        self.id = id
        self.lawyer_id = lawyer_id
        self.json_batch_count = json_batch_count
        self.page_json = page_json
        self.index = index
        self.page_num = page_num
        self.status = status


class CaseLawyerDocBean(object):
    # ----------------step1---------------------
    SYNC_STATUS_00 = "00"  # 未获取java_script
    SYNC_STATUS_01 = "01"  # 正在获取java_script内容中
    SYNC_STATUS_07 = "07"  # 文档不存在
    SYNC_STATUS_09 = "09"  # 获取java_script失败
    SYNC_STATUS_10 = "10"  # 获取java_script成功
    # ----------------step2---------------------
    SYNC_STATUS_11 = "11"  # 格式化中
    SYNC_STATUS_19 = "19"  # 格式化失败
    SYNC_STATUS_20 = "20"  # 格式化成功
    # ----------------step3---------------------
    SYNC_STATUS_21 = "21"  # 同步数据中
    SYNC_STATUS_29 = "29"  # 同步失败
    SYNC_STATUS_30 = "30"  # 同步成功
    # ----------------exception---------------------
    SYNC_STATUS_0E = "0E"  # 以前存在文档,在需要再下载

    def __init__(self, doc_id, lawyer_id, spider_id, sync_status):
        self.doc_id = doc_id
        self.lawyer_id = lawyer_id
        self.spider_id = spider_id
        self.sync_status = self.sync_status
