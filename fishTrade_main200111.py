# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 20:13:32 2019

@author: Haiyi
@email: 806935610@qq.com
@wechart: yyy99966
@github: https://github.com/yyy999

"""
'''
20191010
1.修复了网格未设置问题
2.统一了日志文件与与屏幕的同时输出问题
2019.10.12
v2.0
1.增加了货币对回应信息输出功能
2.实现了价格和交易量精度自动获得功能
3.增加多货币对交易功能
2019.10.18
1.修复下单后不能正常返回问题
2019.11.16
1.调整开仓策略为金字塔式开仓
2019.11.21
1.加入域名配置
2019.12.06
1.增加授权码验证功能
2.开仓定量
2019.12.22
1.增加了数据库支持功能
2.优化了读取API账户的算法,防止了交易所的限频超时断开连接错误
2019.12.25
1.0修改了首次插入sql时初始资金和时间问题
2.去除了sql_calss.py中mh库,通过参数把对象传入
3.消除近日无交易不下单问题
2019.12.29
1.0改为单独交易版,将sql功能剥离,另外做一个插件独立使用
2020.1.11
1.开仓网格修改为自动高低点设置
'''
#import ma_ind as maInd
import sys
import marketHelper1005 as marketHelper
import accountConfig as accCfg
#import sql_class1225 as sql
import traceback
import time
import logging
#import multiprocessing
import math
from utils.helper import *
import datetime
import ma_ind as maInd
# 设置logging


# =============================================================================
#  log date  shift
# =============================================================================

logger = logging.getLogger()
logger.setLevel(logging.INFO)
#now_dir = os.getcwd()
main_log_handler = logging.FileHandler("log/fishTrade_main_{0}.log".format(int(time.time())), mode="w", encoding="utf-8")
main_log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
main_log_handler.setFormatter(formatter)
logger.addHandler(main_log_handler)
account_id=0
write_flag=0
class ClassET:
    """
        交易对：用一种资产（quote currency）去定价另一种资产（base currency）,比如用比特币（BTC）去定价莱特币（LTC），
        就形成了一个LTC/BTC的交易对，
        交易对的价格代表的是买入1单位的base currency（比如LTC）
        需要支付多少单位的quote currency（比如BTC），
        或者卖出一个单位的base currency（比如LTC）
        可以获得多少单位的quote currency（比如BTC）。
        当LTC对BTC的价格上涨时，同等单位的LTC能够兑换的BTC是增加的，而同等单位的BTC能够兑换的LTC是减少的。
    """

    def __init__(self, base_cur="eos", quote_cur="eth",  highPrice=0, lowPrice=0,step_num=10,first_lots=1):
        """
        初始化
        :param base_cur:  基准资产
        :param quote_cur:  定价资产
        :param highPrice:  高点价格
        :param lowPrice:  低点价格
        网格数量
        第一单手数
        """

        # 设定EA监控交易对
        self.base_cur = base_cur
        self.quote_cur = quote_cur
#        self.mid_cur = mid_cur   # 中间货币，usdt或者btc
#
#        self.base_quote_slippage = 0.002  # 设定市场价滑点百分比
##        self.base_mid_slippage = 0.002
##        self.quote_mid_slippage = 0.002
#
#        self.base_quote_fee = 0.002  # 设定手续费比例
##        self.base_mid_fee = 0.002
##        self.quote_mid_fee = 0.002
#
#        self.order_ratio_base_quote = 0.5  # 设定吃单比例
##        self.order_ratio_base_mid = 0.5

        # 设定监控时间
        self.interval = 2
        self.highPrice = highPrice
        self.lowPrice = lowPrice
#        self.startPrice = startPrice
        self.step_num = step_num
        self.medialPrice = (highPrice+lowPrice)/2
        self.stepGrid = (highPrice-lowPrice)/step_num
        #XXX
        # 最小的交易单位设定
        self.min_trade_unit = 0.002   # LTC/BTC交易对，设置为0.2, ETH/BTC交易对，设置为0.02
        self.pos_rate = {'0.10':0.1 ,'0.25':0.25,'0.38':0.38,'0.50':0.5,'0.62':0.62,'0.75':0.75,'1.00':1}
        self.pos_rate_list = [0.1,0.25,0.38,0.5,0.62,0.75,1.0]
        self.pos_first_lots = first_lots
        self.pos_count_max = 7
        self.pos_count_buy = 0
        self.pos_count_sell = 0
        self.market_price_tick = dict()  # 记录触发套利的条件时的当前行情
        self.pos = False
        self.buyCmd = False
        self.sellCmd = False
        self.openBuy = 0
        self.openSell =0
        self.closeBuy=0
        self.closeSell=0
        self.doAction=0 #1:openBuy,2:openSell,3:closeBuy,4:closeSell
        self.logstr1="str1"
        self.logstr2="str2"
        strPara ="初始参数设置:symbol={0}_{1} highPrice={2} lowPrice={3}  step_num={4}".format(\
                                        self.base_cur, self.quote_cur, self.highPrice, self.lowPrice,  self.step_num)
        logger.info(strPara)
        print(strPara)
# =============================================================================
#
# =============================================================================
    def strategy(self):   # 主策略
        # 检查是否有开仓条件
        try:
            if self.highPrice<=0 or self.lowPrice<=0  or self.step_num<=1:
                strPara ="初始参数设置错误:symbol={0}_{1} highPrice={2} lowPrice={3}  step_num={4}".format(\
                                        self.base_cur, self.quote_cur, self.highPrice, self.lowPrice,  self.step_num)
                logger.error(strPara)
                print(strPara)
                return -1
            # 初始化为火币市场
            huobi_market = marketHelper.Market()
            if account_id==-1:
                print('API账户连接失败，请确认配置API访问键值对正确？')
                return -1
            self.market_price_tick = dict()
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)] = \
                huobi_market.market_detail(self.base_cur, self.quote_cur)
#            print(self.market_price_tick)
#            print(huobi_market.market_detail(self.base_cur, self.quote_cur))
            market_price_sell_1 = \
                self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][0]
            market_price_buy_1 = \
                self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("bids")[0][0]
#            self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)] = \
#                huobi_market.market_detail(self.base_cur, self.mid_cur)
            print('ask1=',market_price_sell_1)
            print('bid1=',market_price_buy_1)
#            print(self.market_price_tick)
#            print(huobi_market.market_detail(self.base_cur, self.quote_cur))
            symbol = self.get_market_name(self.base_cur,self.quote_cur)
            closePrice=float(huobi_market.get_market_close(symbol))
            print('closePrice=',closePrice)
            if(closePrice==0):
                return -1
            sym_info=huobi_market.get_symbols(symbol)
#            self.print_log('sym_info'+str(sym_info))
            digits=sym_info.get('amount-precision')
            self.min_trade_unit=sym_info.get('min-order-amt')
            print('digits=',digits)
            buylots_avl=self.get_currency_available(huobi_market,self.quote_cur)/closePrice
            buylots_avl=downRound(buylots_avl,digits)
#            matradesys.buy_enter(huobi_market,buylots)
            selllots_avl=self.get_currency_available(huobi_market,self.base_cur)
            selllots_avl = downRound(selllots_avl, digits)
#            return


            n=(closePrice-self.medialPrice)/self.stepGrid
            lastOrderPrice,amount,_type=huobi_market.get_last_order_price(symbol)
            lastOrderPrice=float(lastOrderPrice)
            amount=float(amount)
            if lastOrderPrice>0:
            #cmd价差大于网格时允许交易
                cmd=abs(closePrice-lastOrderPrice)-self.stepGrid
            #判断交易方向
                diretion=closePrice-lastOrderPrice
#                selllots=amount
#                buylots=amount
            else:
                print('近两日无交易')
                diretion=closePrice-self.medialPrice
                r=math.modf(n)
                cmd=1
#                if math.fabs(r[0])>0.75 or math.fabs(r[0])<0.25:
#                    cmd=1
#                else:
#                    cmd=0
            print('n=',n)
            print('lastOrderPrice=',lastOrderPrice)
            print(closePrice)
            print(cmd)
            print(self.stepGrid)
#            '''buy check
            logStr_err="小于最小交易单位:"+symbol+' '+str(self.min_trade_unit)

            if self.sellCmd==False or self.buyCmd==False:
                if n<0:
                    self.buyCmd=True
                    self.sellCmd==False
                elif n>0:
                    self.sellCmd=True
                    self.buyCmd==False

                if cmd>0 and diretion<0:#open buy
                    self.doAction=1

                    buylots=self.pos_first_lots*self.pos_rate_list[0]
                    buylots=downRound(buylots,digits)
                    market_buy_size =buylots         # self.get_market_buy_size(huobi_market)
                    market_buy_size = downRound(market_buy_size, 6)
                    if market_buy_size >= self.min_trade_unit:
                        if market_buy_size<buylots_avl:
                            res=self.buy_enter(huobi_market, market_buy_size)
                        else:#改变方向补仓
                            market_sell_size=downRound(0.5*selllots_avl,digits)
                            res=self.sell_enter(huobi_market, market_sell_size)
                    else:
                        self.print_log(logStr_err)
#                    print('buylots=',buylots)
                    self.logstr1='buylots='+str(buylots)
#                    logger.info(outStr)


                    if self.pos_count_buy>=self.pos_count_max:self.pos_count_buy=0
                elif cmd>0 and diretion>0:#close buy
                    self.doAction=2

#                    if self.pos_count_buy<0:self.pos_count_buy=0
                    selllots=self.pos_first_lots*self.pos_rate_list[0]
                    selllots = downRound(selllots, digits)
                    market_sell_size =selllots          # self.get_market_sell_size(huobi_market)
                    market_sell_size = downRound(market_sell_size, 6)

                    if market_sell_size >= self.min_trade_unit:
                        if market_sell_size<selllots_avl:
                            res=self.sell_enter(huobi_market, market_sell_size)
                        else:
                            market_buy_size=downRound(0.5*buylots_avl,digits)
                            res=self.buy_enter(huobi_market, market_buy_size)
                    else:
                        self.print_log(logStr_err)
                    self.logstr2='selllots='+str(selllots)
#                    logger.info(outStr)

#                    self.pos_count_sell+=1
                else:
                    self.doAction=0

                outStr="买入区：{0},卖出区:{1}, 动作:{2}, 方向:{3}\nlastOrderPrice={4},closePrice={5},stepGrid={6},priceDeff={7}"\
                        .format(self.buyCmd,self.sellCmd,self.doAction,diretion,lastOrderPrice,closePrice,self.stepGrid,cmd)
                logger.info(outStr)
                print(outStr)
                self.print_log(self.logstr1)
                self.print_log(self.logstr2)
                self.sellCmd=False
                self.buyCmd==False
                if self.doAction==0:
                    logger.info('无操作')
#                    return 0
            return 1
        except:
            logger.error(traceback.format_exc())
            print(traceback.format_exc())
            return -99
#    def sum_slippage_fee(self):
#        return self.base_quote_slippage + self.base_mid_slippage + self.quote_mid_slippage + \
#               self.base_quote_fee + self.base_mid_fee + self.quote_mid_fee

#    @staticmethod
    def get_market_name(self,base, quote):
            return "{0}{1}".format(base, quote)

    # 计算最保险的下单数量
    '''

    '''
    def get_market_buy_size(self, huobi_market):
        market_buy_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][1] \
                          * self.order_ratio_base_quote
        base_mid_sell_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("bids")[0][1] \
                             * self.order_ratio_base_mid
        base_quote_off_reserve_buy_size = \
            (huobi_market.account_available(self.quote_cur, self.get_market_name(self.base_cur, self.quote_cur))
             - self.base_quote_quote_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][0]
        quote_mid_off_reserve_buy_size = \
            (huobi_market.account_available(self.mid_cur, self.get_market_name(self.quote_cur, self.mid_cur)) -
             self.quote_mid_mid_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.quote_cur, self.mid_cur)].get("asks")[0][0] / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][0]
        base_mid_off_reserve_sell_size = \
            huobi_market.account_available(self.base_cur, self.get_market_name(self.base_cur, self.mid_cur)) - \
            self.base_mid_base_reserve
        logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(market_buy_size, base_mid_sell_size,
                                                      base_quote_off_reserve_buy_size, quote_mid_off_reserve_buy_size,
                                                      base_mid_off_reserve_sell_size))
        return math.floor(min(market_buy_size, base_mid_sell_size, base_quote_off_reserve_buy_size,
                              quote_mid_off_reserve_buy_size, base_mid_off_reserve_sell_size)*10000)/10000

    '''

    '''
    def get_market_sell_size(self, huobi_market):
        market_sell_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("bids")[0][1] \
                           * self.order_ratio_base_quote
        base_mid_buy_size = self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("asks")[0][1] \
                            * self.order_ratio_base_mid
        base_quote_off_reserve_sell_size = \
            huobi_market.account_available(self.base_cur, self.get_market_name(self.base_cur, self.quote_cur)) \
            - self.base_quote_base_reserve
        quote_mid_off_reserve_sell_size = \
            (huobi_market.account_available(self.quote_cur, self.get_market_name(self.quote_cur, self.mid_cur)) -
             self.quote_mid_quote_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("bids")[0][0]
        base_mid_off_reserve_buy_size = \
            (huobi_market.account_available(self.mid_cur, self.get_market_name(self.base_cur, self.mid_cur)) -
             self.base_mid_mid_reserve) / \
            self.market_price_tick["{0}_{1}".format(self.base_cur, self.mid_cur)].get("asks")[0][0]
        logger.info("计算数量：{0}，{1}，{2}，{3}，{4}".format(market_sell_size, base_mid_buy_size,
                    base_quote_off_reserve_sell_size, quote_mid_off_reserve_sell_size, base_mid_off_reserve_buy_size))
        return math.floor(min(market_sell_size, base_mid_buy_size, base_quote_off_reserve_sell_size,
                          quote_mid_off_reserve_sell_size, base_mid_off_reserve_buy_size) * 10000) / 10000

    '''

    '''
    def buy_enter(self, huobi_market, market_buy_size):
        logger.info("多单开仓 size:{0}".format(market_buy_size))
        # return
        order_result = huobi_market.buy(cur_market_name=self.get_market_name(self.base_cur, self.quote_cur),price=self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].get("asks")[0][0], amount=market_buy_size)
        logger.info("买入结果：{0}".format(order_result))
        time.sleep(2)
        if not huobi_market.order_normal(order_result,cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)):
            # 交易失败
            logger.info("buy交易失败，退出 {0}".format(order_result))
            return 0
        # 获取真正成交量
        retry, already_close_amount = 0, 0.0
        while retry < 3:   # 循环3次检查是否交易成功
            if retry == 2:
                # 取消剩余未成交的
#                self.pos_count_buy-=1
                huobi_market.cancel_order(order_result, self.get_market_name(self.base_cur, self.quote_cur))
                self.wait_for_cancel(huobi_market, order_result, self.get_market_name(self.base_cur, self.quote_cur))
            field_amount = float(huobi_market.get_order_processed_amount(
                order_result, cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)))
            logger.info("field_amount:{0}_{1}".format(field_amount,already_close_amount))
            retry += 1
            time.sleep(2)
            if field_amount-already_close_amount < self.min_trade_unit:
                logger.info("没有新的成功交易或者新成交数量太少")
                continue

            already_close_amount = field_amount
            if field_amount >= market_buy_size:  # 已经完成指定目标数量的套利
                logger.info("完成多单开仓")
#                huobi_market.get_orders_history()
                return 1
        return 0
    '''

    '''
    def sell_enter(self, huobi_market, market_sell_size):
        logger.info("空单开仓")
        # return
        order_result = huobi_market.sell(cur_market_name=self.get_market_name(self.base_cur, self.quote_cur),
                                         price=self.market_price_tick["{0}_{1}".format(self.base_cur, self.quote_cur)].
                                         get("bids")[0][0], amount=market_sell_size)
        if not huobi_market.order_normal(order_result,
                                         cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)):
            # 交易失败
            logger.info("sell交易失败，退出 {0}".format(order_result))
            return 0
        time.sleep(2)
        # 获取真正成交量
        retry, already_close_amount = 0, 0.0
        while retry < 3:  # 循环3次检查是否交易成功
            if retry == 2:
                # 取消剩余未成交的
#                self.pos_count_buy+=1
                huobi_market.cancel_order(order_result, self.get_market_name(self.base_cur, self.quote_cur))

                self.wait_for_cancel(huobi_market, order_result, self.get_market_name(self.base_cur, self.quote_cur))

            field_amount = float(huobi_market.get_order_processed_amount(
                    order_result, cur_market_name=self.get_market_name(self.base_cur, self.quote_cur)))
            logger.info("field_amount:{0}_{1}".format(field_amount, already_close_amount))
            retry += 1
            time.sleep(2)
            if field_amount - already_close_amount < self.min_trade_unit:
                logger.info("没有新的成功交易或者新成交数量太少")
                continue
            already_close_amount = field_amount
            if field_amount >= market_sell_size:  # 已经完成指定目标数量的套利
                logger.info("完成空单开仓")
#                huobi_market.get_orders_history()
                return 1
        return 0
#


    def close_buy_cur_pair(self, buy_size, huobi_market, cur_pair):
        """
        对冲买入货币对
        :param buy_size: 买入数量
        :param huobi_market: 火币市场实例
        :param cur_pair: 货币对名称
        :return:
        """
        logger.info("开始买入{0}".format(cur_pair))
        try:
            order_result = huobi_market.buy(cur_market_name=cur_pair,
                                            price=self.market_price_tick["{0}".format(cur_pair)].
                                            get("asks")[0][0], amount=downRound(buy_size, 2))
            close_amount = 0.0
            time.sleep(0.2)
            logger.info("买入结果：{0}".format(order_result))
            if huobi_market.order_normal(order_result,
                                         cur_market_name=cur_pair):
                huobi_market.cancel_order(order_result, cur_pair)  # 取消未成交的order

                self.wait_for_cancel(huobi_market, order_result, cur_pair)
                close_amount = float(huobi_market.get_order_processed_amount(
                    order_result, cur_market_name=cur_pair))
            else:
                # 交易失败
                logger.info("买入{0} 交易失败 {1}".format(cur_pair, order_result))
            if buy_size > close_amount:
                # 对未成交的进行市价交易
                buy_amount = self.market_price_tick["{0}".format(cur_pair)].get("asks")[4][0] \
                             * (buy_size - close_amount)  # 市价的amount按5档最差情况预估
                buy_amount = max(HUOBI_BTC_MIN_ORDER_CASH, buy_amount)
                market_order_result = huobi_market.buy_market(cur_market_name=cur_pair, amount=downRound(buy_amount, 2))
                logger.info(market_order_result)
        except:
            logger.error(traceback.format_exc())
        logger.info("结束买入{0}".format(cur_pair))

    def close_sell_cur_pair(self, sell_size, huobi_market, cur_pair):
        """
        对冲卖出货币对
        :param sell_size: 卖出头寸
        :param huobi_market: 火币市场实例
        :param cur_pair: 货币对名称
        :return:
        """
        logger.info("开始卖出{0}".format(cur_pair))
        try:
            order_result = huobi_market.sell(cur_market_name=cur_pair,
                                             price=self.market_price_tick["{0}".format(cur_pair)].get("bids")[0][0],
                                             amount=sell_size)
            close_amount = 0.0
            time.sleep(0.2)
            logger.info("卖出结果：{0}".format(order_result))
            if huobi_market.order_normal(order_result,
                                         cur_market_name=cur_pair):
                huobi_market.cancel_order(order_result, cur_pair)
                self.wait_for_cancel(huobi_market, order_result, cur_pair)

                close_amount = float(huobi_market.get_order_processed_amount(order_result, cur_market_name=cur_pair))
            else:
                # 交易失败
                logger.info("卖出{0} 交易失败  {1}".format(cur_pair, order_result))

            if sell_size > close_amount:
                # 对未成交的进行市价交易
                sell_qty = sell_size - close_amount
                ccy_to_sell = cur_pair.split("_")[0]
                if ccy_to_sell == "btc":
                    sell_qty = max(HUOBI_BTC_MIN_ORDER_QTY, sell_qty)
                elif ccy_to_sell == "ltc":
                    sell_qty = max(HUOBI_LTC_MIN_ORDER_QTY, sell_qty)
                elif ccy_to_sell == "eth":
                    sell_qty = max(BITEX_ETH_MIN_ORDER_QTY, sell_qty)
                else:
                    sell_qty = max(BITEX_ETH_MIN_ORDER_QTY, sell_qty)

                market_order_result = huobi_market.sell_market(
                    cur_market_name=cur_pair,
                    amount=downRound(sell_qty, 3))
                logger.info(market_order_result)
        except:
            logger.error(traceback.format_exc())
        logger.info("结束卖出{0}".format(cur_pair))
# =============================================================================
# get mediaPrice
# =============================================================================
    def calcMedialPrice(highPrice,lowPrice):
        return (highPrice+lowPrice)/2
    @staticmethod
    def wait_for_cancel(huobi_market, order_result, market_name):
        """
        等待order  cancel完成
        :param huobi_market: 火币市场实例
        :param order_result: 订单号
        :param market_name: 货币对市场名称
        :return:
        """
        while huobi_market.get_order_status(order_result, market_name) \
                not in [2, 3, 6, "partial-canceled", "filled", "canceled"]:    # 订单完成或者取消或者部分取消
            time.sleep(0.1)
# =============================================================================
#   getLots
# =============================================================================
    def get_currency_available(self,market,curPara):
        cur_lots=market.account_available(curPara)
        return cur_lots
# =============================================================================
# outPut Log
# =============================================================================
    def print_log(self,strLog):
        print(strLog)
        logger.info(strLog)
        return 0
# =============================================================================
#
# =============================================================================
if __name__ == "__main__":

    huobi_market = marketHelper.Market()

    strout=\
            '\n                  ET网格智能交易系统3.0\
             \n*************************版权声明***************************\
             \n********************All Rights Reserved*********************\
             \n软件开发：海易，需求订制联系微信：yyy99966\
             \n优惠版：有效期30天，每分享一个好友，延长30天，10个延长一年\n'
    logger.info(strout)
    print(strout)
    if accCfg.check_authCode==False:
        print('本账户软件使用未授权或者授权码不正确,请联系你的服务商')

    else:
        r=huobi_market.get_accountInfo()
        print(str(r))
        account_id=r

        if r==-1:
    #        print(r)
            print('API账户连接失败，请确认配置API访问键值对正确？')
        else:
#            r=huobi_market.get_orders_history()
#            print(str(r))
#            sql.ins_order(r)
            list_value=accCfg.sym_list_value[1]
    #        print(list_value)
    #    gridtradesys = ClassET('eos','eth',0.021877,0.015780,0.10)
            gridtradesys = ClassET(list_value[0],list_value[1],float(list_value[2]),float(list_value[3]),float(list_value[4]),float(list_value[5]))
            if len(accCfg.sym_list_value)>2:
                list_value=accCfg.sym_list_value[2]
        #        print(list_value)
                gridtradesys1 = ClassET(list_value[0],list_value[1],float(list_value[2]),float(list_value[3]),float(list_value[4]),float(list_value[5]))

            while True:

                print(strout)
    #            logging.info(strout)
                timeLenth=accCfg.use_right

                if timeLenth<=0:
                    print("软件使用已到期，感谢您的使用，若继续使用请联系作者")
                    break
                print("到期日期为 :", timeLenth,"天后，若继续使用请联系作者")
                i = datetime.datetime.now()
                if i.minute % 5==0 :
                    if write_flag==0:
                        write_flag=1
#                        ab=huobi_market.get_assets(account_id)
#                       # print(ab)
#                        sql.ins_assets(huobi_market,ab,account_id)
                else:
                    write_flag=0

                res=gridtradesys.strategy()
                time.sleep(gridtradesys.interval)
                if res<=-1:
    #                break
                    errInfo="'Cannot connect to proxy.', RemoteDisconnected('Remote end closed connection without response')"
                    print(errInfo)
                    logger.error(errInfo)

                    continue
                if len(accCfg.sym_list_value)>2:
                    print("")
                    res=gridtradesys1.strategy()
                    time.sleep(gridtradesys.interval)

