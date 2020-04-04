# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:35:08 2020

@author: Haiyi
@email: 806935610@qq.com
@wechart: yyy99966
@github: https://github.com/yyy999
"""

## ET智能量化交易网格系统简化开源版简介

本系统由具有多年量化专业开发经验的团队人员研发，是一个针对火币交易所的加密数字资产市场中币币交易开发的一套专用交易系统，系统设计融合了作者多年的金融外汇交易及数字资产市场交易经验，是一套智能7*24小时交易系统。系统对接火币官方接口，经过长达两年的不断测试与优化，云端化运行，安全可控，策略可定制，使用方便!
这是一个开源的单机版本,可以在本地运行
她以当前主流的网格策略为基本原则,然后进行了策略改进,自动适应数字货币市场中行情特点,特别是主流币种的交易节奏.
只需要简单的配置好高低交易区间和交易格子大小,就可以轻松挂机7*24小时交易,克服手工交易诸多弊端

当前版本：v3.0
### 项目文件使用说明
1. api.ini为对接火币交易所的相关参数配置文件,使用前,请先把自己在交易所申请的api键在这个文件中设置好
2. init.ini为交易系统的初始参数配置文件,交易和币种,网格区间及网格大小
3. fishtrade_main*.py为主程序文件
```
订制微信:yyy99966
```
开发环境:win10,spyder(anaconda3)


#ET量化交易web系统：[http://www.simplenet.top](http://www.simplenet.top/hb/ranking.php)
# 安装与使用指南

## Windows10 64位 环境

### 手动安装

#### 1.下载并安装最新版spyder(Anaconda3) 64位

下载地址如下：[Anaconda Distribution](https://www.anaconda.com/distribution/)


&nbsp;
#### 2.下载本项目并解压所有文件
#### 3.打开spyder加载本项目
在文件夹auto_fish中找到fishtrade_main200111.py文件，单击运行。

### 无需安装的编译版本
谷歌网盘下载https://drive.google.com/open?id=1SGligzL2rU4AHdrVwp538kDWCsLfXLNd
找到*.exe程序,可直接双击运行


#### 贡献代码

auto_fish使用Github托管其源代码，如果希望贡献代码请使用github的PR（Pull Request）的流程:

1. [创建 Issue](https://github.com/yyy999/auto_ma912/issues/new) - 对于较大的改动（如新功能，大型重构等）最好先开issue讨论一下，较小的improvement（如文档改进等）直接发PR即可

2. Fork [auto_fish](https://github.com/yyy999/auto_fish) - 点击右上角**Fork**按钮

3. Clone你自己的fork:
 ```git clone https://github.com/$userid/auto_fish.git```

4. 从**dev**创建你自己的feature branch:
```git checkout -b $my_feature_branch dev```

5. 在$my_feature_branch上修改并将修改push到你的fork上

6. 创建从你的fork的$my_feature_branch分支到主项目的**dev**分支的[Pull Request] -  [在此](https://github.com/yyy999/auto_fish/compare?expand=1)点击**compare across forks**，选择需要的fork和branch创建PR

7. 等待review, 需要继续改进，或者被Merge!

在提交代码的时候，请遵守以下规则，以提高代码质量：

  * 使用[autopep8](https://github.com/hhatto/autopep8)格式化你的代码。运行```autopep8 --in-place --recursive . ```即可。
  * 使用[flake8](https://pypi.org/project/flake8/)检查你的代码，确保没有error和warning。在项目根目录下运行```flake8```即可。



#### 项目捐赠

过去3年中收到过许多社区用户的捐赠，在此深表感谢！所有的捐赠资金都投入到了ET量化交易社区基金中，用于支持ET项目的运作。

在此强调一下：**ETopen是我们整个ET量化交易社区中的一个开源项目，可以永久免费使用！！！**

捐赠方式：微信：yyy99966（**林）

长期维护捐赠清单，请在留言中注明是项目捐赠以及捐赠人的名字。



### 其他内容
《ET量化开发实战进阶》在线课程，已经在微信公众号[**ET量化交易社区**]上线，50节内容覆盖从策略设计开发、参数回测优化，到最终实盘自动交易的完整量化业务流程。购买请扫描下方二维码关注后，点击菜单栏的【量化课程】按钮即可：

[!image](http://www.simplenet.top/hb/image/Mt4_ea999_s.jpg)
<p align="center">
  <img src ="http://www.simplenet.top/hb/image/Mt4_ea999_s.jpg"  width="200" height="200"/>
</p>

* [社区行为准则](https://github.com/yyy999/auto_ma912/blob/docs/rule.md)

#### 联系信息
 网站：http://www.simplenet.top

 QQ：806935610

 微信：yyy99966
<p align="center">
  <img src ="http://www.simplenet.top/hb/image/yyy99966_1.jpg"  width="200" height="200"/>

</p>

#### 版权说明

MIT




