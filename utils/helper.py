#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import io
import logging
import math
import sqlite3 as lite
import sys
import time
import traceback
import uuid

import pandas as pd

COIN_TYPE_BTC_CNY = "btc_usdt"
COIN_TYPE_LTC_CNY = "ltc_usdt"
COIN_TYPE_ETH_USDT = "eth_usdt"
COIN_TYPE_EOS_USDT = 'eos_usdt'
COIN_TYPE_LTC_BTC = 'ltc_btc'
COIN_TYPE_ETH_BTC = 'eth_btc'
COIN_TYPE_EOS_ETH = 'eos_eth'

HUOBI_COIN_TYPE_BTC = "btcusdt"
HUOBI_COIN_TYPE_LTC = "ltcusdt"
HUOBI_COIN_TYPE_ETH = "ethusdt"
HUOBI_COIN_TYPE_EOS = "eosusdt"

COIN_TYPE_USDT = "usdt"
COIN_TYPE_USD = "usd"
COIN_TYPE_ETH = "eth"
CONTRACT_TYPE_WEEK = "week"
CONTRACT_TYPE_NEXT_WEEK = "next_week"  # next_week只出现在比特币中
CONTRACT_TYPE_WEEK_AND_NEXT_WEEK = "week_and_next_week"
CONTRACT_TYPE_QUARTER = "quarter"  # 目前不支持
BITVC_MIN_CASH_AMOUNT = 10  # bitvc的最小下单金额
HUOBI_BTC_MIN_ORDER_QTY = 0.001
HUOBI_BTC_MIN_ORDER_CASH = 1.0
HUOBI_LTC_MIN_ORDER_QTY = 0.01
HUOBI_LTC_MIN_ORDER_CASH = 1.0

HUOBI_ETH_MIN_ORDER_QTY = 0.001
HUOBI_ETH_MIN_ORDER_CASH = 1.0
HUOBI_EOS_MIN_ORDER_QTY = 0.01
HUOBI_EOS_MIN_ORDER_CASH = 0.1

BITEX_ETH_MIN_ORDER_QTY = 0.001
BITEX_ETH_MIN_ORDER_CASH = 1.0
OKCOIN_BTC_MIN_ORDER_QTY = 0.001
OKCOIN_LTC_MIN_ORDER_QTY = 0.1
CHBTC_ETH_MIN_ORDER_QTY = 0.001
PRO_ETH_BTC_MIN_ORDER_QTY = 0.00001
PRO_LTC_BTC_MIN_ORDER_QTY = 0.00001
POLO_MIN_ORDER_BTC_AMOUNT = 0.0001
DATA_DEPTH = 150

HUOBI_SPOT_TRANSACTION_FEE = 0.002  # huobi现货手续费
OKCOIN_SPOT_TRANSACTION_FEE = 0.002  # okcoin现货手续费
BITVC_FEE_RATE = 0.0003  # # bitvc开仓手续费比例（请勿随意更改）

# huobi 订单返回信息中，type字段
HUOBI_ORDER_TYPE_BUY_LIMIT = 1
HUOBI_ORDER_TYPE_SELL_LIMIT = 2
HUOBI_ORDER_TYPE_BUY_MARKET = 3
HUOBI_ORDER_TYPE_SELL_MARKET = 4

# (开多: orderType 1 tradeType 1 开空: orderType 1 tradeType 2)
# (平多: orderType 2 tradeType 2 平空: orderType 2 tradeType 1)
CONTRACT_ORDER_TYPE_OPEN = 1
CONTRACT_ORDER_TYPE_CLOSE = 2
CONTRACT_ORDER_TYPE_OPEN_STRING = "open"
CONTRACT_ORDER_TYPE_CLOSE_STRING = "close"
CONTRACT_TRADE_TYPE_BUY = 1
CONTRACT_TRADE_TYPE_SELL = 2

HUOBI = "huobi"
OKCOIN = "okcoin"
BITVC = "bitvc"
BITEX = "bitex"
CHBTC = "chbtc"
POLO = "polo"
PRO = "pro"
HUOBI_MARKET_TYPE = 1
OKCOIN_MARKET_TYPE = 2
BITEX_MARKET_TYPE = 3
CHBTC_MARKET_TYPE = 4
PRO_MARKET_TYPE = 5
POLO_MARKET_TYPE = 6
SPOT_TRADE_TYPE_BUY = "buy"
SPOT_TRADE_TYPE_SELL = "sell"
ORDER_TYPE_LIMIT_ORDER = "limit_order"
ORDER_TYPE_MARKET_ORDER = "market_order"

BITVC_DYNAMIC_RIGHTS = "dynamicRights"
BITVC_STATIC_RIGHTS = "staticRights"

HUOBI_CNY_BTC = "huobi_usdt_btc"
HUOBI_CNY_LTC = "huobi_usdt_ltc"
HUOBI_USD_BTC = "huobi_usd_btc"
HUOBI_CNY_CASH = "huobi_usdt_cash"
HUOBI_USD_CASH = "huobi_usd_cash"

OKCOIN_CNY_BTC = "okcoin_usdt_btc"
OKCOIN_CNY_LTC = "okcoin_usdt_ltc"
OKCOIN_USD_BTC = "okcoin_usd_btc"
OKCOIN_USD_LTC = "okcoin_usd_ltc"
OKCOIN_CNY_CASH = "okcoin_usdt_cash"
OKCOIN_USD_CASH = "okcoin_usd_cash"

BITVC_CNY_BTC = "bitvc_usdt_btc"
BITVC_CNY_LTC = "bitvc_usdt_ltc"
BITVC_USD_BTC = "bitvc_usd_btc"
BITVC_USD_LTC = "bitvc_usd_ltc"
BITVC_CNY_CASH = "bitvc_usdt_cash"
BITVC_USD_CASH = "bitvc_usd_cash"

# bitvc下周合约开始于周四
BITVC_NEXT_WEEK_CONTRACT_START_WEEKDAY = 3
# bitvc下周合约开始于中午12：00
BITVC_NEXT_WEEK_CONTRACT_START_TIME = datetime.time(12, 0)

# bitvc下周合约结束于周五
BITVC_NEXT_WEEK_CONTRACT_END_WEEKDAY = 4
# bitvc下周合约结束于中午12：00
BITVC_NEXT_WEEK_CONTRACT_END_TIME = datetime.time(12, 0)

HUOBI_ORDER_STATUS_INFO = ["unfilled", "partially filled", "fully filled", "cancelled", "abandoned", "abnormal",
                           "partially cancelled", "queuing"]

OKCOIN_ORDER_STATUS_INFO = ["unfilled", "partially filled", "fully filled", "cancelling", "cancelled"]

coinTypeStructure = {
    COIN_TYPE_BTC_CNY: {
        "huobi": {
            "coin_type": HUOBI_COIN_TYPE_BTC,
            "market": COIN_TYPE_USDT,
            "coin_str": HUOBI_CNY_BTC,
            "market_str": HUOBI_CNY_CASH
        },
        "okcoin": {
            "coin_type": COIN_TYPE_BTC_CNY,
            "market": COIN_TYPE_USDT,
            "coin_str": OKCOIN_CNY_BTC,
            "market_str": OKCOIN_CNY_CASH
        },
        "bitvc": {
            "coin_type": HUOBI_COIN_TYPE_BTC,
            "market": COIN_TYPE_USDT,
            "coin_str": BITVC_CNY_BTC,
            "market_str": BITVC_CNY_CASH
        }

    },
    COIN_TYPE_LTC_CNY: {
        "huobi": {
            "coin_type": HUOBI_COIN_TYPE_LTC,
            "market": COIN_TYPE_USDT,
            "coin_str": HUOBI_CNY_LTC,
            "market_str": HUOBI_CNY_CASH
        },
        "okcoin": {
            "coin_type": COIN_TYPE_LTC_CNY,
            "market": COIN_TYPE_USDT,
            "coin_str": OKCOIN_CNY_LTC,
            "market_str": OKCOIN_CNY_CASH
        }
    }
}


# 从huobi style的security拿到okcoin style的security
def getCoinMarketTypeFromSecurity(security):
    if security == "huobi_usdt_btc":
        return COIN_TYPE_BTC_CNY
    elif security == "huobi_usdt_ltc":
        return COIN_TYPE_LTC_CNY
    else:
        raise ValueError("invalid security %s" % security)


# 向下取小数点后decimal_places位精度
def downRound(qty, decimal_places=4):
    r=round(float(qty),decimal_places)
#    a = "%f" % qty
#    b = a.split('.')
#    round_down = '%s.%s' % (b[0], b[1][:decimal_places])
#    return float(round_down)
    return r
# 对币数量进行精度裁剪
def getRoundedQuantity(qty, coin_type):
    if coin_type == COIN_TYPE_BTC_CNY:
        # 按照okcoin的下单规则，比特币都是0.01 btc的整数倍，取下限
        return downRound(qty, decimal_places=2)
    elif coin_type == COIN_TYPE_LTC_CNY:
        # 按照okcoin的下单规则，莱特币都是0.1 ltc的整数倍，取下限
        return downRound(qty, decimal_places=1)
    elif coin_type == COIN_TYPE_ETH_BTC:
        return downRound(qty, decimal_places=4)
    elif coin_type == COIN_TYPE_LTC_BTC:
        return downRound(qty, decimal_places=4)
    else:
        raise ValueError("invalid coin type %s" % coin_type)


# 从对象拿数据
def componentExtract(object, key, default=None):
    if type(object) == dict:
        return object.get(key, default)
    else:
        return getattr(object, key, default)


# 获取uuid
def getUUID():
    return str(uuid.uuid1())


# print traceback to log
def printTracebackToLog(timeLog):
    timeLog(traceback.format_exc())


# 获取当前时间，返回字符串，格式为：'YYYYMMDD_hhmmss'
def current_time_str():
    current_time = datetime.datetime.now()
    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return time_string
# 获取当前时间，返回字符串，格式为：'YYYYMMDD_hhmmss'
def current_date_str():
    current_time = datetime.datetime.now()
    time_string = current_time.strftime("%Y-%m-%d")
    return time_string

# 将时间戳转化为可读时间
def timestamp_to_timestr(timestamp):
    time_struct = time.localtime(timestamp)
    time_string = time.strftime("%Y%m%d_%H%M%S", time_struct)
    return time_string
def time_to_timestr(timestamp):
    time_struct = time.localtime(timestamp/1000)
    time_string = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
    return time_string
def get_today():
    d2=datetime.date.today()
    return d2

def get_start_day(end_day):
#    d2=(end_day)
    d1=end_day-datetime.timedelta(days=1)
    return d1

# 抽象出timelogger
class TimeLogger(object):
    def __init__(self, logFileName):
        self.timeLogger = logging.getLogger('timeLog')
        self.timeLogger.setLevel(logging.DEBUG)
        self.timeLogHandler = logging.FileHandler(logFileName)
        self.timeLogHandler.setLevel(logging.DEBUG)
        self.consoleLogHandler = logging.StreamHandler()
        self.consoleLogHandler.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.timeLogHandler.setFormatter(formatter)
        self.consoleLogHandler.setFormatter(formatter)
        # 给timeLogger添加handler
        self.timeLogger.addHandler(self.timeLogHandler)
        self.timeLogger.addHandler(self.consoleLogHandler)

    def timeLog(self, content, level=logging.INFO):
        if level == logging.DEBUG:
            self.timeLogger.debug(content)
        elif level == logging.INFO:
            self.timeLogger.info(content)
        elif level == logging.WARN:
            self.timeLogger.warn(content)
        elif level == logging.ERROR:
            self.timeLogger.error(content)
        elif level == logging.CRITICAL:
            self.timeLogger.critical(content)
        else:
            raise ValueError("unsupported logging level %d" % level)

# 计算时间差
def diff_times_in_seconds(t1, t2):
    # caveat emptor - assumes t1 & t2 are python times, on the same day and t2 is after t1
    h1, m1, s1 = t1.hour, t1.minute, t1.second
    h2, m2, s2 = t2.hour, t2.minute, t2.second
    t1_secs = s1 + 60 * (m1 + 60*h1)
    t2_secs = s2 + 60 * (m2 + 60*h2)
    return( t2_secs - t1_secs)

# 从数据库中获取调仓信息
def get_trans_record(coinMarketType):
    con = lite.connect('orderBook.db')
    trans_sql = ("select *, datetime(record_time, 'unixepoch', 'localtime') as time_str "
                 "from depth_data_%s order by record_time" % coinMarketType)
    trans_record = pd.read_sql(trans_sql, con, index_col='time_str', parse_dates=['time_str'])
    trans_record.to_csv(
        "data/depth_data/depth_data_%s_%s.csv" % (coinMarketType, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")))
    return trans_record


# 从数据库中获取pos record信息
def get_pos_record():
    con = lite.connect('orderBook.db')
    pos_sql = ("select *, datetime(record_time, 'unixepoch', 'localtime') as time_str "
               "from positionRecord order by record_time")
    pos_record = pd.read_sql(pos_sql, con, index_col='time_str', parse_dates=['time_str'])
    pos_record.to_csv("data/pos_data/pos_data_%s.csv" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")))
    return pos_record


# 查看所给时间是否有bitvc的下周合约
def has_bitvc_next_week_contract(current_datetime):
    """
    测试所给时间是否有bitvc的下周合约
    :param current_datetime: 一个datetime.datetime对象
    :return: 有则返回True， 否则返回False
    """
    current_weekday = current_datetime.weekday()
    current_time = current_datetime.time()
    if BITVC_NEXT_WEEK_CONTRACT_START_WEEKDAY <= current_weekday <= BITVC_NEXT_WEEK_CONTRACT_END_WEEKDAY:
        if current_weekday == BITVC_NEXT_WEEK_CONTRACT_START_WEEKDAY:
            if current_time <= BITVC_NEXT_WEEK_CONTRACT_START_TIME:
                return False
        if current_weekday == BITVC_NEXT_WEEK_CONTRACT_END_WEEKDAY:
            if current_time >= BITVC_NEXT_WEEK_CONTRACT_END_TIME:
                return False
        return True
    return False


# 查看所给时间，是否在本周的某一个时间段内
def in_time_period(current_datetime, start_week_day, end_week_day, start_time, end_time):
    """
    测试所给时间是否在某一个时间段内
    :param current_datetime: 一个datetime.datetime对象
    :return: 有则返回True， 否则返回False
    """
    current_weekday = current_datetime.weekday()
    current_time = current_datetime.time()
    if start_week_day <= current_weekday <= end_week_day:
        if current_weekday == start_week_day:
            if current_time < start_time:
                return False
        if current_weekday == end_week_day:
            if current_time >= end_time:
                return False
        return True
    return False


# 策略进程
def start_strat(strat, exitOnException=False):
    if strat.dailyExitTime is not None:
        # check whether current time is after the dailyExitTime, if yes, exit
        while datetime.datetime.now() <= datetime.datetime.strptime(
                                datetime.date.today().strftime("%Y-%m-%d") + " " + strat.dailyExitTime,
                "%Y-%m-%d %H:%M:%S"):
            try:
                strat.go()
            except Exception:
                printTracebackToLog(strat.timeLog)
                if exitOnException:
                    return
        strat.timeLog("抵达每日终结时间：%s, 现在退出." % strat.dailyExitTime)
    else:
        while True:
            try:
                strat.go()
            except Exception:
                printTracebackToLog(strat.timeLog)
                if exitOnException:
                    return

#search currencent
def find_currency(input_list=[],cur_name="eth"):
#    num_list = [[1,2,3],[4,5,6]]
    if input_list == []:
        num_list = [{'currency': 'mtx', 'type': 'trade', 'balance': '38.987515102698348745'},
                {'currency': 'mtx', 'type': 'frozen', 'balance': '0'},
                {'currency': 'dash', 'type': 'trade', 'balance': '0'},
                {'currency': 'dash', 'type': 'frozen', 'balance': '0'}]
    else:
        num_list = input_list
    cur_list=[]
    for i in num_list:
        if i.get('currency')== cur_name:
            cur_list.append(i)
#            for j in i:
#            if j.get('currency')=='mtx':
#            print('{0}'.format(i.get('balance')))
    return cur_list

'''
本程序入口
'''
if __name__ == "__main__":
#    find_currency()
    end_day=get_today()
    print(end_day)
    d2=end_day-datetime.date(2019,10,1)
    d3=end_day-datetime.timedelta(days=1)
    d4=get_start_day(end_day)
    print(d4)
