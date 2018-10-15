# coding=utf8
import time
import execjs
import os
import re

__all__ = ["get_linux_time"]


def get_linux_time():
    """
    获取linux 10位时间戳
    :return:
    """
    return time.time().__int__()


with open(os.curdir + "/../js/doc_id.js") as f:
    doc_id_js = f.read()


def un_zip_key(source_key):
    return execjs.compile(doc_id_js).call('GetJs', source_key)


def un_zip_doc_id(up_zip_key, source_doc_id):
    context = execjs.compile(doc_id_js)
    context.call('UpdateKey', up_zip_key)
    return context.call('DecryptDocID', up_zip_key, source_doc_id)


def decrypt_id(RunEval, id):
    """
    doc_id解密
    """
    context = execjs.compile(doc_id_js)
    js = context.call("GetJs", RunEval)
    js_objs = js.split(";;")
    js1 = js_objs[0] + ';'
    js2 = re.findall(r"_\[_\]\[_\]\((.*?)\)\(\);", js_objs[1])[0]
    print(js1)
    print(js2)
    key = context.call("EvalKey", js1, js2)
    print(key)
    key = re.findall(r"\"([0-9a-z]{32})\"", key)[0]
    docid = context.call("DecryptDocID", key, id)
    return docid


_test = "w61aw4tuwoMwEMO8FsKiHGxRw7UHUE7DucKEHFcWwqpIwppwSMKoHHrCisOyw68FSgkPw7NIwrENIiPCocKNbMOvemdmw70AKcOrU8K4P1wDGX7DhcKbXSzDg8OLw7HDvVNGw6fDrcOpQ27Co8O9woHCucKOSwJmw5bDpg0iw4DCvMOGClkCwpEXw5nCrjjClVBbGMOoDmVhUD0owobDokIJaALDqsKQA8O8IQIIQxjCqAPDlsOQCcOkQAkVwoDDgULCmMKhw6HCnsOnb1ZBdMK5w4bDsjvCiCPCucOyfMOyRcOyMMOmw57DrsKpW8Oxw5zDrsKcfiMpMULCuMOMw4kGOFXDp0wHw7pHwrLDpsO6w7HDrwRiaXfDokFOOkLCgsKSwp9aw4LCqsK7wpMHwrQnwqvDoVbDunZiKsOPwqbDri9SZcKowpsSNSAoOXTDjF3CgBzCpmjCqcOZC3vCoMOHM25Pw7vDvi9gRMOUw5hQLcOxw7XCosOqwppSH8K4wpZ9NGjCk2tNb1QqY8KAwrXCrsKSwpbCs8OFEGrCs8KaWE1hczvDmCHCo8OcDV3Dly1VLsKDesObIsOoKWRaID3DgzXCtMKywrrCpyhMTsOrw6/CtVIbFsO7XMO6w5NOwoTDiWrDrmVcUAvCumbDpwsgR8ORwrwLw43CvVLCmsOVS8OxwpXDlyBHwpXDo07DnVvCnsKQRnzCp8OOSDzDoCnCpcOlwox7Pw=="
_value = "FcOMw4kRA0EIw4DDgMKUOAd4csOmH8KSw5dfVcK1wpI0UMOFw4/CsQktZVMgUcKCCkBWV0vDjsKlH8KPHhhhwokMW8OFCsOcwqzDjV0yXEQvXcOZBTERPiwGwoDCh0x8Fk/Dv8KkwqB4woTDg14PSMKLwp0GUT1WTcOvwpZwXRBnw4LCgTrCo0DDkg4fYMOLw7bDvBJ8w7BaZsKDIcKzwpY6w59ZwpbDoD3DosKeHn57wo3DtMKdGsOgfMO5Bw=="
doc_id = decrypt_id(_test, _value)
print(doc_id)
"""
function GetJs(RunEval){
    return unzip(RunEval);
}
function EvalKey(js1, js2){
    eval(js1);
    return eval(js2);
}
function UpdateKey(key){
    com.str._KEY = key;
}
function DecryptDocID(key, id){
    if(key){
        UpdateKey(key);
    }
    var unzipid = unzip(id);
    var realid = com.str.Decrypt(unzipid);
    return realid;
}
"""
