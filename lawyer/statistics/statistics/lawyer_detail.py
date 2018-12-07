# coding=utf-8

import xlwt
import logging
from xlwt import *
import datetime
from statistics.config import AreaTool, ProvinceTool, ADS_FIELD, CERT_CONSTANT

# from statistics.dao import LawyerDao

YEAR = datetime.datetime.now().year  # 当前年
MONTH = datetime.datetime.now().month  # 当前月
DAY = datetime.datetime.now().day  # 当前日
workbook = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = workbook.add_sheet('认证律师用户画像', cell_overwrite_ok=True)
style = XFStyle()  # 赋值style为XFStyle()，初始化样式
font = xlwt.Font()  # 字体基本设置
font.name = u'Cambria'
font.color = 'black'
font.height = 220  # 字体大小，220就是11号字体，大概就是11*20得来的吧
style.font = font

borders = xlwt.Borders()
borders.left = 1
borders.right = 1
borders.top = 1
borders.bottom = 1
borders.bottom_colour = 0x3A
style.borders = borders


class CaseBean(object):
    def __init__(self, kwargs):
        self.total_case_num = 0
        self.ads_field = {}
        for key, value in ADS_FIELD.items():
            count = kwargs.get(key, 0)
            self.ads_field[value] = count
            self.total_case_num += count

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class LawyerBeanHelper(object):
    pass


class LawyerBean(object):
    def __init__(self, *args, **kwargs):
        self.lawyer_id = kwargs.get("id", "")
        self.lawyer_name = kwargs.get("real_name", "")
        self.phone = kwargs.get("phone", "")
        self.device_type = kwargs.get("deviceType", "")
        self.device_info = kwargs.get("deviceInfo", "")
        self.deposit_status = kwargs.get("depositStatus", "")
        self.proceed_deposit_status()
        self.id_card_no = kwargs.get("idCard", "")
        self.proceed_id_card_no()
        self.cert_num = kwargs.get("certNum", "未有职业证号")
        self.proceed_cert_num()
        self.province_id = kwargs.get("province_id", "")
        self.city_id = kwargs.get("city_id", "")
        self.proceed_work_space()
        self.case_bean = CaseBean({"201": 123})
        self.ssdb_order_num = 0
        self.ajhz_order_num = 0

    def is_second_generation_identity_card(self):
        return len(self.id_card_no) == 18

    def is_common_cert_num(self):
        return len(self.cert_num) == 17

    def proceed_deposit_status(self):
        deposit_desc = ""
        _deposit_status = str(self.deposit_status)
        if "-1" in _deposit_status:
            deposit_desc = "未付保证金"
        elif "0" in _deposit_status:
            deposit_desc = "已付保证金"
        elif "1" in _deposit_status:
            deposit_desc = "申请退保证金"
        elif "2" in _deposit_status:
            deposit_desc = "已退保证金"
        self.deposit_desc = deposit_desc

    def proceed_cert_num(self):
        self.cert_year = ""
        self.cert_now_year = ""
        self.cert_type = ""

        if self.is_common_cert_num():
            __cert_type = self.cert_num[9:10]  # 执业类别
            __cert_year = self.cert_num[5:9]
            self.cert_year = __cert_year
            self.cert_now_year = YEAR - int(__cert_year) + 1
            self.cert_type = CERT_CONSTANT.get(__cert_type)

    def proceed_work_space(self):
        self.province_name = 0
        self.city_name = 0
        if self.province_id:
            self.province_name = ProvinceTool.PROVINCE_DICT.get(str(self.province_id), self.province_id)
        if self.city_id:
            self.city_name = ProvinceTool.CITY_DICT.get(str(self.city_id), self.city_id)

    def proceed_id_card_no(self):
        self.provice = ""
        self.city = ""
        self.town = ""
        self.sex = ""
        if self.is_second_generation_identity_card():
            print(self.id_card_no)
            birth_year = self.id_card_no[6:10]
            self.age = YEAR - int(birth_year)
            sex_num = self.id_card_no[16:17]  # 第17位数字表示性别：奇数表示男性，偶数表示女性
            if (int(sex_num) % 2) == 0:
                self.sex = "女"
            else:
                self.sex = "男"
            provice = self.id_card_no[0:2]
            city = self.id_card_no[2:4]
            town = self.id_card_no[4:6]
            self.provice = AreaTool.query_name(provice)
            self.city = AreaTool.query_name(provice, city)
            self.town = AreaTool.query_name(provice, city, town)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class TitleRow(object):
    ROW = 1  # 标题2行

    def __init__(self, sheet, **kwargs):
        self.title_dict = {}
        self.sheet = sheet
        index = 0
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = Style.colour_map['yellow']  # 设置单元格背景色为黄色
        style.pattern = pattern
        for key, value in kwargs.items():
            start_index = index
            if isinstance(value, list) and value:
                for sub_value in value:
                    sheet.write(1, index, sub_value, style=style)
                    index += 1
                print(start_index, index, key)
                sheet.write_merge(0, 0, start_index, index - 1, key, style=style)
            else:
                sheet.write_merge(0, 1, start_index, index, key, style=style)
                index += 1
        style.pattern = Pattern()  # 还原回去

    def write(self, bean: LawyerBean):
        self.ROW += 1
        if bean:
            self.sheet.write(self.ROW, 0, bean.lawyer_id, style=style)
            self.sheet.write(self.ROW, 1, bean.lawyer_name, style=style)
            self.sheet.write(self.ROW, 2, bean.phone, style=style)
            self.sheet.write(self.ROW, 3, bean.age, style=style)
            self.sheet.write(self.ROW, 4, bean.sex, style=style)
            self.sheet.write(self.ROW, 5, bean.cert_now_year, style=style)
            self.sheet.write(self.ROW, 6, bean.cert_type, style=style)

            self.sheet.write(self.ROW, 7, bean.province_name, style=style)
            self.sheet.write(self.ROW, 8, bean.city_name, style=style)
            self.sheet.write(self.ROW, 9, "", style=style)  # 没有精确到区

            self.sheet.write(self.ROW, 10, bean.provice, style=style)
            self.sheet.write(self.ROW, 11, bean.city, style=style)
            self.sheet.write(self.ROW, 12, bean.town, style=style)

            self.sheet.write(self.ROW, 13, bean.ssdb_order_num, style=style)
            self.sheet.write(self.ROW, 14, bean.ajhz_order_num, style=style)
            self.sheet.write(self.ROW, 15, bean.device_type, style=style)
            self.sheet.write(self.ROW, 16, bean.device_info, style=style)
            self.sheet.write(self.ROW, 17, bean.case_bean.total_case_num, style=style)
            _index = 18
            for key, value in bean.case_bean.ads_field.items():
                self.sheet.write(self.ROW, _index, value, style=style)
                _index += 1


# _data = LawyerDao.query_by_lawyer_id("4a423e0c02b9e7aa5acf2b4d06427ac1")
# lawyer = LawyerBean(**_data)
lawyer = LawyerBean(**{'id': '4a423e0c02b9e7aa5acf2b4d06427ac1', 'address': '广州市天河路101号兴业银行大厦十三楼',
                       'briefInfo': '国信信扬律师事务所的合伙人。\n专职律师，擅长劳动法、公司法等领域的法律事务。\n同时担任广州市律师协会劳动和社会保障法律专业委员会委员、广东省律师协会劳动和社会保障法律专业委员会委员。先后担任广东省飞来峡水利枢纽管理局、广州市国土资源和房屋管理局越秀分局、广州市越秀区旧城改造项目办公室、广州市越秀区房屋租赁管理所、马士基信息处理(广东)有限公司、卓域集团有限公司、金源矿业有限公司等多个政府单位及大型企业的常年法律顾问。',
                       'caseNum': 101, 'license': '/certificate/2016/1/3/13c190a132414708b4f76547ad33917e.jpg',
                       'certificateDate': datetime.datetime(2006, 6, 1, 0, 0), 'city_id': 1292,
                       'create_date': datetime.datetime(2014, 12, 15, 0, 17, 12), 'deviceType': 'android',
                       'email': '17960413@qq.com', 'login_name': '13076828028',
                       'logo': '/logo/lawyer/2016/1/12/4a423e0c02b9e7aa5acf2b4d06427ac1.jpg', 'phone': '13076828028',
                       'moneyBlocked': 0.0, 'moneyOut': 0.0, 'moneySum': 30.049999999999997, 'law_firm': '国信信扬律师事务所',
                       'orderFlag': 1, 'password': 'fa33ab998750389624466dd272cbecaf', 'province_id': 29,
                       'real_name': '冯志成', 'recommend': 0, 'sex': 0, 'status': 4,
                       'update_date': datetime.datetime(2018, 12, 4, 14, 48, 36), 'weixin': '13076828028',
                       'evaluate_id': '4a423e0c02b9e7aa5acf2b4d06427ac1',
                       'applyDate': datetime.datetime(2016, 1, 14, 10, 25, 51), 'failType': None,
                       'certNum': '14401200610938444', 'points': 0, 'pointsExchange': 0, 'lawyerType': 0,
                       'appVersion': '5.9.1', 'deviceId': '4C643EDD-36EC-487B-80FD-E4E79325F69A',
                       'deviceInfo': 'Simulator,9.30', 'idCard': '410225198912284693',
                       'dwlsd_openid': 'oLn3Vs6NC9VMlM-Q1TvTqsRUngMo', 'moneyTj': None, 'moneyTz': None,
                       'deposit': None,
                       'depositStatus': -1, 'pointsBlocked': 0, 'pointsOut': 1000, 'pointsSum': 100000, 'channel': None,
                       'depositBackDate': None, 'stateJoin': 0, 'security': 0, 'advJoinState': 1, 'wxPush': 1,
                       'wxPushOpenId': 'oLn3Vszm0ylUD2RQqt_2fGitTq50', 'wxSsdbOpenId': None})

##################excel 标题配置 开始#####################
case = ["案例总数量", ]
case.extend(ADS_FIELD.values())
title_dict = {
    "律师ID": [],
    "律师姓名": [],
    "律师手机号": [],
    "年龄": [],
    "性别": [],
    "执业年限": "",
    "执业类别": "",
    "执业地区": ["省", "市", "区"],
    "家乡地区": ["省", "市", "区"],
    "诉保订单量": [],
    "案件合作订单量": [],
    "用户机型": ["手机系统", "机型号"],
    "案例数量": case,
}
##################excel 标题配置 结束#####################
row = TitleRow(sheet=sheet, **title_dict)
row.write(lawyer)
row.write(lawyer)
row.write(lawyer)
row.write(lawyer)

# ---------------------------
sheet = workbook.add_sheet('律师案例数据分析', cell_overwrite_ok=True)
title_dict = {
    "律师ID": "",
    "律师姓名": "",
    "律师手机号": "",
    "年龄": "11",
    "性别": "22",
    "执业地区": "",
    "家乡地区": "",
    "执业年限": "",
    "案例数量": "",
    "诉保订单": "",
    "案件合作": "",
    "保证金": "",
    "用户机型": "",
    "执业类别": "",
}
# ---------------------------
workbook.save(r'.\统计表.xls')
