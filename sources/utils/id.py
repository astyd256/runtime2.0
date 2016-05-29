
import string
import random
import math
import time
from hashlib import md5
import managers


class VDOM_id:
    """id generation class"""
    def hexstr(self, s):
        """convert byte array to hex string"""
        h = string.hexdigits
        r = ""
        for c in s:
            i = ord(c)
            r = r + h[(i >> 4) & 0xF] + h[i & 0xF]
        return r

    def new(self):
        """generate new id"""
        md5obj = md5(str(time.time() + random.random() + math.sin(random.random())))
        return self.hexstr(md5obj.digest())

    def random_string(self, length):
        """generate random string of the specified length"""
        h = string.hexdigits
        r = ""
        for i in xrange(length):
            a = random.randint(0, 255)
            r = r + h[a & 0xF]
        return r


def guid2mod(guid):
    """transform guid to module name"""
    return "module_" + "_".join(guid.split("-"))

# def id2res(owner_id, res_id, res_type):
#     transform owner id and resource id to resource name"""
#         "res_" + owner_id + "_" + res_id + "." + res_type


def id2link(res_id):
    """transform resource id to resource URL"""
    return "/%s.res" % res_id


def id2link1(res_id):
    """transform resource id to resource URL"""
    o = managers.resource_manager.get_resource(None, res_id)
    if not o:
        return ""
    return "".join(["/", res_id, ".", o.res_format])

# def id2tempres(owner_id, tempres_id, res_type):
#   """transform owner id and temporary resource id to temporary resource name"""
#   return "temp_" + owner_id + "_" + tempres_id + "." + res_type


def is_valid_identifier(value):
    if value is "":
        return False
    first = value[0]
    if not ('_' == first or first.isalpha()):
        return False
    last = value[1:]
    for i in last:
        if not ('_' == i or i.isalnum()):
            return False
    return True
