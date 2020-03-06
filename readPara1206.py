# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 21:42:38 2019

@author: Haiyi
@email: 806935610@qq.com
@wechart: yyy99966
@github: https://github.com/yyy999

"""
import time
import os
import sys
import marketHelper1005 as mh
#         read apikey

def read_api_File(file="api.ini"):
    fo = open(file, "r",-1,'utf-8')
    list_key = []
    list_value = []
    for line in fo.readlines():                          #依次读取每行
        line = line.strip()                             #去掉每行头尾空白
        line = line.replace(' ','')                     #去掉行内空白
#        print ("读取的数据为: %s" % (line))
        tempList=line.split('=')
        list_key.append(tempList[0])
        list_value.append(tempList[1])
    # 关闭文件
    fo.close()
    return list_key,list_value
# =============================================================================
#
# =============================================================================
def read_Ini_File():
    # 打开文件
    fo = open("init.ini", "r",-1,'utf-8')
#    print ("文件名为: ", fo.name)
    list_symbol = []
    list_value = []
    for line in fo.readlines():                          #依次读取每行
        line = line.strip()                             #去掉每行头尾空白
        line = line.replace(' ','')                     #去掉行内空白
#        print ("读取的数据为: %s" % (line))
        tempList=line.split(',')
        print(tempList)
        list_symbol.append(tempList)
#        list_value.append(tempList[1])
    # 关闭文件
    fo.close()
    return list_symbol
# =============================================================================
# def 交易报告读取函数
# =============================================================================
def get_account_reports(fn):
            # 打开文件
    fo = open(fn, "r",-1,'utf-8')
#    print ("文件名为: ", fo.name)
    list_symbol = []
#    list_value = []
    #list.append('Baidu')
#    print ("更新后的列表 : ", list)
    s=fo.readline()
    #print(s)
    #str=""
    for line in fo.readlines():                          #依次读取每行
        line = line.strip()                             #去掉每行头尾空白
#        line = line.replace(' ','')                     #去掉行内空白
#        print ("读取的数据为: %s" % (line))
        tempList=line.split(',')
#        print(tempList)
        list_symbol.append(tempList)
#        list_value.append(tempList[1])
    # 关闭文件
    fo.close()
    return list_symbol
# =============================================================================
# count profit or loss
# =============================================================================
def count_profit_or_loss(listInfo,symbol):
    symbol=symbol.upper()
    buyAmounts=0
    sellAmounts=0
    for row in listInfo:
        if row[2]==symbol :
            sym=symbol.split('/')
            if row[3]=='买入' :
                buyAmounts+=1*float(row[6])
            else:
                sellAmounts+=float(row[6])-float(row[7].replace(sym[1],''))
    profitLoss=sellAmounts-buyAmounts
    print("{}={}".format(symbol,profitLoss))
    return profitLoss

def verify_usedRight():
#    your Encryption function加密功能
    pass
    return
# =============================================================================
#
# =============================================================================
if __name__ == "__main__":

    huobi = mh.Market()
    r=huobi.get_accountInfo()
    print(r)
##    r='mk0lklo0de-ac113e7d-ae07f4f9-4591b'

#    list=get_account_reports('History16.csv')
##    print(list)
#    sum=count_profit_or_loss(list,'eos/eth')
#
#    print(sum)
#    sum+=count_profit_or_loss(list,'mtn/eth')
#    print(sum)
#
#    sum+=count_profit_or_loss(list,'mtx/eth')
#    print(sum)
#
#    sum+=count_profit_or_loss(list,'tnb/eth')
#    print(sum)
#    sum_eth=sum
#    print("sum_eth=",sum)
#    sum=0
#    sum+=count_profit_or_loss(list,'eos/btc')
#    print(sum)
#    sum+=count_profit_or_loss(list,'mtn/btc')
#    print(sum)
#    closePrice=float(huobi.get_market_close('ethbtc'))
#    print(closePrice)
#    btc2eth=sum/closePrice
#    print(btc2eth)
#    sum=0
#    sum+=count_profit_or_loss(list,'eos/usdt')
#    print(sum)
#    closePrice=float(huobi.get_market_close('ethusdt'))
#    print(closePrice)
#    us=sum/closePrice
#    print(us)
#    sum_eth+=us+btc2eth
#    print(sum_eth)
##    list1=[]
#    listdir('log',list1)
#    list1=file_name('log')
#    print(list1)
