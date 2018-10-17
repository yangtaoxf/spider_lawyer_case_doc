# coding=utf8
import os
import time
import re
import execjs

__all__ = ["get_linux_time"]

print(execjs.get().name)
os.environ["NODE_PATH"] = os.getcwd() + "/node_modules"
print(execjs.get().name)


def get_linux_time():
    """
    获取linux 10位时间戳
    :return:
    """
    return time.time().__int__()


with open(os.curdir + "/../js/list_context_parser.js") as f:
    doc_id_js = f.read()

with open(os.curdir + "/../js/test.js") as f:
    doc_id_js += f.read()
# def un_zip_key(source_key):
#     return execjs.compile(doc_id_js).call('GetJs', source_key)
#
#
# def un_zip_doc_id(up_zip_key, source_doc_id):
#     context = execjs.compile(doc_id_js)
#     context.call('UpdateKey', up_zip_key)
#     return context.call('DecryptDocID', up_zip_key, source_doc_id)


_test = "w61aw4tuwoMwEMO8FsKiHGxRw7UHUE7DucKEHFcWwqpIwppwSMKoHHrCisOyw68FSgkPw7NIwrENIiPCocKNbMOvemdmw70AKcOrU8K4P1wDGX7DhcKbXSzDg8OLw7HDvVNGw6fDrcOpQ27Co8O9woHCucKOSwJmw5bDpg0iw4DCvMOGClkCwpEXw5nCrjjClVBbGMOoDmVhUD0owobDokIJaALDqsKQA8O8IQIIQxjCqAPDlsOQCcOkQAkVwoDDgULCmMKhw6HCnsOnb1ZBdMK5w4bDsjvCiCPCucOyfMOyRcOyMMOmw57DrsKpW8Oxw5zDrsKcfiMpMULCuMOMw4kGOFXDp0wHw7pHwrLDpsO6w7HDrwRiaXfDokFOOkLCgsKSwp9aw4LCqsK7wpMHwrQnwqvDoVbDunZiKsOPwqbDri9SZcKowpsSNSAoOXTDjF3CgBzCpmjCqcOZC3vCoMOHM25Pw7vDvi9gRMOUw5hQLcOxw7XCosOqwppSH8K4wpZ9NGjCk2tNb1QqY8KAwrXCrsKSwpbCs8OFEGrCs8KaWE1hczvDmCHCo8OcDV3Dly1VLsKDesObIsOoKWRaID3DgzXCtMKywrrCpyhMTsOrw6/CtVIbFsO7XMO6w5NOwoTDiWrDrmVcUAvCumbDpwsgR8ORwrwLw43CvVLCmsOVS8OxwpXDlyBHwpXDo07DnVvCnsKQRnzCp8OOSDzDoCnCpcOlwox7Pw=="
_value = "FcOMw4kRA0EIw4DDgMKUOAd4csOmH8KSw5dfVcK1wpI0UMOFw4/CsQktZVMgUcKCCkBWV0vDjsKlH8KPHhhhwokMW8OFCsOcwqzDjV0yXEQvXcOZBTERPiwGwoDCh0x8Fk/Dv8KkwqB4woTDg14PSMKLwp0GUT1WTcOvwpZwXRBnw4LCgTrCo0DDkg4fYMOLw7bDvBJ8w7BaZsKDIcKzwpY6w59ZwpbDoD3DosKeHn57wo3DtMKdGsOgfMO5Bw=="


# doc_id = decrypt_id(_test, _value)
# print(doc_id)


def decrypt_run_eval(RunEval):
    """
    doc_id解密
    """
    context = execjs.compile(doc_id_js)
    docid = context.call("unzip", RunEval)
    return docid


def run_eval_parser(run_eval, context):
    print(context.call("run_eval_parser", run_eval))


def real_id(_id, _update_key, context):
    return context.call("real_id", _id, _update_key)


def decrypt_id(RunEval, id, _context):
    """
    docid解密
    """
    js = _context.call("run_eval_parser", RunEval)
    js_objs = js.split(";;")
    js1 = js_objs[0] + ';'
    print(js1)
    js2 = re.findall(r"_\[_\]\[_\]\((.*?)\)\(\);", js_objs[1])[0]
    print(js2)
    key = _context.call("EvalKey", js1, js2)
    print("key=" + key)
    key = re.findall(r"\"([0-9a-z]{32})\"", key)[0]
    docid = _context.call("DecryptDocID", key, id)
    print(docid)
    return docid


def query_key(context):
    _query_key = context.call("query_key")
    return _query_key


# run_eval_parser(_test, _context)
# _key = query_key(_context)
# _ret = real_id(_value, None, _context)
# print(_ret)
_context = execjs.compile(doc_id_js)


# decrypt_id(_test, _value, _context)


def hello():
    _hello = execjs.compile(doc_id_js).call("hello")
    print(_hello)


hello()


def unzip_id(_id, _context):
    un_zip_id = _context.call("unzip", _id)
    return un_zip_id


"""
 function Navi(id, keyword) {
    var unzipid = unzip(id);
    try {
        var realid = com.str.Decrypt(unzipid);
        if (realid == "") {
            setTimeout("Navi('" + id + "','" + keyword + "')", 1000);
        } else {
            var url = "/content/content?DocID=" + realid + "&KeyWord=" + encodeURI(keyword); 
            openWin(url);
        }
    } catch (ex) {
        setTimeout("Navi('" + id + "','" + keyword + "')", 1000);
    }
}
"""

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
