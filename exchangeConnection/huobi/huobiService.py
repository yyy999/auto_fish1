#!/usr/bin/env python
# -*- coding: utf-8 -*-

from exchangeConnection.huobi.util import *
from utils.helper import *
from exchangeConnection.huobi.huobiService913 import *

'''
获取账号详情
'''


def getAccountInfo(market, method='get', key_index='USDT_1'):
    urlPath = "/v1/account/accounts"
#
    params = {"method": method}
    params['urlPath'] = urlPath
##    params['url']='/v1/account/accounts'
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
#    res = api_key_get(params,urlPath)
    return res








'''
限价买入
@param symbol
@param price
@param amount
@param tradePassword
@param tradeid
@param method
'''


def buy(symbol, price, amount):
#    params = {"method": method}
#    params['symbol'] = symbol.lower()
#    params['price'] = price
#    params['amount'] = amount
#    extra = {}
#    extra['trade_password'] = tradePassword
#    extra['trade_id'] = tradeid
#    extra['market'] = market
    source="api"
    _type="buy-limit"
    symbol=symbol.lower()
    res = send_order(amount, source, symbol, _type, price)
#    send_order(amount,)
#    send2api(params, extra, key_index=key_index)
    return res #下单号


'''
限价卖出
@param symbol
@param price
@param amount
@param tradePassword
@param tradeid
'''


def sell(symbol, price, amount):

    source="api"
    _type="sell-limit"
    symbol=symbol.lower()
    res = send_order(amount, source, symbol, _type, price)
    return res


'''
市价买
@param symbol
@param amount
@param tradePassword
@param tradeid
'''


def buyMarket(symbol, amount):

    source="api"
    _type="buy-market"
    symbol=symbol.lower()
    price=0
    res = send_order(amount, source, symbol, _type, price)
    return res


'''
市价卖出
@param symbol
@param amount
@param tradePassword
@param tradeid
'''


def sellMarket(symbol, amount):

    source="api"
    _type="sell-market"
    symbol=symbol.lower()
    price=0
    res = send_order(amount, source, symbol, _type, price)
    return res



'''
获取最少订单数量
@param symbol:币种 1 比特币 2 莱特币
火币上比特币交易及莱特币交易都是0.0001的整数倍
比特币最小交易数量：0.001,莱特币最小交易数量：0.01
'''


def getMinimumOrderQty(symbol):
    if symbol == HUOBI_COIN_TYPE_BTC:
        return 0.001
    else:
        return 0.01


'''
获取最少交易金额
火币上比特币交易及莱特币交易金额都是0.01的整数倍
最小交易金额：1
'''


def getMinimumOrderCashAmount():
    return 1


'''
提取BTC/LTC
提币数量 BTC>=0.01 LTC>=0.1
withdraww_fee: 网络转账手续费，支持范围：BTC[0.0001,0.01],LTC目前仅支持0.01。如果不填此参数默认最小值
'''


def withdrawCoin(symbol, amount, address, tradePassword, market, fee,method, key_index='USDT_1'):
    params = {"method": method}
    params["withdraw_amount"] = amount
    params['symbol'] = symbol
    params["withdraw_address"] = address
    extra = {}
    extra['trade_password'] = tradePassword
    extra['market'] = market
    extra["withdraw_fee"] = fee
    res = send2api(params, extra, key_index=key_index)
    return res

# 查询提币执行情况
def withdraw_info(withdraw_id, market, key_index='USDT_1'):
    method = "get_withdraw_coin_result"
    params = {"method": method}
    params["withdraw_coin_id"] = withdraw_id
    extra = {}
    extra['market'] = market
    res = send2api(params, extra, key_index=key_index)
    return res


def get_prices(symbol, frequency, length=300):
    """
    支持1m, 5m, 15m, 30m, 60m, 4h, 1d, 1w, 1M, 1y频率的信息
    返回一个 pandas.DataFrame 对象，结构为
                open    high    low    close    volume
    bar_time

    :param symbol:
    :param frequency:
    :param length:
    :return:
    """
    api_frequency = frequency
    aggregation_level = 1
    if frequency == "4h":
        api_frequency = "60m"
        aggregation_level = 4
    hist = getKLine(symbol, api_frequency, length=length * aggregation_level)
    hist_pd = convert_to_ohlcv_dataframe(hist)
    if frequency == "4h":
        hist_pd = aggregation(hist_pd)
    return hist_pd


# 聚合
def aggregation(df):
    ohlc = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'}
    new_pd = df.resample('240min', closed='left', label='left').apply(ohlc).ffill()
    return new_pd


def convert_to_ohlcv_dataframe(data_array):
    date_format = "%Y%m%d%H%M%S000"
    df = pd.DataFrame(data_array, columns=['bar_time', 'open', 'high', 'low', 'close', 'volume'], )
    df.index = pd.to_datetime(df.bar_time, format=date_format, utc=True)
    del df['bar_time']
    return df






# 获取最新的买卖盘数据
def get_orderbook(base_currency, market):
    if market == COIN_TYPE_USDT:
        url = TRADE_URL+"/staticmarket/detail_" & base_currency &"_json.js"
        raise ValueError("invalid market %s" % market)
    return httpRequest(url, {})

# 获取最近60笔市场成交信息
def get_latest_trades(symbol, market="usdt"):
    orderbook = get_orderbook(symbol, market)
    trades_data = orderbook["trades"]
    trades_df = pd.DataFrame(trades_data)
    trades_df = trades_df.set_index("time")
    trades_df.sort_index(inplace=True)
    return trades_df

