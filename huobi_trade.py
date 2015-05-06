#!/usr/bin/python
# -*- coding: utf-8 -*-

#team: Serengeti 
# Lu Bin    lubinsz@gmail.com
# Yang sen  nuaays@gmail.com

import huobi
import time

email = ""
password = ""

if __name__ == '__main__':
    client = huobi.Huobi(email, password)
#    resultBuy = client.buy(3, 1)
#    print resultBuy
#    if resultBuy == 0:
#        print 'get True'
#    else:
#        print 'get False'
#        print resultBuy
#        mycheck = client.check_order(resultBuy)
#        if mycheck == True:
#           print 'check true'
#           client.cancel(resultBuy)
#        else:
#           print 'check false'
#    client.sell(3, 3)
#    client.get_market_depth()
#    client.get_all_orders()
#    pass

#    while 1:
#        time.sleep(5)
#        client.get_market_depth()
#        print 'bblu: ok...'
#        #print len(client.buy_list)
   
#        if len(client.buy_list) != 0:
#            buy_amount = client.buy_list[0]['amount'] + client.buy_list[1]['amount'] + client.buy_list[2]['amount']
#            sell_amount = client.sell_list[0]['amount'] + client.sell_list[1]['amount'] +client.sell_list[2]['amount'] +client.sell_list[3]['amount'] +client.sell_list[4]['amount'] + client.sell_list[5]['amount']
#            print 'bblu buy_amount:%d'%(buy_amount)
#            print 'bblu sell_amount:%d'%(sell_amount)

    client.arbitrage()  
#    xx = client.get_ticker_BitStamp()   
#    print xx
