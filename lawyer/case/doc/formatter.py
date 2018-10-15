# coding:utf8
import logging

_css_change_map = {
    'FONT-SIZE: 16pt': 'FONT-SIZE: 12pt',
    'FONT-SIZE: 22pt': 'FONT-SIZE: 18pt',
    'FONT-SIZE: 26pt': 'FONT-SIZE: 18pt',
    'LINE-HEIGHT: 25pt': 'LINE-HEIGHT: 20pt',
    'LINE-HEIGHT: 30pt': 'LINE-HEIGHT: 25pt',
}

_templete_DivContent = '<div id="DivContent" style="TEXT-ALIGN: justify; text-justify: inter-ideograph;">{}</div>'


# HTML转义
def html_css_format(html_context):
    if html_context == None or html_context == "":
        return None
    for old, new in _css_change_map.items():
        html_context = html_context.replace(old, new)
    return _templete_DivContent.format(html_context)


# 擅长领域字典
_master_skill_domian = [
    {"key": "201", "value": "毒品犯罪", "column": "案件名称", "keyword": ["毒品"]},
    {"key": "202", "value": "刑事自诉", "column": "案件名称",
     "keyword": ["侮辱罪", "诽谤罪", "虐待罪", "遗弃罪", "暴力干涉婚姻自由罪", "重婚罪", "侵占罪"]},
    {"key": "203", "value": "职务犯罪", "column": "案件名称",
     "keyword": [
         "贪污罪 ", "挪用 ", "受贿罪 ", "行贿罪  ", "巨额财产来源不明罪 ", "隐瞒境外存款罪 ", "私分国有资产罪 ", "私分罚没财物罪", "滥用职权罪",
         "玩忽职守罪", "泄露国家秘密罪", "枉法", "私放在押人员罪", "失职致使在押人员脱逃罪", "徇私舞弊", "失职罪", "放纵"]
     },
    {"key": "204", "value": "经济犯罪", "column": "案件名称",
     "keyword": ["法吸收公众存款罪", "集资诈骗罪", "贷款诈骗罪", "票据诈骗罪", "金融凭证诈骗罪", "信用证诈骗罪", "保险诈骗罪", "合同诈骗罪", "非法经营罪", "洗钱罪", "逃汇罪"]},
    {"key": "205", "value": "国家赔偿", "column": "案件名称", "keyword": ["刑事赔偿", "国家赔偿", "行政赔偿", "赔偿决定书", "赔偿判决书"]},
    {"key": "206", "value": "海事海商", "column": "案件名称",
     "keyword": ["船舶", "海上", "通海水域", "航次", "渔船", "海运集装箱", "港口", "理货", "船员", "海事", "航道", "港口", "船坞", "码头", "海损", "海洋",
                 "海运", "船载", "船用"]},
    {"key": "207", "value": "国际贸易", "column": "案件名称", "keyword": ["进出口", "国际货物买卖"]},
    {"key": "208", "value": "国际运输", "column": "案件名称", "keyword": ["国际铁路", "多式联运"]},
    {"key": "209", "value": "交通事故", "column": "案件名称", "keyword": ["交通事故"]},
    {"key": "210", "value": "劳动纠纷", "column": "案件名称",
     "keyword": ["劳动", "劳务", "社会保险", "待遇纠纷", "人事", "辞职", "辞退", "经济补偿", "竞业限制", "集体合同"]},
    {"key": "211", "value": "赡养抚养", "column": "案件名称", "keyword": ["赡养", "抚养费", "抚养关系", "收养", "监护权", "探望权"]},
    {"key": "212", "value": "继承", "column": "案件名称", "keyword": ["继承", "遗赠", "扶养协议"]},
    {"key": "213", "value": "离婚纠纷", "column": "案件名称", "keyword": ["婚约", "离婚", "婚姻无效", "夫妻", "同居"]},
    {"key": "214", "value": "医疗纠纷", "column": "案件名称", "keyword": ["医疗", "患者"]},
    {"key": "215", "value": "名誉侵权", "column": "案件名称", "keyword": ["姓名权", "肖像权", "名誉权", "荣誉权", "隐私权", "人格权"]},
    {"key": "216", "value": "人身损害", "column": "案件名称",
     "keyword": ["人身损害", "安全保障义务", "公共场所管理人", "群众性活动组织者", "教育机构", "高度危险责任", "物件损害", "防卫过当", "紧急避险"]},
    {"key": "217", "value": "财产损害", "column": "案件名称",
     "keyword": ["财产损害", "财产保全损害", "先予执行损害", "占有物", "遗失物", "漂流物", "埋藏物", "隐藏物", "车位", "车库", "返还原物", "排除妨害", "消除危险",
                 "修理", "重作", "更换", "物权确认", "所有权确认", "用益物权确认", "不动产登记", "异议登记不当", "虚假登记损害"]},
    {"key": "218", "value": "网络购物", "column": "案件名称", "keyword": ["网络购物"]},
    {"key": "219", "value": "借贷纠纷", "column": "案件名称", "keyword": ["借款", "拆借", "借贷"]},
    {"key": "220", "value": "房产纠纷", "column": "案件名称", "keyword": ["房屋", "商品房", "经济适用房", "建筑物区分所有权", "业主专有权", "业主共有权"]},
    {"key": "221", "value": "建筑工程", "column": "案件名称",
     "keyword": ["房地产开发", "委托代建", "开发房地产", "项目转让", "建设工程", "铁路修建", "农村建房"]},
    {"key": "222", "value": "装修工程", "column": "案件名称", "keyword": ["装饰", "装修"]},
    {"key": "223", "value": "合伙联营", "column": "案件名称", "keyword": ["入伙", "退伙", "合伙"]},
    {"key": "224", "value": "招标投标", "column": "案件名称", "keyword": ["招标投标"]},
    {"key": "225", "value": "矿产资源", "column": "案件名称", "keyword": ["探矿权", "采矿权", "自然资源"]},
    {"key": "226", "value": "股权", "column": "案件名称", "keyword": ["出资人", "公司制改造", "股份合作制改造", "股东", "股权"]},
    {"key": "227", "value": "公司解散", "column": "案件名称", "keyword": ["解散", "清算", "破产"]},
    {"key": "228", "value": "证券期货", "column": "案件名称", "keyword": ["证券", "债券", "股票", "国债", "期货"]},
    {"key": "229", "value": "行政诉讼", "column": "案件名称", "keyword": ["行政"]},
    {"key": "230", "value": "刑事辩护", "column": "案件名称", "keyword": ["刑事"]},
    {"key": "231", "value": "土地纠纷", "column": "案件名称", "keyword": ["土地", "承包地", "建设用地", "宅基地", "地役权", "临时用地"]},
    {"key": "232", "value": "保险理赔", "column": "案件名称", "keyword": ["保险合同", "保险经纪", "保险代理", "保险费"]},
    {"key": "233", "value": "外商投资", "column": "案件名称", "keyword": ["中外合资", "中外合作", "外商独资"]},
    {"key": "234", "value": "抵押担保", "column": "案件名称", "keyword": ["抵押权", "质权", "保证合同", "质押"]},
    {"key": "235", "value": "知识产权", "column": "案件名称",
     "keyword": ["著作权", "创作 ", "发明", "出版", "表演", "音像", "邻接权", "计算机", "商标", "专利", "新品种", "集成电路", "秘密技术", "企业名称", "特殊标志",
                 "网络域名", "知识产权", "作品"]},
    {"key": "236", "value": "银行卡纠纷", "column": "案件名称", "keyword": ["借记卡", "信用卡", "银行卡"]},
    {"key": "237", "value": "反垄断与不正当竞争", "column": "案件名称",
     "keyword": ["仿冒", "不正当竞争", "虚假宣传", "侵害商业秘密", "侵害技术秘密", "侵害经营秘密", "有奖销售", "商业诋毁", "垄断", "滥用市场支配地位", "掠夺定价", "拒绝交易",
                 "限定交易", "捆绑交易", "差别待遇", "经营者集中"]},
    {"key": "238", "value": "合同纠纷", "column": "案件名称", "keyword": ["合同", "债权", "债务"]},
    {"key": "239", "value": "其他", "column": "案件名称", "keyword": []},
    {"key": "240", "value": "互联网金融"},
    {"key": "241", "value": "财税"},
    {"key": "242", "value": "跨境电商"},
    {"key": "243", "value": "IPO"},
    {"key": "244", "value": "私募投资"},
    {"key": "245", "value": "新三板"},
    {"key": "246", "value": "不良资产处置"}
]


# 根据标题擅长领域分类
def lawyer_case_case_type(title, page):
    # 默认239其他
    ret_key = "239"
    for it in _master_skill_domian:
        key = it.get("key")
        keyword = it.get("keyword");
        if keyword is not None and keyword != "":
            for keyword_sub in keyword:
                match = title is not None and keyword_sub in title or keyword_sub in page
                if match:
                    ret_key = key
                    logging.info('match ret_key==>' + ret_key)
                    return ret_key
    logging.info("default ==>" + ret_key)
    return ret_key
