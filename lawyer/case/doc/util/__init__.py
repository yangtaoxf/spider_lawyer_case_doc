# coding=utf8
import logging
import sys
import re
import time
import os
import execjs
from util.decorator import log_cost_time

current_Path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(current_Path)[0]
print(root_path)
sys.path.append(root_path)
__all__ = ["get_linux_time", "decrypt_id", "_test", "_value"]
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode='a', )
logging.info(execjs.get().name)
with open(root_path + "/js/list_context_parser.js") as f:
    doc_id_js = f.read()


def get_linux_time():
    """
    获取linux 10位时间戳
    :return:
    """
    return time.time().__int__()


_test = "w61aw51uwoIwFH4WwowXbVjDtgLDhCsfYcKXJw0xw6gmF8KTwqXCsivDo8K7D8KYdkBbw5HDkSLDqMKXwpBjw5rCnsK/w687wofCtiTDjsK3w6l6wrNPZMO6wpUvw55ywpnDrj5ew59lw7bCucOcwq7DpDJbb1gYwoQkIEYtXkACw4RzdMOIIwB5wpLDlxXCuxJqCwHDnsOBLATCqgfDhlBcwpAAJsOACQDCgx1ABzFADcO8wqADPAEcIMKhAhBowoQRCh5Fw7FiwpZkwrt9LsK/wpM8wpPCsyjCplgUD2PDocOhWMKqwqnDp3DDpMO0a0nChRAiZEHCtcOAwqnDqcKzXMOoXsKpwobDs8K/fycQK8KnCw0Kw4oVElTDvMK0AjbDlcKDwpPCgT1YK2/Co8Ouw4XCnMOqw57DjMOzKlTClcK1TsKRwpbCghHDgwXDnyrDicOrGMKtDTvDk8K+UsOjFsK1wpt1w79nw5DDg8Kqwq9pwrseDsK8OUnDicKHJx/DrsK8w7nDtMOrWCvCu3nDrMKYeXvCuDF1wp1fw5LDj8OQbTvCrMKnCsKowr3Du3wSw7nCgsObOCTCjMK1H8KEw6HCoSo5fDB7w6/DuMOdK8KcwrxZw6bDnnjDgG5QXW/Cu8Oow7Q9wrHCh8OGw5Idw7ZOOQ0VeyoXwodJXXAmwpPDgCkLw70Gc8KHY8ONCV/Chm8rDRw1bgzDpsOZwrpDw6rDsXU4IsOywpBPLSxnPMO6AQ=="
_value1 = "FcKOw4kNRDEIw4VaYn3CgWMIw5B/ScOzw6dqWcKyw5PDn8OmYsOlwqRmwrpYwosJw5LCh8KXHDbDgyopacKEwqM3X2ctw5jCkxQcwp/CvcKDwobDi1JpJXoSHsOjwofCjgsqFGPDmjDCumJ5T8OFwqPClcKrw4dML8O/MQ7DoTlawqMRNcO9SDUew6QWw7EIw43DnMKoZEbCkcK8w6Btw7TCuWnDik/DiWc9cl7CrcO1wp5vasOqwrvDuDIXw5p8wpfDl153w78A"
_value2 = "FcKMwrcRA0EQwoBaWm/DgnXDl39JesKlDFDDrMK4wo/CisKAQsKoLHbDmx/ChDV4acOCwro2JsKCRSYIw6QqR8KJImLDoD/CqUbDiMKMw5INwqc+wpDDvcKSKz/DkHddw44fEMOkRcK7wollVEPDgMKqwrfChMOFN8Kdw7PDjsOdw5FHQ1cpGcOzwrvCnMK5CS3DsMOVUkrCvDfDigLDkXknw6zDjkTDsynCiCYww7zDjQBmNMOPelLCqWPDvHHCmDTDvAA="
_value3 = "DcKNwrcNw4BADMOEVlLDlsKrVMOcfyTCuzrCgDjCghXDvlTCkHHCscOgwp/Cl8KxbkXDjSzCjSrDt8KDwqZWw6PClsOtDMKHEBHDt8KwUcOTwrzDlBwZwrxzw7nCtT7ChsOoTsOjSAt3GsKEw7JKFsKiwrcHYsK5aW5TTyjCoVnDocKAcsKmWlfDgypyLcKtwp7Dgz5oBcK4O8K+wpbDt8OMXH7DuCdUVHvCkVAXGyB7DsKCw5fClsOGTcKywpTDvh/Dn19Ww54P"
_value4 = "DcONwrkRADEIBMOBwpRAwrwyYUHDucKHdMOnw49UZxE7BQYZwqYpw6/DqhnCjcKdTWFPCwTDsBdoYcOTe8Kiw4vCuFIpwrM1A8KiwpU1FsOTwrh9BHzDg3LDhMONw5oDa2QvOMOIw70ewqUjesOgc1XCvWTCo8K8wrrDvMKiwpzCicOewrsUwo/CmX/DqMOnHMKlWDRrw7s8w7zDrAvCnMK3wrQgI8OPwrciwqp7woIxw60gw4dMwpnDjMO8C8Ohw442w7kUwp0P"
_value5 = "FcKOwrcBA0EMw4NWUg7CpcOSw60/wpLDnw0LFAAlw5rCsx9IIwEfwq8BwoDDj8Kga8Oow57CuzxOwpElwqbCg8Kaw5Uwwr/Dlx7Do8KDUATDisOKw586XA/CkTPCjnHDoWJdUsOVC8OTWxrDmsOMZUogWwzCkw0NwrTDuER+aWQRBGlew5A4wrzDtcO4wolewrwgUSlyw5LCqzZiBMKxEcOJw4gcwqzDly3DjcKLK8OGw7vCvn/CvMOzD8Oow5nDh8KFW1B/"
_value6 = "FcKPw4sRRDEIw4NaInwMHMKBwpDDvkvDmsK3V8KNRxrDq8K1bjVIw7rDrsOsw4Rdwptrw5RIIHpTw5w9w7ARSMK9QzxEKcOgLMOtCMKbNmDCtTHDp8OdChY/wrvCucKuMjMfOcO5N8KqwrPDnMKxN0Fpw7TCjMKfaivDt8OqSMK+w4k4BwvDj8O9ZhrCp8K+VsOcG8OUecOBwrxVw4tkwo4cwo9HYMKNecKkVcKZODfDgsOHWXvDuXvDsXnCs8KSw5pKKsKiwqHDuAE1"
_error_value7 = "DcONwrkRADEIBMOBwpRAwrwyYaInwMHMKBwpDDvkvDmsK3V8KNRxrDq8K1bjVIw7rDrsOsw4Rdwptrw5RIIHpTw5w9w7ARSMK9QzxEKcOgLMOtCMKbNmDCtTHDp8OdChY/wrvCucKuMjMfOcO5N8KqwrPDnMKxN0Fpw7TCjMKfaivDt8OqSMK+w4k4BwvDj8O9ZhrCp8K+VsOcG8OUecOBwrxVw4tkwo4cwo9Cs8KSw5pKKsKiwqHDuAE3"
_error_value8 = "FcKPw4sRRDEIw4NaInwMHMKBwpDDvkvDmsK3V8KNRxrDq8K1bjVIw7rDrsOsw4Rdwptrw5RIIHpTw5w9w7ARSMK9QzxEKcOgLMOtCMKbNmDCtTHDp8OdChY/wrvCucKuMjMfOcO5N8KqwrPDnMKxN0Fpw7TCjMKfaivDt8OqSMK+w4k4BwvDj8O9ZhrCp8K+VsOcG8OUecOBwrxVw4tkwo4cwo9Cs8KSw5pKKsKiwqHDuAE3"

_context = execjs.compile(doc_id_js)


@log_cost_time(describe="解密文档")
def decrypt_id(run_eval, _id):
    """
    解密doc_id
    """
    js = _context.call("GetJs", run_eval)
    js_objs = js.split(";;")
    js1 = js_objs[0] + ';'
    js2 = re.findall(r"_\[_\]\[_\]\((.*?)\)\(\);", js_objs[1])[0]
    key = _context.call("EvalKey", js1, js2)
    key = re.findall(r"\"([0-9a-z]{32})\"", key)[0]
    doc_id = _context.call("DecryptDocID", key, _id)
    return doc_id


@log_cost_time(describe="解密文档")
def decrypt_id_array(run_eval, _ids: list) -> dict:
    """
    解密doc_id
    """
    ret = {}
    js = _context.call("GetJs", run_eval)
    js_objs = js.split(";;")
    js1 = js_objs[0] + ';'
    js2 = re.findall(r"_\[_\]\[_\]\((.*?)\)\(\);", js_objs[1])[0]
    key = _context.call("EvalKey", js1, js2)
    key = re.findall(r"\"([0-9a-z]{32})\"", key)[0]
    doc_id_array = _context.call("DecryptDocIDArray", key, _ids)
    for i, doc_id in enumerate(_ids):
        ret[doc_id] = doc_id_array[i]
    return ret


def mock():
    decrypt_id(_test, _value1)
