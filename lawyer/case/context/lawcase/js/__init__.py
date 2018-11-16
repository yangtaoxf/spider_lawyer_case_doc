import logging
import os
import sys

wen_shu_js = ""
current_Path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_Path)[0]
sys.path.append(root_path)
print()
with open(current_Path + "/md5_20180820.js") as f:
    wen_shu_js += f.read()
with open(current_Path + "/base64_200180820_1.js") as f:
    wen_shu_js += f.read()
with open(current_Path + '/Base64_20180820.js') as f:
    wen_shu_js += f.read()
with open(current_Path + "/sha1.js") as f:
    wen_shu_js += f.read()
with open(current_Path + '/rawinflate_20180820.js') as f:
    wen_shu_js += f.read()
with open(current_Path + "/wenshu_20180820.js") as f:
    wen_shu_js += f.read()
# logging.info(wen_shu_js)
