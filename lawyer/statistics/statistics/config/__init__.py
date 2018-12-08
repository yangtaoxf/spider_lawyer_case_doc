import os

ADS_FIELD = {
    '201': '刑事辩护',
    '206': '海事海商',
    '207': '国际贸易',
    '208': '国际运输',
    '209': '交通事故',
    '210': '劳动纠纷',
    '211': '赡养抚养',
    '212': '继承',
    '213': '离婚纠纷',
    '214': '医疗纠纷',
    '215': '名誉侵权',
    '216': '人身损害',
    '217': '财产损害',
    '218': '网络购物',
    '219': '借贷纠纷',
    '220': '房产纠纷',
    '221': '建筑工程',
    '222': '装修工程',
    '223': '合伙联营',
    '224': '招标投标',
    '225': '矿产资源',
    '226': '股权',
    '227': '公司解散',
    '228': '证券期货',
    '229': '行政诉讼',
    '231': '土地纠纷',
    '232': '保险理赔',
    '233': '外商投资',
    '234': '抵押担保',
    '235': '知识产权',
    '236': '银行卡纠纷',
    '237': '反垄断与不正当竞争',
    '238': '合同纠纷',
    '239': '其他',
}

CERT_CONSTANT = {
    # 1为专职、2为兼职、3为香港、4为、澳门、5为台湾、6为公职、7为公司、8为法律援助、9为军队
    "1": "专职",
    "2": "兼职",
    "3": "香港",
    "4": "澳门",
    "5": "台湾",
    "6": "公职",
    "7": "公司",
    "8": "法律援助",
    "9": "军队",
    "0": "其它"
}

case = ["案例总数量", ]
case.extend(ADS_FIELD.values())
TITLE_DICT = {
    "律师ID": [],
    "律师姓名": [],
    "律师手机号": [],
    '基本资料': ["年龄", "性别", "身份证号"],
    "律师认证情况": ['注册类型', '注册时间', '认证状态', '执业年限', '执业类别', '执业证号'],
    "执业地区": ["省", "市", "区"],
    "家乡地区": ["省", "市", "区"],
    "诉保订单量": [],
    "案件合作订单量": ["发单量", "接单量"],
    "用户机型": ["手机系统", "机型号"],
    "案例数量": case,
}


class AreaBean(object):
    def __init__(self, code, name, city_id, parent_code):
        self.code = code
        self.name = name
        self.city_id = city_id
        self.parent_code = parent_code

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class AreaTool(object):
    data_dict = {}
    if not data_dict:
        with  open(os.path.dirname(os.path.abspath(__file__)) + "/area.txt", 'r', encoding="utf-8") as r:
            for line in r.readlines():
                _line = line.strip(os.linesep)
                if _line:
                    _ret = _line.split("|")
                    if len(_ret) == 4:
                        bean = AreaBean(*_ret)
                        data_dict[_ret[0]] = bean

    @staticmethod
    def query_name(*code):
        print(code)
        _code = "".join(code).ljust(6, '0')
        _ret = _code
        bean = AreaTool.data_dict.get(_code)
        if bean:
            _ret = bean.name
        return _ret


class ProvinceBean(object):
    def __init__(self, province_id, province_name):
        self.province_id = province_id
        self.province_name = province_name

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class CityBean(object):
    def __init__(self, city_id, city_name):
        self.city_id = city_id
        self.city_name = city_name

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class ProvinceTool(object):
    # from xml.dom.minidom import parse
    # import xml.dom.minidom
    # dom_tree = xml.dom.minidom.parse(os.path.dirname(os.path.abspath(__file__)) + "/province_city.xml")
    # collection = dom_tree.documentElement
    # PROVINCES = collection.getElementsByTagName("PROVINCES")
    # import lxml
    # lxml.etree.xml("")
    # for province in PROVINCES:
    #     province.getElementsByTagName("")
    #     print(province.tagName)
    # print(PROVINCES)
    from lxml import etree
    PROVINCE_DICT = {}
    CITY_DICT = {}
    xml_file = etree.parse(os.path.dirname(os.path.abspath(__file__)) + "/province_city.xml")
    provinces_data = xml_file.xpath("/ROOT/PROVINCES/RECORD")
    for _province_data in provinces_data:
        province_id = _province_data.find("N_PROVID").text
        province_name = _province_data.find("S_PROVNAME").text
        # bean = ProvinceBean(province_id=province_id, province_name=province_name)
        PROVINCE_DICT[province_id] = province_name

    citys_data = xml_file.xpath("/ROOT/CITYS/RECORD")
    for city_data in citys_data:
        city_id = city_data.find("N_CITYID").text
        city_name = city_data.find("S_CITYNAME").text
        # bean = CityBean(city_id=city_id, city_name=city_name)
        CITY_DICT[city_id] = city_name
