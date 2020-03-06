#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 21:57:24 2019
@author: Haiyi
@email: 806935610@qq.com
@wechart: yyy99966
@github: https://github.com/yyy999

"""
from  exchangeConnection.huobi.util import *
import exchangeConnection.huobi.huobiService
import exchangeConnection.huobi.huobiService913
import utils.helper as uh
import time

# 包装一个不同市场的统一接口 方便同一调用
class Market:
    def __init__(self, market_name="huobi"):
        self.market_name = market_name

    def market_detail(self, base_cur,quotes_cur=''):
        """
        获取市场盘口信息
        :param base_cur:
        :param quote_cur:
        :return:
        """
        symbol=base_cur+quotes_cur
#        print(symbol)
        if self.market_name == "huobi":
            return exchangeConnection.huobi.huobiService913.get_depth(symbol,"step0").get("tick")
        else:
            return None
# =============================================================================
# get accounts
# =============================================================================
    def get_accountInfo(self, market_name="huobi"):
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            bitex_acc = exchangeConnection.huobi.huobiService913.get_accounts()
#            print(bitex_acc)
            if bitex_acc['status']=='ok':
                acc_id=bitex_acc.get("data")[0].get("id")
                return acc_id
            else:
                return -1
        else:
            return None
# =============================================================================
#
# =============================================================================
    def account_available(self, cur_name, cur_market_name=None):
        """
        获取某个currency的可用量
        :param cur_name:
        :param cur_market_name:
        :return:
        """
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            bitex_acc = exchangeConnection.huobi.huobiService913.get_balance()
#            print(bitex_acc)
            now_list=uh.find_currency(bitex_acc.get("data").get("list"),cur_name)
            return uh.downRound(float(now_list[0].get("balance")),8) #取可交易的余额
        else:
            return None
# =============================================================================
#
# =============================================================================
    def account_frozen(self, cur_name, cur_market_name=None):
        """
        获取某个currency的可用量
        :param cur_name:
        :param cur_market_name:
        :return:
        """
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            bitex_acc = exchangeConnection.huobi.huobiService913.get_balance()
#            print(bitex_acc)
            now_list=uh.find_currency(bitex_acc.get("data").get("list"),cur_name)
            return uh.downRound(float(now_list[1].get("balance")),8) #取冻结的余额
        else:
            return None
# =============================================================================
#   get lastest market close
# =============================================================================
    def get_market_close(self, base_cur, quotes_cur=""):
        """
        获取市场盘口信息
        :param base_cur:
        :param quote_cur:
        :return:
        """
        symbol=base_cur+quotes_cur
        #        print(symbol)
        if self.market_name == "huobi":
            result=exchangeConnection.huobi.huobiService913.get_trade(symbol)#.get("data")[0]['price']
#            print(result)
            if result.get("status") == "ok":
#               lastorder = result.get('data')[0].get('price')
               lastorder = result['tick']['data'][0]['price']
               return lastorder
            else:
               return 0
        else:
            return 0
    def buy(self, cur_market_name, price, amount):
        '''
        buy-limit
        '''
        # print("buy", cur_market_name, price, amount)
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            return exchangeConnection.huobi.huobiService.buy(cur_market_name, price, amount)
        else:
            return None

    def sell(self, cur_market_name, price, amount):
        #sell-limit
        # print("sell", cur_market_name, price, amount)
        if self.market_name == "huobi":
            return exchangeConnection.huobi.huobiService.sell(cur_market_name, price, amount)

        else:
            return None

    def buy_market(self, cur_market_name, amount):
        """
        市价买
        :param cur_market_name: 货币对的名称
        :param amount: 买的总价
        :return:
        """
        # print("buy_market:", cur_market_name, amount)
        if self.market_name == "huobi":
            return exchangeConnection.huobi.huobiService.buyMarket(cur_market_name, amount)
        else:
            return None

    def sell_market(self, cur_market_name, amount):
        """
        市价卖
        :param cur_market_name: 货币对的名称
        :param amount: 卖的数量
        :return:
        """
        # print("sell_market:", cur_market_name, amount)
        if self.market_name == "huobi":
            return exchangeConnection.huobi.huobiService.SellMarket(cur_market_name, amount)
        else:
            return None
# =============================================================================
#       get orderlist
# =============================================================================
    def get_last_order_price(self,symbol):
            #print(orders_list('eoseth','filled'))
        if self.market_name == "huobi":
            n=0
            d2=uh.get_today()
            d1=uh.get_start_day(d2)
            while(n<5):
                n=n+1
#                d1_str=time.strftime("%Y-%m-%d", d1)
#                d2_str=time.strftime("%Y-%m-%d", d2)
#                result=exchangeConnection.huobi.huobiService913.orders_list(symbol,states,None,d1,d2)
                result=exchangeConnection.huobi.huobiService913.orders_matchresults(symbol,None,d1,d2)

#                print(result)
                if result.get("status") == "ok" :
                    if result.get('data')!=[]:
        #               lastorder = result.get('data')[0].get('price')
                       lastorder = result['data'][0]['price']
                       amount = result['data'][0]['filled-amount']
                       _type = result['data'][0]['type']
                       return lastorder,amount,_type
                    else:
                        print(d1)
                        d2=uh.get_start_day(d1)
                        d1=uh.get_start_day(d2)
                else:
                   return -1,0,0
            else:
                return -1,0,0
        else:
            return 0,0,0
# =============================================================================
#         get order history
# =============================================================================
    def get_orders_history(self):
        if self.market_name == "huobi":
#            n=0
#            d2=uh.get_today()
#            d1=uh.get_start_day(d2)
#            while(n<30):
#                n=n+1
#                d1_str=time.strftime("%Y-%m-%d", d1)
#                d2_str=time.strftime("%Y-%m-%d", d2)
#            result=exchangeConnection.huobi.huobiService913.orders_list(symbol,states,None,d1,d2)
            result=exchangeConnection.huobi.huobiService913.orders_history()

#            print(result)
            if result.get("status") == "ok" :
                if result.get('data')!=[]:
#                    order_list=['']*10
    #               lastorder = result.get('data')[0].get('price')
                    cols_list=['']*11
                    cols_list[0]=result['data'][0]['id']
                    cols_list[1]=uh.time_to_timestr(result['data'][0]['finished-at'])
                    cols_list[2]=result['data'][0]['symbol']
                    cols_list[3]=result['data'][0]['type']
                    cols_list[4]=result['data'][0]['price']
                    cols_list[5]=result['data'][0]['field-amount']
                    cols_list[6]=result['data'][0]['field-cash-amount']
                    cols_list[7]=result['data'][0]['field-fees']
                    cols_list[8]=result['data'][0]['source']
                    cols_list[9]= result['data'][0]['state']
                    cols_list[10]=result['data'][0]['account-id']
                    return cols_list
                else:
#                    print(d1)
#                    d2=uh.get_start_day(d1)
#                    d1=uh.get_start_day(d2)
#                        continue
                    return 0,0,0
            else:
               return -1,0,0
        else:
            return -2,0,0
# =============================================================================
#
# =============================================================================
    def get_orderid(self,clienorderid):
        if self.market_name == "huobi":
            result=exchangeConnection.huobi.huobiService913.get_orderid(clienorderid)
#            print(result)
            return result
# =============================================================================
#
# =============================================================================
    def order_normal(self, order_result, cur_market_name):
        """
        是否成功下单
        :param order_result: 下单返回结果
        :param cur_market_name: 货币对名称
        :return:
        """
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            if order_result.get("status") == "ok":
                return True
            else:
                return False



    def get_order_processed_amount(self, order_result, cur_market_name=None):
        # print("get_order_processed_amount:", order_result, cur_market_name)
        if self.market_name == "huobi":
            result = exchangeConnection.huobi.huobiService913.order_info(order_result.get("data"))
#            print(result)
            return result.get('data').get("field-amount")
        else:
            return None

    def cancel_order(self, order_result, cur_market_name=None):
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
#            if quote_cur == "usdt":
#                if base_cur == "eth":
#                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="USDT_1")\
#                        .cancel_order(str(order_result.get("data")))  # {'status': 'ok', 'data': '2705970'}
#                elif base_cur == "etc":
#                    return exchangeConnection.bitex.bitexService.BitexServiceAPIKey(key_index="USDT_1")\
#                        .cancel_order(str(order_result.get("data")))  # {'status': 'ok', 'data': '2705970'}
#                elif base_cur == "btc":
            return exchangeConnection.huobi.huobiService913.cancel_order(order_result.get("data"))# {'status': 'ok', 'data': '2705970'}
#                elif base_cur == "ltc":
#                    return exchangeConnection.huobi.huobiService.cancelOrder(
#                        2, order_result.get("id"), "usdt", "cancel_order")
#            elif quote_cur == "btc":
#                if base_cur == "ltc" or base_cur == "eth" or base_cur =="etc":
#                    return exchangeConnection.pro.proService.ProServiceAPIKey(key_index="USDT_1").cancel_order(
#                           order_result.get("data"))
        else:
            return None

    def get_order_status(self, order_result, cur_market_name):
        # print("get_order_status:", order_result, cur_market_name)
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            result = exchangeConnection.huobi.huobiService913.order_info(order_result.get("data"))
            return result.get('data').get("state")
        else:
            return None
    def get_symbols(self,symbol=''):
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            result = exchangeConnection.huobi.huobiService913.get_symbols()
            if symbol=='':
#                print( result['data'])
                return result.get('data')
            else:
                for sym in result['data']:
                    if sym.get('symbol')==symbol:
                        list_sym=(sym.get('min-order-amt'),sym.get('amount-precision'),sym.get('price-precision'))
                        list1=sym
                        break

                digits=list1.get('amount-precision')
#                print(digits)
                return list1
        else:
            return None
    def get_assets(self,acc_id):
        if self.market_name == "huobi":
#            base_cur, quote_cur = cur_market_name.split("_")
            bitex_acc = exchangeConnection.huobi.huobiService913.get_balance()
            a=['usdt','btc','eth','eos']
            a_balanc=[0]*9
            a_balanc[0]=acc_id # self.get_accountInfo()
            a_balanc[1]=uh.current_date_str()

            for i in range(len(a)):
                now_list=uh.find_currency(bitex_acc.get("data").get("list"),a[i])
                a_balanc[i+2]=uh.downRound(float(now_list[0].get("balance"))+float(now_list[1].get("balance")),8)
#                a_balanc[i+2]=float(now_list[0].get("balance"))+float(now_list[1].get("balance"))
                print(a_balanc[i+2])
#                time.sleep(2)
            return(a_balanc)


#            print(bitex_acc)

#            return uh.downRound(float(now_list[0].get("balance")+now_list[1].get("balance")),8) #取可交易的余额
        else:
            return None



# test
if __name__ == "__main__":
    huobi = Market()
    a=huobi.get_accountInfo()
    print(a)
#    b=huobi.account_available('eth')
#    print(b)
#    print(huobi.get_symbols('eoseth'))
##        print huobi.(get_symbols())
##    print(huobi.get_accounts())
#    print(huobi.get_assets(a))
    print(huobi.get_orders_history())
    print(huobi.get_orderid(62657991295))
#     print(huobi.market_detail("eth","btc"))
#    print(huobi.market_detail("eosusdt"))
#     print(huobi.market_detail("ltc", "usdt"))
#     print(huobi.market_detail("eth", "usdt"))
##     print(huobi.market_detail("eos", "eth"))
