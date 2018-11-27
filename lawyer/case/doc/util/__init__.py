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


_test = "w61aw4tuwoMwEMO8FsKiHGxRw7UHUE7DucKEHFcWwqpIwppwSMKoHHrCisOyw68FSgkPw7NIwrENIiPCocKNbMOvemdmw70AKcOrU8K4P1wDGX7DhcKbXSzDg8OLw7HDvVNGw6fDrcOpQ27Co8O9woHCucKOSwJmw5bDpg0iw4DCvMOGClkCwpEXw5nCrjjClVBbGMOoDmVhUD0owobDokIJaALDqsKQA8O8IQIIQxjCqAPDlsOQCcOkQAkVwoDDgULCmMKhw6HCnsOnb1ZBdMK5w4bDsjvCiCPCucOyfMOyRcOyMMOmw57DrsKpW8Oxw5zDrsKcfiMpMULCuMOMw4kGOFXDp0wHw7pHwrLDpsO6w7HDrwRiaXfDokFOOkLCgsKSwp9aw4LCqsK7wpMHwrQnwqvDoVbDunZiKsOPwqbDri9SZcKowpsSNSAoOXTDjF3CgBzCpmjCqcOZC3vCoMOHM25Pw7vDvi9gRMOUw5hQLcOxw7XCosOqwppSH8K4wpZ9NGjCk2tNb1QqY8KAwrXCrsKSwpbCs8OFEGrCs8KaWE1hczvDmCHCo8OcDV3Dly1VLsKDesObIsOoKWRaID3DgzXCtMKywrrCpyhMTsOrw6/CtVIbFsO7XMO6w5NOwoTDiWrDrmVcUAvCumbDpwsgR8ORwrwLw43CvVLCmsOVS8OxwpXDlyBHwpXDo07DnVvCnsKQRnzCp8OOSDzDoCnCpcOlwox7Pw=="
_value = "FcOMw4kRA0EIw4DDgMKUOAd4csOmH8KSw5dfVcK1wpI0UMOFw4/CsQktZVMgUcKCCkBWV0vDjsKlH8KPHhhhwokMW8OFCsOcwqzDjV0yXEQvXcOZBTERPiwGwoDCh0x8Fk/Dv8KkwqB4woTDg14PSMKLwp0GUT1WTcOvwpZwXRBnw4LCgTrCo0DDkg4fYMOLw7bDvBJ8w7BaZsKDIcKzwpY6w59ZwpbDoD3DosKeHn57wo3DtMKdGsOgfMO5Bw=="

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


def mock():
    decrypt_id(_test, _value)
