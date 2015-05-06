#/usr/bin/env python
# -*- coding: utf-8 -*-
 
import sys,os
import cPickle as p
import time
import requests
import httplib
import json
import urllib
import urllib2
import cookielib
import random 
import re
import ticker_btce

class Huobi():
    (TRADE_BUY, TRADE_SELL) = range(2)
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookiesFile = 'huobi_cookies.dat'
        self.debugFile = '/dev/shm/date.log'
        self.loginUrl = 'https://www.huobi.com/account/login.php'
        self.tradeUrl = 'https://www.huobi.com/trade/index.php'
        self.orderUrl = 'https://www.huobi.com/trade/index.php'
        self.cancelUrl = 'https://www.huobi.com/trade/?a=cancel&id='
        self.http_headers={'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'}
        self.tickerBitStamp='https://www.bitstamp.net/api/ticker/'
        self.timeout = 30
        self.exchangeRate =  6.09
        self.offset = 1 
        self.threshold_multi = 5 
        self.threshold_number = 100

        self.buy_list = [] 
        self.sell_list = []
        self.veryfyBuy = 'myModalBuy'
        self.veryfySell = 'myModalSell'

        self.maxSell = 2 
        self.m_buy = 0
        self.m_buy_id = 0
        self.m_buy_price = 0
        self.m_sell_price = 0
        self.m_trade_amount = 0.51 
        self.m_trade_profit_low = 0.9 
        self.m_trade_profit_high = 4.9 
        self.m_trade_profit_highest = 9.9 
        self.m_amount = 0
        self.m_retry = 0
        self.m_check = 0
        self.m_sell = 0
        self.m_catch_it = 0

        self.m_global_count = 0
        self.m_global_price = 0

        self.m_login_count = 50
        self.result_fullOrder = 100
        self.login()

    def login (self):
        print 'Login ....'
        try:
            session = requests.session()
            session.headers.update(self.http_headers)

            cookies = self.load_cookies(self.cookiesFile)
            htmlLogin = session.post(self.loginUrl,data={"email":self.email,"password":self.password},timeout=self.timeout)
            self.save_cookies (self.cookiesFile,session.cookies)
        except:
            print 'login crashed'
            return

    def save_cookies(self, cookiesFile,cookies):
        try:
                with open(cookiesFile,'w') as f:
                        p.dump(requests.utils.dict_from_cookiejar(cookies),f)
                        #print 'Saved'
                        f.close()
        except:
                print 'Save cookies failed', sys.exc_info()[0]
                sys.exit(99)

    def load_cookies(self, cookiesFile):
        try:
                with open (cookiesFile,'r') as f:
                        cookies=requests.utils.cookiejar_from_dict(p.load(f))
                        f.close()
        except:
                cookies=''
        return cookies

    def save_file(self, destFile, data):
        try:
                with open(destFile, 'w') as f:
                        f.write(data)
                        print 'Saved'
                        f.close()
        except:
                print 'Save data failed', sys.exe_info()[0]
                sys.exit(99)
 
    def buy(self, price, amount):
      try:  
        print 'buy..'
        session = requests.session()
        session.headers.update(self.http_headers)
                
        cookies = self.load_cookies(self.cookiesFile)
        session.cookies.update(cookies)
        #verfy if the cookies work, if not work del it and rebuild
        htmlTrade = session.post(self.tradeUrl,data={"a":"do_buy","price":price,"amount":amount},timeout=self.timeout)
        myModalBuy = re.findall(self.veryfyBuy, htmlTrade.text)
        print len(myModalBuy)
        if len(myModalBuy) == 1:
            return 0 
        else:
            pattern = re.compile(r"buy_btc_edit\((.*?)\)")
            res = pattern.findall(htmlTrade.text)
            if len(res) != 0: 
                return res[0] 
            else:
                return 0
      except:
        return 0 

    def sell(self, price, amount):
      try:
        session = requests.session()
        session.headers.update(self.http_headers)

        cookies = self.load_cookies(self.cookiesFile)
        session.cookies.update(cookies)
        #verfy if the cookies work, if not work del it and rebuild
        htmlTrade = session.post(self.tradeUrl,data={"a":"do_sell","price":price,"amount":amount},timeout=self.timeout)
        myModalSell = re.findall(self.veryfySell, htmlTrade.text)
        print len(myModalSell)
        if len(myModalSell) > 0:
            return (len(myModalSell) -1)
        else:
            return 0
      except:
        return -1 

    def trade(self, trade_type, price, amount):
        pass
 
    def get_account_info(self, post_data={}):
        pass
 
    def get_market_depth(self):
        Huobi_staticmarket_Url = "https://detail.huobi.com/staticmarket/detail.html"

        jsoncallbackValue = "jQuery171024871149915270507_"

        timestamp = time.time() * 1000 - 200
        #print('sleep %d'%(timestamp))
        #run( timestamp )
        payloadValue = jsoncallbackValue + "%13d" % timestamp
        payload = { 'jsoncallback': payloadValue }

        try:
            req = requests.get( Huobi_staticmarket_Url, params=payload, allow_redirects=False, timeout=2 )
            if( req.status_code == requests.codes.ok ):
                #print "URL : " + req.url
                #print req.text
                remote_data = req.text
                remote_data = remote_data[12:-1]
                #print(remote_data)           
                remote_data = json.loads(remote_data)
                #print 'syrenbase buy:'
                self.buy_list = remote_data['buys']
                #print(self.buy_list)
            
                #print 'syrenbase sell:'
                self.sell_list = remote_data['sells'] 
                #print(self.sell_list)
                #print(self.sell_list[0]['price'])
                #print(self.sell_list[0]['amount'])
                return
        except:
            self.buy_list = []
            self.sell_list = []
            return

    def cancel(self, id):
        print 'cancel ....'
        try:
            session = requests.session()
            session.headers.update(self.http_headers)

            cookies = self.load_cookies(self.cookiesFile)
            session.cookies.update(cookies)
            htmlCancel = session.get(self.cancelUrl+id,timeout=self.timeout)
            time.sleep(1)
            
            result_fullOrder = self.get_num_buyOrders()
            if result_fullOrder == 0:
                return True
            else:
                return False
        except:
            return False

    def get_orders(self, id=None, open_only=True, post_data={}):
        pass
 
    def get_all_orders(self):
        print 'Get all orders ....'
        session = requests.session()
        session.headers.update(self.http_headers)

        cookies = self.load_cookies(self.cookiesFile)
        session.cookies.update(cookies)
        htmlOrder = session.get(self.orderUrl,timeout=self.timeout)
#        print(htmlOrder.content)
        pattern = re.compile(r"buy_btc_edit\((.*?)\)")
        res = pattern.findall(htmlOrder.text)
#        self.save_file(self.debugFile, htmlOrder.content)  
        print 'bblu ...'
        print len(res)
        print res[0],res[1],res[2]

        myModalBuy = re.findall('myModalBuy',htmlOrder.text)
        print len(myModalBuy)
   
    def get_num_sellOrders(self):
        print 'Get number of sell orders ....'
        try:
            session = requests.session()
            session.headers.update(self.http_headers)

            cookies = self.load_cookies(self.cookiesFile)
            session.cookies.update(cookies)
        
            htmlOrder = session.get(self.orderUrl,timeout=self.timeout)

            myModalSell = re.findall(self.veryfySell, htmlOrder.text)
            #print len(myModalSell)
            if len(myModalSell) > 0:
                return (len(myModalSell) -1)
            else:
                return 0
        except:
            print 'get_num_sellOrders crash..return 0 here.'
            return 0

    def get_num_buyOrders(self):
        print 'Get number of buy orders ....'
        try:
            session = requests.session()
            session.headers.update(self.http_headers)

            cookies = self.load_cookies(self.cookiesFile)
            session.cookies.update(cookies)

            htmlOrder = session.get(self.orderUrl,timeout=self.timeout)

            myModalBuy = re.findall(self.veryfyBuy, htmlOrder.text)
            print len(myModalBuy)
            if len(myModalBuy) > 0:
                return (len(myModalBuy) -1)
            else:
                return 0
        except:
            print 'get_num_buyOrders crash..return 0 here.'
            return 0
 
    def check_order(self, id):
        print 'check ...'
        if id == 0:
            return False 
        try:
            session = requests.session()
            session.headers.update(self.http_headers)

            cookies = self.load_cookies(self.cookiesFile)
            session.cookies.update(cookies)
            htmlOrder = session.get(self.orderUrl,timeout=self.timeout)
       
            myOrder = re.findall(id, htmlOrder.text)
            if len(myOrder) == 0:
                return False
            else:
                return True
        except:
            return False 
    
    def get_ticker_BitStamp(self):
        print 'get ticker of BitStamp'
        try:
            session = requests.session()
            session.headers.update(self.http_headers)

            cookies = self.load_cookies(self.cookiesFile)
            session.cookies.update(cookies)
            htmlBitStamp = session.get(self.tickerBitStamp, timeout = self.timeout)
            
            remote_data = json.loads(htmlBitStamp.text)
            
            last = float(remote_data['last'])
            return last*self.exchangeRate
        except:
            return False
      
    def arbitrage(self):
        print 'arbitrage...' 
        
        try:
            while 1:
#                if self.m_login_count == 0:
#                    self.login()
#                    self.m_login_count = 300
#                else:
#                    self.m_login_count = self.m_login_count -1

#                if self.m_global_count == 0:
#                    self.m_global_count = 5
#                    tickerGlobal = self.get_ticker_BitStamp()
#                    if tickerGlobal !=False:
#                        self.m_global_price = tickerGlobal
#                        print 'bblu Global price: %f'%(self.m_global_price)
#                else:
#                    self.m_global_count = self.m_global_count -1 

                if self.m_check == 1:
                    if self.m_buy == 1:
                        self.get_market_depth()

                        if len(self.buy_list) < 3:
                            continue
                        print self.buy_list[0]['price']
                        if len(self.buy_list) != 0:
                            buy_amount = float(self.buy_list[0]['amount']) + float(self.buy_list[1]['amount']) + float(self.buy_list[2]['amount']) + float(self.buy_list[3]['amount']) + float(self.buy_list[4]['amount'])
                            sell_amount = float(self.sell_list[0]['amount']) + float(self.sell_list[1]['amount']) + float(self.sell_list[2]['amount']) + float(self.sell_list[3]['amount']) + float(self.sell_list[4]['amount']) + float(self.sell_list[5]['amount'])

                            if ( sell_amount > (self.threshold_multi-2)*buy_amount) and ( sell_amount > (self.threshold_number - 40) ):
                                result_cancel = self.cancel(self.m_buy_id)
                                time.sleep(1)
                                result_cancel = self.cancel(self.m_buy_id)
                                if result_cancel != True:
                                    print 'bblu cancel 1 fail....'
                                    self.m_retry = 1
                                    continue
                                else:
                                    print 'bblu cancel 1 ok...'
                                    self.m_buy = 0
                                    self.m_check = 0
                                    self.m_retry = 0

                        result_noorder = self.check_order(self.m_buy_id)
                        if result_noorder == True:
                            if self.m_retry == 0:
                                result_cancel = self.cancel(self.m_buy_id)
                                time.sleep(1)
                                result_cancel = self.cancel(self.m_buy_id)
                                if result_cancel != True:
                                    print 'bblu cancel fail....'
                                    self.m_retry = 1
                                    continue 
                                else:
                                    print 'bblu cancel ok...'
                                    self.m_buy = 0
                                    self.m_check = 0
                                    self.m_retry = 0
                            else:
                                time.sleep(5)
                                self.m_retry = self.m_retry -1
                                print 'bblu: continue %d'%(self.m_retry)
                                continue 
                        else:
                            print 'bblu get here...'
                            #time.sleep(1)
                            #buy success, so sell it + 3 
                            if self.m_buy_price > (self.m_global_price - 20) : 
                                self.m_sell_price = self.m_buy_price + self.m_trade_profit_low 
                            elif self.m_buy_price > (self.m_buy_price -60):
                                self.m_sell_price = self.m_buy_price + self.m_trade_profit_high                 
                            else:
                                self.m_sell_price = self.m_buy_price + self.m_trade_profit_highest
                            #print 'bblu bcte:%f'%(self.m_global_price) 
                            print 'bblu sell:%f'%(self.m_sell_price)
                            self.login()
                            checkSell = self.sell(self.m_sell_price,self.m_trade_amount)
                            time.sleep(1)
                            checkSell = self.sell(self.m_sell_price,self.m_trade_amount)
                            if ( checkSell == -1):
                                print 'bblu sell fail...'
                                time.sleep(10)
                                self.login()
                                time.sleep(5)
                                checkSell = self.sell(self.m_sell_price,self.m_trade_amount)

                            print 'bblu sell ok:%d'%(checkSell)
                            self.result_fullOrder = self.get_num_sellOrders()
                            self.m_check = 0
                            self.m_buy = 0
                            time.sleep(1)

                if self.m_login_count == 0:
                    self.login()
                    self.m_login_count = 300
                else:
                    self.m_login_count = self.m_login_count -1

                if self.m_global_count == 0:
                    self.m_global_count = 10 
#                    tickerBTCE = ticker_btce.instance_ticker()
#                    print 'bblu get btce...'
#                    if tickerBTCE != False:
#                        self.m_global_price  = float(tickerBTCE['ticker']['last'])*self.exchangeRate
#                        print 'bblu BtcE %f'%(self.m_global_price)
                    self.login()
                    tickerGlobal = self.get_ticker_BitStamp()
                    if tickerGlobal !=False:
                        self.m_global_price = tickerGlobal
                        print 'bblu Global price: %f'%(self.m_global_price)
                else:
                    self.m_global_count = self.m_global_count -1
                 
                if (self.result_fullOrder > self.maxSell) or (self.result_fullOrder == 0) : 
                    self.result_fullOrder = self.get_num_sellOrders()   
                    print self.result_fullOrder 
                    if (self.result_fullOrder > self.maxSell) or (self.result_fullOrder == 0):
                        print 'bblu: order is full'
                        time.sleep(30)
                        continue

                print 'bblu: start....'
                time.sleep(1)
                print(time.strftime('%H-%M-%S',time.localtime(time.time())))
#                self.save_file(self.debugFile, time.strftime('%H-%M-%S',time.localtime(time.time()))+ '***' + str(self.result_fullOrder) + '*')  
                self.get_market_depth()
               
                if len(self.buy_list) < 3:
                   continue
                print self.buy_list[0]['price'] 
                if float(self.buy_list[0]['price']) > ( float(self.m_global_price) + self.offset):
                    print 'bblu:price is too high, sleep 60s...'
                    time.sleep(120)
                    self.m_global_count = 0
                    self.m_login_count = 0
                    continue
                if len(self.buy_list) != 0: 
                    buy_amount = float(self.buy_list[0]['amount']) + float(self.buy_list[1]['amount']) + float(self.buy_list[2]['amount']) + float(self.buy_list[3]['amount']) + float(self.buy_list[4]['amount'])                 
                    sell_amount = float(self.sell_list[0]['amount']) + float(self.sell_list[1]['amount']) + float(self.sell_list[2]['amount']) + float(self.sell_list[3]['amount']) + float(self.sell_list[4]['amount']) + float(self.sell_list[5]['amount'])
                    print self.buy_list[0]['price']
                    print 'bblu buy_amount:%d'%(buy_amount)
                    print 'bblu sell_amount:%d'%(sell_amount)
                
                    if ( buy_amount > self.threshold_multi*sell_amount) and ( buy_amount > self.threshold_number):
                        for i in range(0,4):
                            if float(self.buy_list[i]['amount']) > (buy_amount)/3:
                                self.m_buy_price = float(self.buy_list[i]['price']) + 0.01
                                print 'bblu buy 1...'
                                break
                            else:
                                self.m_buy_price = float(self.buy_list[0]['price']) + 0.01 
#                        self.m_buy_price = float(self.buy_list[0]['price']) + 0.01
                        self.m_buy_id = self.buy(self.m_buy_price, self.m_trade_amount)
                        if (self.m_buy_id == 0):
                            print 'bblu buy fail...'
                            self.m_buy_id = self.buy(self.m_buy_price, self.m_trade_amount)
                            if(self.m_buy_id == 0):
                                continue

                        print 'bblu buy: %f...'%(self.m_buy_price)
                        self.result_fullOrder = self.get_num_sellOrders()
                        self.m_buy = 1
                        self.m_check = 1
                        self.m_retry = 10 
                        time.sleep(1) 
        finally:
            print 'bblu: end............'        
