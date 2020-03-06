# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 10:54:46 2019

@author: Haiyi
@email: 806935610@qq.com
@wechart: yyy99966
@github: https://github.com/yyy999

"""

import base64
import datetime
import time
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests

import accountConfig
# 此处填写APIKEY

#ACCESS_KEY = "152696e6-10a6dda2-787fcb1a-bewr5drtmh"
#SECRET_KEY = "18f45246-85b7228d-996e0d98-82540"
#ACCESS_KEY = "30abf671-1qdmpe4rty-4bef0805-2360d"
#SECRET_KEY = "02b3ea6d-35ae1e6e-c99c222a-4e29d"


# API 请求地址
MARKET_URL =accountConfig.huobiApi
 # "https://api.huobi.vn"
TRADE_URL =accountConfig.huobiApi
# "https://api.huobi.vn"
#MARKET_URL = "https://api.huobi.pro"
#TRADE_URL = "https://api.huobi.pro"
# 首次运行可通过get_accounts()获取acct_id,然后直接赋值,减少重复获取。
ACCOUNT_ID =  None

#'Timestamp': '2017-06-02T06:13:49'

KEY_INDEX = "USDT_1"  # 默认的key_index
#
#ACCOUNT_INFO = "get_account_info"
#GET_ORDERS = "get_orders"
#ORDER_INFO = "order_info"
#BUY = "buy"
#BUY_MARKET = "buy_market"
#CANCEL_ORDER = "cancel_order"
#NEW_DEAL_ORDERS = "get_new_deal_orders"
#ORDER_ID_BY_TRADE_ID = "get_order_id_by_trade_id"
#SELL = "sell"
#SELL_MARKET = "sell_market"

'''
发送信息到api
'''



def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)
    response = requests.get(url, postdata, headers=headers, timeout=5)
    try:

        if response.status_code == 200:
            return response.json()
        else:
            return
    except BaseException as e:
        print("httpGet failed, detail is:%s,%s" %(response.text,e))
        return


def http_post_request(url, params, add_to_headers=None):
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = json.dumps(params)
    response = requests.post(url, postdata, headers=headers, timeout=5)
    try:

        if response.status_code == 200:
            return response.json()
        else:
            return
    except BaseException as e:
        print("httpPost failed, detail is:%s,%s" %(response.text,e))
        return


def api_key_get(params, request_path):
    method = 'GET'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    ACCESS_KEY = accountConfig.HUOBI.get("USDT_1").get("ACCESS_KEY")
    SECRET_KEY = accountConfig.HUOBI.get("USDT_1").get("SECRET_KEY")
    params.update({'AccessKeyId': ACCESS_KEY,
                   'SignatureMethod': 'HmacSHA256',
                   'SignatureVersion': '2',
                   'Timestamp': timestamp})

    host_url = TRADE_URL
    host_name = urllib.parse.urlparse(host_url).hostname
#    host_name = host_name.lower()
    params['Signature'] = createSign(params, method, host_name, request_path, SECRET_KEY)

    url = host_url + request_path
#    print(url)
    return http_get_request(url, params)


def api_key_post(params, request_path):
    method = 'POST'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    ACCESS_KEY = accountConfig.HUOBI.get("USDT_1").get("ACCESS_KEY")
    SECRET_KEY = accountConfig.HUOBI.get("USDT_1").get("SECRET_KEY")
    params_to_sign = {'AccessKeyId': ACCESS_KEY,
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp}

    host_url = TRADE_URL
    host_name = urllib.parse.urlparse(host_url).hostname
    host_name = host_name.lower()
    params_to_sign['Signature'] = createSign(params_to_sign, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
    return http_post_request(url, params)


def createSign(pParams, method, host_url, request_path, secret_key):
    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urllib.parse.urlencode(sorted_params)
    payload = [method, host_url, request_path, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')

    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature

'''
request
'''


def httpRequest(url, params):
    '''
    postdata = urllib.parse.urlencode(params)
    postdata = postdata.encode('utf-8')
    fp = urllib.request.urlopen(url, postdata, timeout = 5)
    if fp.status != 200:
        return None
    else:
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        return mystr
    '''
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }

    postdata = urllib.parse.urlencode(params)
    # postdata = postdata.encode('utf-8')
    response = requests.post(url, postdata, headers=headers, timeout=5)
    time.sleep(0.2)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("httpPost failed, detail is:%s" % response.text)