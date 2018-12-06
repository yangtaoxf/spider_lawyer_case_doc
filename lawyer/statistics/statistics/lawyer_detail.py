# coding=utf-8

import xlwt
import logging
from xlwt import *

workbook = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = workbook.add_sheet('认证律师用户画像', cell_overwrite_ok=True)
style = XFStyle()  # 赋值style为XFStyle()，初始化样式
font = xlwt.Font()  # 字体基本设置
font.name = u'Cambria'
font.color = 'black'
font.height = 220  # 字体大小，220就是11号字体，大概就是11*20得来的吧
style.font = font


class TitleRow(object):

    def __init__(self, sheet, **kwargs):
        self.title_dict = {}
        self.sheet = sheet
        index = 0
        for key, value in kwargs.items():
            sheet.write(0, index, key, style=style)
            index += 1


class LawyerBean(object):
    def __init__(self, *args, **kwargs):
        self.age = kwargs.get("age")
        self.id_card_no = kwargs.get("id_card_no")
        self.proceed_id_card_no()

    def is_second_generation_identity_card(self):
        return len(self.id_card_no) == 18

    def proceed_id_card_no(self):
        if self.is_second_generation_identity_card():
            print(self.id_card_no)
            birth_year = self.id_card_no[6:10]
            sex_num = self.id_card_no[16:17]  # 第17位数字表示性别：奇数表示男性，偶数表示女性
            if (int(sex_num) % 2) == 0:
                self.sex = "女"
            else:
                self.sex = "男"
            provice = self.id_card_no[0:2]
            city = self.id_card_no[2:4]
            town = self.id_card_no[4:6]
            self.provice = provice
            self.city = city
            self.town = town

            # 前1、2
            # 位数字表示：所在省份的代码；（2）第3、4
            # 位数字表示：所在城市的代码；（3）第5、6
            # 位数字表示：所在区县的代码；
            print(sex_num)
            print(birth_year)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


lawyer = LawyerBean(age="111", id_card_no="511322198803156853")
print(lawyer)
print(lawyer.is_second_generation_identity_card())
print(lawyer.proceed_id_card_no())
print(lawyer.sex)

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
TitleRow(sheet=sheet, **title_dict)

# sheet.write(0, 0, 'EnglishName', style=style)  # 其中的'0-行, 0-列'指定表中的单元，'EnglishName'是向该单元写入的内容
# sheet.write(1, 0, 'Marcovaldo', style=style)
txt2 = '马可瓦多'
sheet.write(1, 1, txt2, style=style)

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
TitleRow(sheet=sheet, **title_dict)
# ---------------------------
workbook.save(r'.\统计表.xls')
