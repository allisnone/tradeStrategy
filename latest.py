
import urllib.request, urllib.parse, urllib.error
import string
import datetime
from datetime import date
import mailSMS
import time
ISOTIMEFORMAT = '%Y-%m-%d %X'

#https://www.chinastock.com.cn/trade/webtrade/login.jsp

#holding_stock=['000528','600115','601958','000599','600801','000631','000976','150222','000100','150178','603898','600958','603686','150172','000987','600028','600153','002282','000998','600489','600673','000667','000869','000821','600256','002043','601111','600398']
holding_stock=['601018','000987','002493','002678','603988','603158','002269','399006','000012','002663','002282','000153','600559','002556','600031','000998','600673','002501']#,'600673','000878','002389','600236','603993','600115','000599','000631','150222','000987','000998','000667','000821','002043','600398']

def form_url(stock_list):
    mystock_list=[]
    url=r'http://hq.sinajs.cn/list='
    for stock in stock_list:
        hold_stock=[stock,0,1]
        mystock_list.append(hold_stock)
        stock_url=''
        if stock>'600000':
            stock_url='s_sh'+stock+','
        else:
            stock_url='s_sz'+stock+','
        url=url+stock_url
    url=url[:-1]
    return mystock_list,url

mystock_list,url=form_url(holding_stock)

"""
mystock_list=[
         #code,holding_amount,buy_in_price
         ['600115',11000,6.03],
         ['601958',11000,6.03],
         ['000703',0,9.0],
         ['600395',0,11.43],
         ['600470',0,7.718],
         ['000538',0,64],
         ['601166',0,8.3],
         ['000767',0,8.3],
         ['002673',0,8.3],
         ['600830',0,1],
         ['600601',0,1],
         ['000976',0,1],
         ['000680',0,1],
         ['600801',0,1],
         ['600340',0,1],
         ['600078',0,1],
         ['000878',0,1],
         ['150118',0,1],
         ['150193',0,1],
         ['150158',0,1],
         ['150172',0,1],
         ['150201',0,1],
         ['150210',0,1],
         ['150218',0,1],
         ['150206',0,1],
         ['150158',0,1],
         ['150101',0,1],
         ['150131',0,1],
         ['000667',0,1],
         ['000100',0,1],
         ['002146',0,1]
         
         
]

url='http://hq.sinajs.cn/list=\
s_sh600115,\
s_sh601958,\
s_sz000703,\
s_sh600395,\
s_sh600470,\
s_sz000538,\
s_sh601166,\
s_sz000767,\
s_sz002673,\
s_sh600830,\
s_sz000528,\
s_sh600601,\
s_sz000680,\
s_sh600801,\
s_sh600340,\
s_sh600078,\
s_sz000878,\
s_sz150118,\
s_sz150193,\
s_sz150158,\
s_sz150172,\
s_sz150201,\
s_sz150210,\
s_sz150218,\
s_sz150206,\
s_sz150158,\
s_sz150101,\
s_sz150131,\
s_sz000667,\
s_sz000100,\
s_sz002146'
"""
proxy={'http':'http://jpyoip01.mgmt.ericsson.se:8080'}
expect_increase_rate=2.5
sell_decrease_rate=-3

def name_in_mystock(name):
    i=0
    for s in mystock_list:
        i=i+1
        if name.find(s[0]) is not -1:
            return i
    return 0

#url='http://stock.qq.com/i/'

def get_real_time_price(url,mystock_list,proxies):
    data = urllib.request.urlopen(url,proxies=proxy).read()
    #print data
    line = data.split('\n')

    #print line
    now=datetime.datetime.now()
    thisday=now.date()
    #while thisday.isoweekday():
    print('code    name      price     increase    increase(%)   mount(w)    myprice    porfile')
    for vv in line:
        aa = vv.split(',')
        """
        if aa[0]:
            #print aa[0].split('_')[3]
            #name  = aa[0].split('_')[3].replace('"','').replace('=','   ')
            name  = aa[0].split('_')[3].split('=')[0]
            cur   = string.atof(aa[1])
            wave  = string.atof(aa[2])
            per   = string.atof(aa[3])
            money = string.atof(aa[5].replace('";',''))
            index = name_in_mystock (name)
            if index :
                mypri = mystock[index-1][2]
                mypro = (cur - mypri) * mystock[index-1][1]
                print "%s %10.2f %10.2f %10.2f %12d w %10.3f %10.2f" %(name, cur, wave, per, money, mypri, mypro)
            else:
                print '%s %10.2f %10.2f %10.2f %12d w' %(name, cur, wave, per, money)
        """
        eventlist=[]
        if aa[0]:
            price_list=get_price_info(aa)
            if price_list[5]:
                print("%s %10.2f %10.2f %10.2f %12d w %10.3f %10.2f" %(price_list[0], price_list[1], price_list[2], price_list[3], price_list[4], price_list[5], price_list[6]))
            else:
                print('%s %10.2f %10.2f %10.2f %12d w' %(price_list[0], price_list[1], price_list[2], price_list[3], price_list[4]))
        
        if price_list:
            eventlist=get_state_info(price_list, expect_increase_rate, sell_decrease_rate, now)
            if eventlist:
                """"Trigger somemail here"""
                mailto_list=['104450966@qq.com']
                #mailSMS.sendMail(eventlist)
                sub=price_list[0] + eventlist[3]
                content=eventlist[4] +' '+ eventlist[5]+': current per_change is %s , please take action!' % price_list[3]
                #mailSMS.send_mail(mailto_list, sub, content)
                pass

#inputinfo=[code,cost,current_price,eventtype,date_time,eventinfo]
def get_price_info(aa):
    #print aa[0].split('_')[3]
    #code  = aa[0].split('_')[3].split('=')[0]
    #print aa
    code = aa[0].split('_')[3].replace('"','').replace('=',' ')
    cur   = string.atof(aa[1])
    wave  = string.atof(aa[2])
    per   = string.atof(aa[3])
    money = string.atof(aa[5].replace('";',''))
    index = name_in_mystock (code)
    price_list=[]
    if index :
        mypri = mystock_list[index-1][2]
        mypro = (cur - mypri) * mystock_list[index-1][1]
        price_list=[code, cur, wave, per, money, mypri, mypro]
    else:
        price_list=[code, cur, wave, per, money,0,0]
    return price_list

def get_state_info(price_list,expect_increase_rate,sell_decrease_rate,now):
    per=price_list[3]
    nowtime=now.strftime(ISOTIMEFORMAT)
    event_list=[]
    if per>expect_increase_rate:
        #print per,expect_increase_rate
        eventinfo='newhigh'
        eventtype='alarm'
        event_list=[price_list[0],price_list[5],price_list[1],eventtype,nowtime,eventinfo,price_list[3]]
    else:
        if per<sell_decrease_rate:
            eventinfo='newlow'
            eventtype='alert'
            event_list=[price_list[0],price_list[5],price_list[1],eventtype,nowtime,eventinfo,price_list[3]]
        else:
            #print 'no action'
            pass
    return event_list

def is_valid_trade_time(now=datetime.datetime.now()):
    now_string=now.strftime(ISOTIMEFORMAT)
    day_string=now_string[:11]
    is_valid_time_monring=now>datetime.datetime.strptime(day_string+'9:15:00') and now<datetime.datetime.strptime(day_string+'11:31:00')
    is_valid_time_noon=now>datetime.datetime.strptime(day_string+'13:00:00') and now<datetime.datetime.strptime(day_string+'15:01:00')
    return (is_valid_time_monring or is_valid_time_noon)

def refresh():
    now=datetime.datetime.now()
    week_daynum=now.date().isoweekday()
    if week_daynum<=5:
        #while is_valid_trade_time(now) :
        while True:
            print('refresh')
            get_real_time_price(url,mystock_list,proxy)
            time.sleep(60)
            now=datetime.datetime.now()

refresh()


#price_list=[current,high,low]
def msg_trigger(cur_price,max,min):
    if cur_price>=max:
        max=cur_price
    else:
        if cur_price<min:
            min=cur_price
        else:
            pass
        
    price_list=[]
    return


def find_boduan(data_list):
    indx=0
    count=len(data_list)
    max=data_list[0]
    min=data_list[0]
    split_list=[]
    split_list.append(max)
    indx=1
    action=''
    if data_list[0]>data_list[1]:
        action='find_min'
    else:
        action='find_max'
    lst_value=data_list[(count-1)]
    while indx<(count-1) and indx>=1:
        value=data_list[indx]
        #print value,action,indx
        if action=='find_max':
            #print min,max
            if value>=max:
                max=value
                action='find_max'
            else:
                last_value=data_list[indx-1]
                min=value
                max=last_value
                split_list.append(last_value)
                action='find_min'
                pass
        else:
            if action=='find_min':
                #print min,max
                if value<=min:
                    min=value
                    action='find_min'
                else:
                    last_value=data_list[indx-1]
                    max=value
                    min=last_value
                    split_list.append(last_value)
                    action='find_max'
                    pass
            else:
                pass
        indx=indx+1
    split_list.append(lst_value)
    return split_list