import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_excel("./统计表.xls", sheet_name="认证律师用户画像")
data = data.iloc[1:, 18:19]
print(data)
print(type(data))

r = data.rolling(window=10, min_periods=1)
print(r.aggregate(np.sum))

print(data.rolling(window=1).mean())

# df = pd.DataFrame((123, 123, 123, 123), index=['a', 'b', 'c', 'd'], columns=['x'])
data.plot.pie(subplots=True, explode=[0, 0.1, 0, 0])
# labels = ('A', 'B', 'C', 'D')
# fracs = [15, 30.55, 44.44, 10]
# explode = [0, 0.1, 0, 0]  # 0.1 凸出这部分，
# plt.axes(aspect=1)  # set this , Figure is round, otherwise it is an ellipse
# # autopct ，show percet
# plt.pie(x=fracs, labels=labels, explode=explode, autopct='%3.1f %%',
#         shadow=True, labeldistance=1.1, startangle=90, pctdistance=0.6
#
#         )
'''
labeldistance，文本的位置离远点有多远，1.1指1.1倍半径的位置
autopct，圆里面的文本格式，%3.1f%%表示小数有三位，整数有一位的浮点数
shadow，饼是否有阴影
startangle，起始角度，0，表示从0开始逆时针转，为第一块。一般选择从90度开始比较好看
pctdistance，百分比的text离圆心的距离
patches, l_texts, p_texts，为了得到饼图的返回值，p_texts饼图内部文本的，l_texts饼图外label的文本
'''

plt.show()
