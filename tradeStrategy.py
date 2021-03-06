# -*- coding:utf-8 -*-
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os,sys,time

import tushare as ts
import json
import string

import urllib.request, urllib.error, urllib.parse
import datetime
import threading
import smtplib
from email.mime.text import MIMEText
import code

import pdsql as ps


ISOTIMEFORMAT='%Y-%m-%d %X'
#ISODATEFORMAT='%Y%m%d'
ISODATEFORMAT='%Y-%m-%d'

#ROOT_DIR='C:/work/stockAnalyze'
ROOT_DIR="C:/中国银河证券海王星/T0002"

RAW_HIST_DIR=ROOT_DIR+'/export/'
HIST_DIR=ROOT_DIR+'/hist/'
HIST_FILE_TYPE='.csv'


#get the all file source data in certain DIR
def get_all_code(hist_dir):
    all_code=[]
    for filename in os.listdir(hist_dir):#(r'ROOT_DIR+/export'):
        code=filename[:-4]
        if len(code)==6:
            all_code.append(code)
    return all_code

#get the history raw data for certain code: ['date','open','high','low','close','volume','rmb']
"""data from 'export' is update from trade software everyday """
def get_raw_hist_df(code_str,latest_count=None):
    file_type='csv'
    file_name=RAW_HIST_DIR+code_str+'.'+file_type
    column_list=['date','open','high','low','close','volume','rmb']
    #print('file_name=',file_name)
    df_0=pd.read_csv(file_name,names=column_list, header=0,encoding='gb2312')#'utf-8')   #for python3
    #print df_0
    #delete column 'rmb' and delete the last row
    del df_0['rmb']
    df=df_0.ix[0:(len(df_0)-2)]
    #print df
    
    """"check"""
    df= df.set_index('date')
    #df.index.name='date'
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    df.index.name=this_time_str
    """check"""
    hist_dir=ROOT_DIR+'/hist/'
    file_type='csv'
    file_name=hist_dir+code_str+'.'+file_type
    #print df
    df.to_csv(file_name)
    hist_dir=ROOT_DIR+'/update/'
    file_name=hist_dir+code_str+'.'+file_type
    df.to_csv(file_name)
    #column_list=['date','open','high','low','close','volume']
    if latest_count!=None and latest_count<len(df):
        df=df.tail(latest_count)
    return df

def write_hist_index():
    """
    hist_sh_df=ts.get_hist_data('sh')
    hist_sz_df=ts.get_hist_data('sz')
    hist_hs300_df=ts.get_hist_data('hs300')
    hist_sz50_df=ts.get_hist_data('sz50')
    hist_zxb_df=ts.get_hist_data('zxb')
    hist_cyb_df=ts.get_hist_data('cyb')
    """
    #print datetime.datetime.now()
    index_list=['sh','sz','zxb','cyb','hs300','sz50']
    index_dir=ROOT_DIR+'/index/'
    file_type='csv'
    for index_str in index_list:
        print('Getting hist data for %s index ...' % index_str)
        file_name=index_dir+index_str+'.'+file_type
        index_df=ts.get_hist_data(index_str)
        index_df.to_csv(file_name)
        print('Getting hist data for %s index is completed' % index_str)
    
    #print datetime.datetime.now()
def get_hist_index(index_str):
    index_dir=ROOT_DIR+'/index/'
    file_type='csv'
    index_list=['sh','sz','zxb','cyb','hs300','sz50']
    file_name=index_dir+index_str+'.'+file_type
    column_list=['date','open','high','close','low','volume','price_change','p_change','ma5','ma10','ma20','v_ma5','v_ma10','v_ma20']
    index_df=pd.read_csv(file_name)#,names=column_list)
    index_df= index_df.set_index('date')
    return index_df

def get_file_timestamp(file_name):
    file_mt_str=''
    try:
        file_mt= time.localtime(os.stat(file_name).st_mtime)
        file_mt_str=time.strftime("%Y-%m-%d %X",file_mt)
    except:
        #file do not exist
        pass
    return file_mt_str

#get the history data for certain code: ['date','open','high','low','close','volume']
def get_hist_df(code_str,analyze_type,latest_count=None):
    target_dir=''
    if analyze_type=='history':
        target_dir=ROOT_DIR+'/hist/'
    else:
        if analyze_type=='realtime':
            target_dir=ROOT_DIR+'/update/'
        else:
            pass
    file_type='csv'
    code_str=str(code_str)
    file_name=target_dir+code_str+'.'+ file_type
    #print 'file_name:',file_name
    data={}
    column_list=['date','open','high','low','close','volume']#,'rmb']
    df=pd.DataFrame(data=data,columns=column_list)
    now_time=datetime.datetime.now()
    file_mt_str=now_time.strftime("%Y-%m-%d %X")
    try:
        hist_df=pd.read_csv(file_name,names=column_list, header=0)
        #column_list=['date','open','high','low','close','volume']
        """"check"""
        #df= df_0.set_index('date')
        #df=df_0.ix[:'2015-05-22']
        #df.index.name='date'
        """check"""
        default_count=10000
        if latest_count!=None and latest_count<len(hist_df):
            default_count=latest_count
        df=hist_df.tail(min(default_count,len(hist_df)))
            #df=df.set_index('date')
        file_mt_str= get_file_timestamp(file_name)
    except:
        pass
    return df,file_mt_str
  

def f_code_2sybol(code_f):
    #print 'code_f:',code_f
    s1=str(code_f)
    #print 's1=',s1
    zero_str={6:'',5:'0',4:'00',3:'000',2:'0000',1:'00000'} #,2:'00000',1:'00000'}
    le_n=len(s1)
    code_str=zero_str[le_n]+s1 #[:-2]
    #print 'code_str=',code_str
    return code_str

#to get the latest trade day
def get_latest_trade_date(this_date=None):
    except_trade_day_list=['2015-05-01','2015-06-22','2015-09-03','2015-10-01','2015-10-02','2015-10-06','2015-10-07','2015-10-08']
    this_day=datetime.datetime.now()
    #if this_day.hour>=0 and this_day.hour<=9:
    #    this_day=this_day+datetime.timedelta(days=-1)
    if this_date!=None:
            this_day=this_date
    open_str=' 09:31:00'
    this_str=this_day.strftime('%Y-%m-%d %X')
    if this_str<this_str[:10]+open_str and (this_day.hour>=0 and this_day.hour<=9):
        this_day=datetime.datetime.strptime(this_str,'%Y-%m-%d %X')+datetime.timedelta(days=-1)
        this_str=this_day.strftime('%Y-%m-%d')  
    latest_day_str=''
    this_str=this_str[:10]
    while this_str>='2010-01-01':
        if this_day.isoweekday()<6 and (this_str not in except_trade_day_list):
            latest_day_str = this_str
            break
        else:
            this_day=this_day+datetime.timedelta(days=-1)
            this_str=this_day.strftime('%Y-%m-%d')  
    return latest_day_str

#to get the latest trade day
def get_last_trade_date(given_latest_datetime=None):
    latest_datetime=datetime.datetime.now()
    if given_latest_datetime:
        latest_datetime=given_latest_datetime
    else:
        latest_day_str=get_latest_trade_date()
        print('latest_day_str=',latest_day_str)
        latest_datetime_str=latest_day_str+' 10:00:00'
        latest_datetime=datetime.datetime.strptime(latest_datetime_str,'%Y-%m-%d %X')
    last_datetime=latest_datetime+datetime.timedelta(days=-1)
    last_date_str=get_latest_trade_date(last_datetime)
    print('last_date_str=',last_date_str)
    return last_date_str

def is_trade_time(latest_trade_date):
    this_time=datetime.datetime.now()
    this_str=this_time.strftime('%Y-%m-%d %X')
    #latest_trade_date=get_latest_trade_date()
    return this_str>=(latest_trade_date+ ' 09:31:00') and this_str <= (latest_trade_date + ' 15:00:00')

def is_trade_time_now():
    except_trade_day_list=['2015-05-01','2015-06-22','2015-09-03','2015-10-01','2015-10-02','2015-10-06','2015-10-07','2015-10-08']
    now_timestamp=time.time()
    this_time=datetime.datetime.now()
    hour=this_time.hours
    minute=this_time.minutes
    is_trade_time=((hour>=9 and minute>=30) and (hour<=11 and minute<=30)) or (hour>=13 and hour<=15)
    is_working_date=this_time.isoweekday()<6 and (this_date not in except_trade_day_list)
    return is_trade_time and is_working_date

def get_pass_time():
    """
    提取已开市时间比例
    :param this_time: ，string
    :return:,float 
    """
    pass_second=0.0
    if not is_trade_time_now():
        return pass_second
    this_time=datetime.datetime.now()
    hour=this_time.hour
    minute=this_time.minute
    second=this_time.second
    total_second=4*60*60
    if hour<9 or (hour==9 and minute<=30):
        pass
    elif hour<11 or (hour==11 and minute<=30):
        pass_second=(hour*3600+minute*60+second)-(9*3600+30*60)
    elif hour<13:
        pass_second=2*60*60
    elif hour<15:
        pass_second=2*60*60+(hour*3600+minute*60+second)-13*3600
    else:
        pass_second=total_second
    return round(round(pass_second/total_second,2),2)

    #is_trade_time=now_timestamp>start_timestamp and 
def get_ma_list(close_list,ma_num):
    ma_list=[]
    i=0
    while (i<len(close_list)):
        k=0
        if i<ma_num:
            temp_list=close_list[0:(i+1)]
            ma=round(round(sum(temp_list),2)/len(temp_list),2)
            ma_list.append(ma)
        else:
            temp_list=close_list[(i-(ma_num-1)):(i+1)]
            ma=round(round(sum(temp_list),2)/ma_num,2)
            ma_list.append(ma)
        i=i+1
    #print ma_list,len(ma_list)
    return ma_list

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

def specify_rate_range(init_rate=-1.5,rate_interval=0.5,range_num=10):
    """
    return the range to seperate the rate in class 
    """
    rate_list=[]
    for i in range(0,range_num):
        rate=round(init_rate+i*rate_interval,1)
        rate_list.append(rate)
        if rate>10.95 or rate <-9.0:
            break
    return rate_list

def get_today_df():
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    """
    latest_trade_day=get_latest_trade_date()
    latest_trade_end=latest_trade_day + ' 15:00:00'
    latest_trade_before_start=latest_trade_day + ' 09:15:00'
    """
    latest_trade_day_str=get_latest_trade_date()
    latest_trade_time_str=latest_trade_day_str + ' 15:00:00'
    pre_name='all'
    #if profix_name != None:
    #    pre_name=profix_name
    file_name=ROOT_DIR+'/data/%s.csv'%(pre_name+latest_trade_day_str)
    file_time_str=get_file_timestamp(file_name)
    
    data={}
    column_list=['code','changepercent','trade','open','high','low','settlement','volume','turnoverratio']
    today_df=pd.DataFrame(data,columns=column_list)#,index=['
    if not is_trade_time(get_latest_trade_date()):
        if file_time_str:
            #if file_time_str>=latest_trade_day_str+' 13:00:00':
            #print '---------------1'
            today_df=read_today_df(file_name)
            today_df.index.name=latest_trade_time_str
            #return today_df,file_time_str
        else:
            #print '---------------2'
            today_df=ts.get_today_all()
            del today_df['name']
            today_df=write_today_df(file_name,today_df)
            today_df= today_df.set_index('code')
            file_time_str=get_file_timestamp(file_name)
            today_df.index.name=latest_trade_time_str
            #return today_df,this_time_str
    else:
        # read the real time update data on today
        #print '---------------3'
        today_df=ts.get_today_all()
        del today_df['name']
        today_df= today_df.set_index('code')
        today_df.index.name=this_time_str
        #return today_df,this_time_str
    if today_df.empty:
        return today_df
    today_df=today_df.astype(float)
    today_df.insert(6, 'h_change', (100*(today_df.high-today_df.settlement)/today_df.settlement).round(2))
    today_df.insert(7, 'l_change', (100*(today_df.low-today_df.settlement)/today_df.settlement).round(2))
    today_df['atr']=np.where((today_df['high']-today_df['low'])<(today_df['high']-today_df['settlement']),(today_df['high']-today_df['settlement']),(today_df['high']-today_df['low'])) #temp_df['close'].shift(1)-temp_df['low'])
    today_df['atr']=np.where(today_df['atr']<(today_df['settlement']-today_df['low']),(today_df['settlement']-today_df['low']),today_df['atr'])
    today_df['atr_ocp']=(today_df['trade']-today_df['open'])/today_df['atr']
    today_df['atr_r']=today_df['atr']/today_df['settlement']*100.0
    return today_df,this_time_str

def write_today_df(file_name,today_df):
    #latest_trade_day_str=get_latest_trade_date()
    #today_df=ts.get_today_all()
    #del today_df['name']
    #today_df1=today_df.set_index('code')
    #pre_name='all'
    #file_name=ROOT_DIR+'/data/%s.csv'%(pre_name+latest_trade_day_str)
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    today_df.index.name=this_time_str
    today_df.to_csv(file_name) #,encoding='GB18030')
    return today_df
        
def read_today_df(file_name):
    column_list=['code','changepercent','trade','open','high','low','settlement','volume','turnoverratio']
    
    today_df=pd.read_csv(file_name,names=column_list)# header=1)
    #all_codes_f=today_df['code'].values.tolist()
    #print all_codes_f
    """
    all_codes=[]
    if all_codes_f:
        for code_f in all_codes_f:
            code=f_code_2sybol(code_f)
            all_codes.append(code)
    all_codes=all_codes[1:]
    today_df['code']=pd.Series(all_codes)
    """
    df= today_df.set_index('code')
    #this_time=datetime.datetime.now()
    #this_time_str=this_time.strftime('%Y-%m-%d %X')
    #print 'read_today_df,index.name',df.index.name
   # df.index.name=this_time_str
    df=df.ix[1:]
    #print df
    return df

def update_one_hist(code_sybol,today_df,today_df_update_time):
    #latest_trade_day_str=get_latest_trade_date()
    #print latest_trade_day_str
    #today_df_update_time=today_df.index.name
    #print 'today_df_update_time=',today_df_update_time
    #print today_df
    today_str=today_df_update_time[:10]
    #print 'today_str=',today_str
    hist_df,file_mt=get_hist_df(code_sybol,'history')
    #print 'hist_df0=',hist_df
    #print 'file_mt=',file_mt
    date_list=hist_df['date'].values.tolist()
    #print date_list
    last_hist_date=date_list[-1]
    #print 'last_hist_date=',last_hist_date
    if file_mt>today_df_update_time:
        #print 'update_one_hist1, if1'
        pass
    else:
        #print 'update_one_hist, else1'
        if last_hist_date==today_str:
            hist_df=hist_df.head(len(hist_df)-1)
            #print 'update_one_hist1,hist_df1=',hist_df
            print(last_hist_date)
        else:
            #print 'update_one_hist1, else2'
            pass
        today_df=today_df.astype(float)
        code_value=today_df.ix[code_sybol].values.tolist()
        open_price=today_df.ix[code_sybol].open
        high_price=today_df.ix[code_sybol].high
        low_price=today_df.ix[code_sybol].low
        current_price=today_df.ix[code_sybol].trade
        last_price=today_df.ix[code_sybol].settlement
        volume=today_df.ix[code_sybol].volume
        """
        open_price=round(today_df.ix[code_sybol]['open'].mean(),2)
        high_price=round(today_df.ix[code_sybol]['high'].mean(),2)
        low_price=round(today_df.ix[code_sybol]['low'].mean(),2)
        current_price=round(today_df.ix[code_sybol]['trade'].mean(),2)
        last_price=round(today_df.ix[code_sybol]['settlement'].mean(),2)
        volume=round(today_df.ix[code_sybol]['volume'].mean(),2)
        """
        #hist_value=[code_value[3],code_value[4],code_value[5],code_value[2],code_value[7]]
        data={'date':[today_str],'open':open_price,'high':high_price,'low':low_price,'close':current_price,'volume':volume}
        column_list=['date','open','high','low','close','volume']
        hist_today_df=pd.DataFrame(data,columns=column_list)#,index=['2015-05-15'])
        hist_df=hist_df.append(hist_today_df,ignore_index=True)
        #print hist_today_df
        #print hist_df
        #print hist_df_updated
        hist_df= hist_df.set_index('date')
        #hist_df_updated.index.name='date'
        hist_df.index.name=today_df_update_time
        #print hist_df.index.name
        #print hist_df
        #print 'update_one_hist:',hist_df_updated
        update_file_name=ROOT_DIR+'/update/%s.csv'% code_sybol
        hist_df.to_csv(update_file_name)
        hist_file_name=ROOT_DIR+'/hist/%s.csv'% code_sybol
        if is_trade_time(get_latest_trade_date()):
            pass
        else:
            hist_df.to_csv(hist_file_name)
    return hist_df
    
def update_all_hist(today_df,today_df_update_time):
    print('Star update history stock data...')
    hist_all_code=get_all_code(ROOT_DIR+'/hist')
    #print 'update_all_hist:',hist_all_code
    all_codes=today_df.index.values.tolist()
    #for code_sybol in hist_all_code:
    latest_trade_date=get_latest_trade_date()
    #all_codes=['000001']
    #hist_all_code=['000001']
    print('update_all_hist,all_codes=', all_codes)
    print('update_all_hist,hist_all_code=', hist_all_code)
    for code_sybol in all_codes:
        
        if code_sybol in hist_all_code:
            updated_df=update_one_hist(code_sybol, today_df,today_df_update_time)
            """
            file_name=ROOT_DIR+'/update/%s.csv'% code_sybol
            hist_file_name=ROOT_DIR+'/hist/%s.csv'% code_sybol
            #updated_df.to_csv(file_name) #,encoding='GB18030')
            if is_trade_time(latest_trade_date):
                pass
            else:
                #updated_df.to_csv(hist_file_name)
                pass
            """
        else:
            #to get hist data update
            print('update_all_hist----else')
            pass
    print('Completed history stock data update!')
    return

#update all hist code from export
def init_all_hist_from_export():
    raw_hist_code=get_all_code(RAW_HIST_DIR)
    hist_code=get_all_code(HIST_DIR)
    except_code_list=list(set(raw_hist_code).difference(set(hist_code)))
    print(except_code_list) 
    print(len(hist_code))
    print(len(raw_hist_code))
    """update all hist data from export"""
    if len(hist_code)==0 or (len(hist_code)!=0 and len(hist_code)!=(len(raw_hist_code))):
        print('Begin pre-processing  the hist data')
        for code_sybol in raw_hist_code:
            get_raw_hist_df(code_sybol)
        print('pre-processing completed')
    else:
        pass
    
    """update all hist data based on the new 'today' data"""
    #update_all_hist(get_today_df())
    
def get_top_list():
    update_file_name=ROOT_DIR+'/result/top_2015-07-08.csv'
    df=ts.top_list('2015-07-08')
    df.to_csv(update_file_name,encoding='GB18030')
    return

def get_timestamp(date_time_str):
    #date_time_str='2015-07-20 13:20:01'
    return time.mktime(time.strptime(date_time_str, ISOTIMEFORMAT))

def get_delta_seconds(start_time, end_time):
    #start_time,end_time: datetime.datetime Object
    delta=end_time-start_time
    get_last_trade_dateta_second=delta.days*24*3600+delta.seconds+delta.microseconds*10**(-6)
    return delta_second

def send_mail(alarm_list):
    # alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
    if alarm_list:
        mailto_list=['104450966@qq.com'] 
        mail_host='smtp.163.com'
        mail_user='zgx20022002@163.com'
        mail_pass='821853Zgx'  
        mail_postfix="qq.com"
        me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
        """
        print 'Setting MIMEText'
        CT=open('content.txt','r')  #read the txt
        content=CT.read().decode('utf-8')
        msg=MIMEText(content.encode('utf8'),_subtype='html')
        CT.close()#close tst
        """
        sub=alarm_list[2]+ ' for '+ alarm_list[0]+' :' +alarm_list[3]
        #date_time='%s'%alarm_list[1]
        content=alarm_list[1] + '\n ' + alarm_list[4]
        msg = MIMEText(content)  
        msg['Subject'] = sub  
        msg['From'] = mail_user 
        msg['To'] = ";".join(mailto_list)
        try:  
            #s = smtplib.SMTP()
            s=smtplib.SMTP_SSL(mail_host,465)
            s.login(mail_user,mail_pass)  
            s.sendmail(mail_user, mailto_list, msg.as_string())  
            s.close()  
        except Exception as e:  
            print(str(e))
    else:
        pass

def get_interval(interval):
    this_time=datetime.datetime.now()
    this_time_str=this_time.strftime('%Y-%m-%d %X')
    latest_trade_day=get_latest_trade_date()
    morning_time0=datetime.datetime.strptime(latest_trade_day+' 09:30:00','%Y-%m-%d %X')
    morning_time1=datetime.datetime.strptime(latest_trade_day+' 11:30:00','%Y-%m-%d %X')
    noon_time0=datetime.datetime.strptime(latest_trade_day+' 13:00:00','%Y-%m-%d %X')
    noon_time1=datetime.datetime.strptime(latest_trade_day+' 15:00:00','%Y-%m-%d %X')
    next_morning_time0=morning_time0+datetime.timedelta(days=1)
    #print 'now_time=',this_time
    #this_time=datetime.datetime(2015,7,21,13,25,20,0)
    #print my_df
    if this_time>morning_time1 and this_time<noon_time0 :
        interval_time=noon_time0-this_time
        interval=interval_time.days*24*3600+interval_time.seconds
        print('Have a lest druing the noon, sleep %s seconds...'%interval)
    else:
        if this_time<=morning_time0:
            interval_time=morning_time0-this_time
            interval=interval_time.days*24*3600+interval_time.seconds
            print('Market does not start yet in the morning, sleep %s seconds...'%interval)
        else:
            if this_time>=noon_time1:
                interval_time=next_morning_time0-this_time
                interval=interval_time.days*24*3600+interval_time.seconds
                market_analyze_today()
                #market_analyze_today()
                write_hist_index()
                print('Market will start in next morning, sleep %s seconds...'%interval)
            else:
                if (this_time>=morning_time0 and this_time<=morning_time1)  or (this_time>=noon_time0 and this_time<=noon_time1):
                    interval=interval
"""
def filter_df_by_date(raw_df,from_date_str,to_date_str):  #index of df should be date:
    #from_date_str: '2015-05-16'
    if from_date_str>to_date_str:
        temp_date_str=from_date_str
        from_date_str=to_date_str
        to_date_str=temp_date_str
    else:
        pass
    #self.h_df.set_index('date')
   
    date_index=raw_df.index.values.tolist()
    #print date_index

    df=raw_df[from_date_str:to_date_str]
    return df
"""
def filter_df_by_date(raw_df,from_date_str,to_date_str):  #index of df should not be date:
    #from_date_str: '2015-05-16'
    if from_date_str>to_date_str:
        temp_date_str=from_date_str
        from_date_str=to_date_str
        to_date_str=temp_date_str
    else:
        pass
    #self.h_df.set_index('date')
    """
    date_index=raw_df.index.values.tolist()
    #print date_index
    if date_index[0]>from_date_str:
        from_date_str=date_index[0]
    else:
        pass
    if date_index[-1]<to_date_str:
        to_date_str=date_index[-1]
    else:
        pass
    """
    crit1=raw_df.date>=from_date_str 
    crit2=raw_df.date<=to_date_str
    df=raw_df[crit1 & crit2]
    return df
def market_analyze_today():
    #init_all_hist_from_export()
    latest_trade_day=get_latest_trade_date()
    today_df,df_time_stamp=get_today_df()
    out_file_name=ROOT_DIR+'/result/result-' + latest_trade_day + '.txt'
    output=open(out_file_name,'w')
    sys.stdout=output
    market=Market(today_df)
    #update_all_hist(today_df,df_time_stamp)
    #actual_101_list,success_101_rate=market.get_101()
    market.get_hist_cross_analyze()
    market.get_realtime_cross_analyze()
    actual_101_list,success_101_rate=market.get_101('realtime')
    t_df=market.today_df
    df_101=t_df[t_df.index.isin(actual_101_list)]
    #print 'df_101=',df_101
    star_rate=0.25
    star_df=market.get_star_df(star_rate)
    #print star_df
    star_list=star_df.index.values.tolist()
    code_10,rate=market.get_10('history', star_list)
    #print code_10
    t_df=market.today_df
    df_10=t_df[t_df.index.isin(code_10)]
    #print df_10
    filename=ROOT_DIR+'/data/is10-%s.csv' % latest_trade_day
    df_10.to_csv(filename)
    #code_10= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
    #print 'potential_101_list=',potential_101_list
    realtime_101_list,success_101_rate=market.get_101('realtime',code_10)
    sys.stdout=sys.__stdout__
    output.close()
    print('market_analyze completed for today.')
    
class Stockhistory:
    def __init__(self,code_str,ktype):
        self.code=code_str
        self.ktype=ktype
        self.DEBUG_ENABLED=False
        self.h_df=ps.get_raw_hist_df(code_str)             #the history data frame data set
        self.alarm_trigger_timestamp=0
        self.max_price=-1
        self.min_price=1000
        self.alarm_category='normal'
        self.realtime_stamp=0
        self.temp_hist_df=self._form_temp_df()
        #self.average_high=0
        #self.average_low=0
        #print self.h_df
    
    def set_hist_df_by_date(self,from_date_str, to_date_str,raw_df=None):  #from_date_str: '2015-05-16'
        h_df=self.h_df#.set_index('date')
        if raw_df!=None:
            h_df=raw_df
        self.h_df=filter_df_by_date(h_df,from_date_str,to_date_str)
        
    def set_hist_df_by_count(self,count):
        if self.h_df.empty:
            pass
        else:
            valid_count=min(count,len(self.h_df))
            self.h_df=self.h_df.tail(valid_count)
                
    def set_max_price(self,max_price):
        self.max_price=max_price
        
    def set_min_price(self,min_price):
        self.min_price=min_price        
        
    def set_alarm_category(self,alarm_category):
        self.alarm_category=alarm_category
        
    def is_new_stock(self):
        return len(self.h_df)<2
    
    def is_second_new_stock(self):
        return len(self.h_df)>=20 and len(self.h_df)<100
    
    def is_stop_trade(self):
        is_stopping=False
        if self.h_df.empty:
            is_stopping=True
        else:
            last_trade_date=get_latest_trade_date()
            last_df_date=self.h_df.tail(1).iloc[0].date
            #print(last_trade_date,last_df_date)
            is_stopping=last_df_date<last_trade_date
            #print(is_stopping)
        return is_stopping
            
    #to set debug mode
    def set_debug_mode(self,debug):
        self.DEBUG_ENABLED=debug
        
    #get df of the latest <num>
    def set_history_df(self,df):
        self.h_df=df
    
    def get_average_rate(self,days=None,selected_column=None):
        num=60
        if days!=None:
            num=days
        temp_df=self._form_temp_df()
        temp_df=temp_df.tail(num)
        #print temp_df
        column='p_change'
        if selected_column!=None:
            column=selected_column
        average_rate=temp_df[column].mean()
        #average_high=high_df['p_change'].mean()
        return average_rate
    
    def get_average_high(self,days=None):
        num=60
        if days!=None:
            num=days
        high_df,filter_rate=self.filter_hist('gte', 0, num)
        #print high_df
        average_high=high_df['h_change'].mean()
        average_close=high_df['p_change'].mean()
        #print average_high,average_close
        average_high=round((average_high+average_close)*0.5,2)
        return average_high
    
    def get_average_low(self,days=None):
        num=60
        if days!=None:
            num=days
        low_df,filter_rate=self.filter_hist('lt', 0, num)
        #print low_df
        average_low=low_df['l_change'].mean()
        average_close=low_df['p_change'].mean()
        #print average_low,average_close
        average_low=round((average_low+average_close)*0.5,2)
        return average_low
    
    #form temp df with 'last_close' for calculating p_change    
    def _form_temp_df(self):
        
        if self.h_df.empty:
            return self.h_df
        df=self.h_df
        close_c=df['close']
        idx=close_c.index.values.tolist()
        va=df['close'].values.tolist()
        idx1=idx[1:]
        first_idx=idx.pop(0)
        va1=va[:-1]
        last_close=Series(va1,index=idx1)
        temp_df=df[1:]
        temp_df.insert(4, 'last_close', last_close)
        #temp_df.insert(7, 'p_change', 100.00*(temp_df.close-temp_df.last_close)/temp_df.last_close)
        temp_df.insert(6, 'p_change', 100.00*((temp_df.close-temp_df.last_close)/temp_df.last_close).round(4))
        
        temp_df.is_copy=False
        temp_df['ma5'] = np.round(pd.rolling_mean(temp_df['close'], window=5), 2)
        temp_df['ma10'] = np.round(pd.rolling_mean(temp_df['close'], window=10), 2)
        temp_df['ma20'] = np.round(pd.rolling_mean(temp_df['close'], window=20), 2)
        temp_df['ma30'] = np.round(pd.rolling_mean(temp_df['close'], window=30), 2)
        temp_df['ma60'] = np.round(pd.rolling_mean(temp_df['close'], window=60), 2)
        temp_df['ma120'] = np.round(pd.rolling_mean(temp_df['close'], window=120), 2)
        temp_df['v_ma5'] = np.round(pd.rolling_mean(temp_df['volume'], window=5), 2)
        temp_df['v_ma10'] = np.round(pd.rolling_mean(temp_df['volume'], window=10), 2)
        temp_df.insert(14, 'h_change', 100.00*((temp_df.high-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(15, 'l_change', 100.00*((temp_df.low-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(16, 'o_change', 100.00*((temp_df.open-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df['atr']=np.where(temp_df['high']-temp_df['low']<temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['low']) #temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['atr']<temp_df['close'].shift(1)-temp_df['low'],temp_df['close'].shift(1)-temp_df['low'],temp_df['atr'])
        short_num=5
        long_num=10
        temp_df['atr_ma%s'%short_num] = np.round(pd.rolling_mean(temp_df['atr'], window=short_num), 2)
        temp_df['atr_%s_rate'%short_num]=(temp_df['atr_ma%s'%short_num]/temp_df['atr']).round(2)
        temp_df['atr_%s_max_r'%short_num]=np.round(pd.rolling_max(temp_df['atr_%s_rate'%short_num], window=short_num), 2)
        temp_df['atr_ma%s'%long_num] = np.round(pd.rolling_mean(temp_df['atr'], window=long_num), 2)
        temp_df['atr_%s_rate'%long_num]=(temp_df['atr_ma%s'%long_num]/temp_df['atr']).round(2)
        temp_df['atr_%s_max_r'%long_num]=np.round(pd.rolling_max(temp_df['atr_%s_rate'%long_num], window=long_num), 2)
        expect_rate=1.8
        temp_df['rate_%s'%expect_rate]=(expect_rate*temp_df['atr']/temp_df['atr']).round(2)
        #temp_df['atr_in']=np.where((temp_df['atr_%s_rate'%short_num]==temp_df['atr_%s_max_r'%short_num]) & (temp_df['atr_%s_max_r'%short_num]>=temp_df['rate_%s'%expect_rate]),(0.5*(temp_df['atr_%s_rate'%short_num]+temp_df['atr_%s_rate'%long_num])).round(2),0)
        temp_df['atr_in']=np.where((temp_df['atr_%s_rate'%short_num]==temp_df['atr_%s_max_r'%short_num]),(0.5*(temp_df['atr_%s_rate'%short_num]+temp_df['atr_%s_rate'%long_num])).round(2),0)
        #temp_df.to_csv(ROOT_DIR+'/result_temp/temp_%s.csv' % self.code)
        return temp_df
    
    def _form_temp_df1(self):
        #print(self.h_df)
        if len(self.h_df) <30:
            return 0,'',0,'' 
        df=self.h_df
        if len(self.h_df)>1000:
            df=df.tail(1000)
        close_c=df['close']
        idx=close_c.index.values.tolist()
        va=df['close'].values.tolist()
        idx1=idx[1:]
        first_idx=idx.pop(0)
        va1=va[:-1]
        last_close=Series(va1,index=idx1)
        temp_df=df[1:]
        temp_df.insert(4, 'last_close', last_close)
        #temp_df.insert(7, 'p_change', 100.00*(temp_df.close-temp_df.last_close)/temp_df.last_close)
        temp_df.insert(6, 'p_change', 100.00*((temp_df.close-temp_df.last_close)/temp_df.last_close).round(4))
        
        temp_df.is_copy=False
        temp_df['ma5'] = np.round(pd.rolling_mean(temp_df['close'], window=5), 2)
        temp_df['ma10'] = np.round(pd.rolling_mean(temp_df['close'], window=10), 2)
        temp_df['ma20'] = np.round(pd.rolling_mean(temp_df['close'], window=20), 2)
        temp_df['ma30'] = np.round(pd.rolling_mean(temp_df['close'], window=30), 2)
        temp_df['ma60'] = np.round(pd.rolling_mean(temp_df['close'], window=60), 2)
        temp_df['ma120'] = np.round(pd.rolling_mean(temp_df['close'], window=120), 2)
        temp_df['v_ma5'] = np.round(pd.rolling_mean(temp_df['volume'], window=5), 2)
        temp_df['v_ma10'] = np.round(pd.rolling_mean(temp_df['volume'], window=10), 2)
        temp_df.insert(14, 'h_change', 100.00*((temp_df.high-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(15, 'l_change', 100.00*((temp_df.low-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df['atr']=np.where(temp_df['high']-temp_df['low']<temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['low']) #temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['atr']<temp_df['close'].shift(1)-temp_df['low'],temp_df['close'].shift(1)-temp_df['low'],temp_df['atr'])
        short_num=5
        long_num=10
        temp_df['atr_ma%s'%short_num] = np.round(pd.rolling_mean(temp_df['atr'], window=short_num), 2)
        temp_df['atr_%s_rate'%short_num]=(temp_df['atr_ma%s'%short_num]/temp_df['atr']).round(2)
        temp_df['atr_%s_max_r'%short_num]=np.round(pd.rolling_max(temp_df['atr_%s_rate'%short_num], window=short_num), 2)
        temp_df['atr_ma%s'%long_num] = np.round(pd.rolling_mean(temp_df['atr'], window=long_num), 2)
        temp_df['atr_%s_rate'%long_num]=(temp_df['atr_ma%s'%long_num]/temp_df['atr']).round(2)
        temp_df['atr_%s_max_r'%long_num]=np.round(pd.rolling_max(temp_df['atr_%s_rate'%long_num], window=long_num), 2)
        expect_rate=1.8
        temp_df['rate_%s'%expect_rate]=(expect_rate*temp_df['atr']/temp_df['atr']).round(2)
        temp_df['atr_in']=np.where((temp_df['atr_%s_rate'%short_num]==temp_df['atr_%s_max_r'%short_num]) & (temp_df['atr_%s_max_r'%short_num]>=temp_df['rate_%s'%expect_rate]),(0.5*(temp_df['atr_%s_rate'%short_num]+temp_df['atr_%s_rate'%long_num])).round(2),0)
        temp_df.to_csv(ROOT_DIR+'/result_temp1/temp_%s.csv' % self.code,encoding='utf-8')
        atr_in_rate=round(temp_df.tail(1)['atr_in'].mean(),2)
        last_date=temp_df.tail(1).iloc[0].date
        #print type(last_date)
        last2_df=temp_df.tail(2)
        atr_in_rate_last=round(last2_df.head(1)['atr_in'].mean(),2)
        last2_date=last2_df.head(1).iloc[0].date
        #print 'atr_in_rate=',atr_in_rate
        return atr_in_rate,last_date,atr_in_rate_last,last2_date
    
    def _form_temp_df0(self):
        df=self.h_df
        close_c=df['close']
        idx=close_c.index.values.tolist()
        va=df['close'].values.tolist()
        idx1=idx[1:]
        first_idx=idx.pop(0)
        va1=va[:-1]
        last_close=Series(va1,index=idx1)
        temp_df=df[1:]
        temp_df.insert(4, 'last_close', last_close)
        #temp_df.insert(7, 'p_change', 100.00*(temp_df.close-temp_df.last_close)/temp_df.last_close)
        temp_df.insert(6, 'p_change', 100.00*((temp_df.close-temp_df.last_close)/temp_df.last_close).round(4))
        #temp_df.insert(7, '_change', 100.00*(temp_df.high-temp_df.last_close)/temp_df.last_close)
        """Insert MA data here """
        close_list=temp_df['close'].values.tolist()
        ma5_list=get_ma_list(close_list, 5)
        ma10_list=get_ma_list(close_list, 10)
        ma20_list=get_ma_list(close_list, 20)
        ma30_list=get_ma_list(close_list, 30)
        ma60_list=get_ma_list(close_list, 60)
        ma120_list=get_ma_list(close_list, 120)
        s_ma5=pd.Series(ma5_list,index=temp_df.index)
        s_ma10=pd.Series(ma10_list,index=temp_df.index)
        s_ma20=pd.Series(ma20_list,index=temp_df.index)
        s_ma30=pd.Series(ma30_list,index=temp_df.index)
        s_ma60=pd.Series(ma60_list,index=temp_df.index)
        s_ma120=pd.Series(ma120_list,index=temp_df.index)
        temp_df.insert(8,'ma5',s_ma5)
        temp_df.insert(9,'ma10',s_ma10)
        temp_df.insert(10,'ma20',s_ma20)
        temp_df.insert(11,'ma30',s_ma30)
        temp_df.insert(12,'ma60',s_ma60)
        temp_df.insert(13,'ma120',s_ma120)
        temp_df.insert(14, 'h_change', 100.00*((temp_df.high-temp_df.last_close)/temp_df.last_close).round(4))
        temp_df.insert(15, 'l_change', 100.00*((temp_df.low-temp_df.last_close)/temp_df.last_close).round(4))
        return temp_df
    
    def change_static(self,rate_list,column):
        temp_df=self._form_temp_df()
        N=len(temp_df)
        if N<50:
            return pd.DataFrame({})
        else:
            #Do not consider special first 30 days for each stock 
            temp_df=temp_df[30:]
        gt_column=['code']
        #gt_column=['code']
        gt_data={}
        gt_data['code']=self.code
        for rate in rate_list:
            df=temp_df[temp_df[column]>rate]
            gt_rate_num=len(df)
            gt_rate=round(float(gt_rate_num)/N,2)
            column_name='gt_%s' % rate
            gt_data[column_name]=gt_rate
            gt_column.append(column_name)
        gt_static_df=pd.DataFrame(gt_data,columns=gt_column,index=['0'])
        #print 'static for %s:' % column
        #print gt_static_df 
        return gt_static_df
    
    def get_open_static(self,high_open_rate):
        trade_rate=0.2
        criteria_high_open=self.h_df['open']>self.h_df['close'].shift(1)*(1+high_open_rate*0.01)
        high_open_df=self.h_df[criteria_high_open]
        if len(high_open_df)>0:
            hopen_hclose_df=high_open_df[high_open_df['close']>high_open_df['open']*(1+(trade_rate)*0.01)]
            hopen_hclose_rate=round(round(len(hopen_hclose_df),2)/len(high_open_df),2)
            print('hopen_hclose_rate_%s=%s' % (high_open_rate,hopen_hclose_rate))
            
            criteria_high_next=self.h_df['high'].shift(-1)>self.h_df['open'].shift(1)*(1+(trade_rate+high_open_rate)*0.01)
            hopen_next_high_df=self.h_df[criteria_high_open & criteria_high_next]
            print(len(hopen_next_high_df))
            hopen_hnext_rate=round(round(len(hopen_next_high_df),2)/len(high_open_df),2)
            print('hopen_hnext_rate_%s=%s' % (high_open_rate,hopen_hnext_rate))
        
        low_open_df=self.h_df[self.h_df['open']<self.h_df['close'].shift(1)*(1-high_open_rate*0.01)]
        if len(low_open_df):
            lopen_lclose_df=low_open_df[low_open_df['close']<low_open_df['open']*(1+trade_rate*0.01)]
            lopen_lclose_rate=round(round(len(lopen_lclose_df),2)/len(low_open_df),2)
            print('lopen_lclose_rate_n%s=%s' %(high_open_rate,lopen_lclose_rate))
        return
    
    def is_drop_then_up(self,temp_df,great_dropdown=-4.0,turnover_rate=0.75,turnover_num=None):
        #turnover_num=2, mean 2 days inscrease over turnover_rate
        #temp_df=self._form_temp_df()
        is_drop_up=False
        actual_turnover_rate=0
        if temp_df.empty or (self.is_stop_trade() and not temp_df.empty):
            pass
        else:
            if turnover_num and turnover_num<len(temp_df)-1:
                temp_df=temp_df.tail(turnover_num+1)
                drop_rate=temp_df.iloc[0].p_change
                temp_df_1=temp_df.tail(turnover_num)
                total_incrs_after_drop=temp_df_1['p_change'].sum()
                is_drop_up=total_incrs_after_drop>=turnover_rate*abs(drop_rate) and drop_rate<great_dropdown
                if is_drop_up:
                    actual_turnover_rate=round(total_incrs_after_drop/abs(drop_rate),4)
            elif not turnover_num and len(temp_df)>=2: #turnover_num=1
                temp_df=temp_df.tail(2)
                drop_rate=temp_df.iloc[0].p_change
                incrs_after_drop=temp_df.iloc[1].p_change
                is_drop_up=incrs_after_drop>=turnover_rate*abs(drop_rate) and drop_rate<great_dropdown
                if is_drop_up:
                    actual_turnover_rate=round(incrs_after_drop/abs(drop_rate),4)
            else:
                pass
        return is_drop_up,actual_turnover_rate
    
    def is_extreme_recent(self,temp_df,recent_count=None,continue_extreme_count=None):
        #temp_df=self._form_temp_df()
        continue_extreme_num=0
        is_continue_extreme=False
        if temp_df.empty or (self.is_stop_trade() and not temp_df.empty):
            return is_continue_extreme,continue_extreme_num
        extreme_num=1
        extreme_rate=0.1
        recent_num=20
        if recent_count:
            recent_num=recent_count
        recent_df=temp_df.tail(min(len(temp_df),100))
        last_index=recent_df.index.values.tolist()[-1]
        if continue_extreme_count:
            extreme_num=continue_extreme_count
        extreme_df=recent_df[recent_df.volume<recent_df.v_ma10*extreme_rate]
        if extreme_df.empty:
            return is_continue_extreme,continue_extreme_num
        else:
            last_extreme_index=extreme_df.index.values.tolist()[-1]
            last_extreme_rate=extreme_df.tail(1).iloc[0].p_change
            is_extreme=(last_index-last_extreme_index)<recent_num
            if (last_index-last_extreme_index)<recent_num:
                continue_extreme_num=self.get_continue_index_num(extreme_df)
                if continue_extreme_num==0:
                    continue_extreme_num=1
                else:
                    pass
            continue_extreme_num=continue_extreme_num*int(last_extreme_rate/abs(last_extreme_rate))
            is_continue_extreme=continue_extreme_num>=extreme_num
            #print(self.code,continue_extreme_num)
        return is_continue_extreme,continue_extreme_num
    
    def get_recent_over_ma(self,temp_df,ma_type='ma5',ma_offset=0.002,recent_count=None):
        #temp_df=self._form_temp_df()
        count=len(temp_df)
        if temp_df.empty or (self.is_stop_trade() and not temp_df.empty):
            return 0.0,0,'1979-01-01'
        else:
            if recent_count:
                count=min(len(temp_df),recent_count)
            else:
                pass
        temp_df=temp_df.tail(count)
        date_last=temp_df.tail(1).iloc[0].date
        temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
        df_over_ma=temp_df[(temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1)]
        over_ma_rate=round(round(len(df_over_ma),4)/len(temp_df),4)
        #print('over_ma_rate=',over_ma_rate)
        continue_over_ma_num=0
        index_i=len(df_over_ma)-1
        index_list=df_over_ma.index.values.tolist()
        if df_over_ma.empty:
            return over_ma_rate,continue_over_ma_num,'1979-01-01'
        date_last_over_ma=df_over_ma.tail(1).iloc[0].date
        #print(date_last,date_last_over_ma)
        if date_last_over_ma==date_last:
            continue_over_ma_num=self.get_continue_index_num(df_over_ma)
        #print('continue_over_ma=',continue_over_ma_num)
        return over_ma_rate,continue_over_ma_num,date_last
    
    def get_continue_index_num(self,df):
        continue_num=0
        if df.empty:
            return continue_num
        index_i=len(df)-1
        index_list=df.index.values.tolist()
        while index_i>0:
            if index_list[index_i]-index_list[index_i-1]==1:
                continue_num+=1
            else:
                break
            index_i=index_i-1
        if continue_num>0:
            continue_num+=1
        return continue_num
    
    def get_trade_df(self,ma_type='ma5',ma_offset=0.002,great_score=4,great_change=5.0):
        #based on MA5
        #scoring based on recent three day's close: -5 to 5
        temp_df=self._form_temp_df()
        if len(temp_df)==0:
            return {}
        ma_offset=0.002
        temp_df['pv_rate']=(temp_df['p_change']/100.0/(temp_df['volume']-temp_df['volume'].shift(1))*temp_df['volume'].shift(1)).round(2)
        temp_df['v_rate']=(temp_df['volume']/temp_df['v_ma5'].shift(1)).round(2)
        temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
        temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])<-ma_offset*temp_df['close'].shift(1),-1,temp_df['c_o_ma']) #-1 for bellow ma
        #print temp_df
        WINDOW=3
        temp_df['sum_o_ma'] = np.round(pd.rolling_sum(temp_df['c_o_ma'], window=WINDOW), 2)
        temp_df['trend_o_ma']=temp_df['sum_o_ma']-temp_df['sum_o_ma'].shift(1)
     
        temp_df['g-chg']=np.where(temp_df['p_change']>great_change,1,0)
        temp_df['g-chg']=np.where(temp_df['p_change']<-great_change,-1,temp_df['g-chg'])
        
        temp_df['score']=temp_df['sum_o_ma']+temp_df['trend_o_ma'] #+temp_df['g-chg']
        
        temp_df['max'] = np.round(pd.rolling_max(temp_df['score'], window=WINDOW), 2)
        temp_df['min'] = np.round(pd.rolling_min(temp_df['score'], window=WINDOW), 2)
        
        temp_df['operate']=np.where(temp_df['score']>=temp_df['min']+great_score,1,0)              #1 to buy, 0 to keep unchanged
        temp_df['operate']=np.where(temp_df['max']>=temp_df['score']+great_score,-1,temp_df['operate'])       #-1 to sell

        #count_sell= temp_df['operate'].value_counts()
        #print count_sell
        
        recent_sum=temp_df.tail(WINDOW)['operate'].sum()
        #print 'recent_sum=', recent_sum
        
        #"""
        non_zero_df=temp_df[temp_df['operate']!=0]
        if non_zero_df.empty:
            return {}
        this_stratege_state= non_zero_df.tail(1).iloc[0].operate
        this_stratege_date= non_zero_df.tail(1).iloc[0].date
        #print this_stratege_date,this_stratege_state
        this_state= temp_df.tail(1).iloc[0].operate
        this_date= temp_df.tail(1).iloc[0].date
        this_score=temp_df.tail(1).iloc[0].score
        #print this_date,this_state
        
        last_stratege_df=non_zero_df[non_zero_df['operate']!=this_stratege_state]#.tail(1)
        last_stratege_date=last_stratege_df.tail(1).iloc[0].date
        #print last_stratege_date
        #temp_df['market']=np.log(temp_df['close']/temp_df['close'].shift(1))
        #temp_df['strategy']=temp_df['regime'].shift(1)*temp_df['market']
        result_data={'code':self.code,
                     'l_s_date':last_stratege_date,
                     'l_s_state':this_stratege_state*(-1),
                     't_s_date':this_stratege_date,
                     't_s_state':this_stratege_state,
                     't_date':this_date,
                     't_state':this_state,
                     'score':this_score,
                     'oper3':recent_sum
                     }
        #result_list=[self.code,last_stratege_date,this_stratege_state*(-1),this_stratege_date,this_stratege_state,this_date,this_state,this_score,recent_sum]
        #print result_list
        #"""
        temp_df.to_csv(ROOT_DIR+'/trade_temp/%s.csv'%self.code)
        #print 'temp_df=',temp_df
        return result_data
    
    def get_trade_df0(self,ma_type='ma5',ma_offset=0.01,great_score=4,great_change=5.0):
        #based on MA5
        #scoring based on recent three day's close: -5 to 5
        temp_df=self._form_temp_df()
        temp_df['c_o_ma']=temp_df['close']-temp_df[ma_type]
        ma_offset=0.01
        temp_df['regime']=np.where(temp_df['c_o_ma']>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
        temp_df['regime']=np.where(temp_df['c_o_ma']<-ma_offset*temp_df['close'].shift(1),-1,temp_df['regime']) #-1 for bellow ma
        #print temp_df
        WINDOW=3
        temp_df['gt_ma'] = np.round(pd.rolling_sum(temp_df['regime'], window=WINDOW), 2)
        temp_df['gt-ma5-incrs']=temp_df['gt_ma']-temp_df['gt_ma'].shift(1)
     
        
        temp_df['g-chg']=np.where(temp_df['p_change']>great_change,1,0)
        temp_df['g-chg']=np.where(temp_df['p_change']<-great_change,-1,temp_df['g-chg'])
        
        temp_df['score']=temp_df['gt_ma']+temp_df['gt-ma5-incrs'] #+temp_df['g-chg']
        
        temp_df['max'] = np.round(pd.rolling_max(temp_df['score'], window=WINDOW), 2)
        temp_df['min'] = np.round(pd.rolling_min(temp_df['score'], window=WINDOW), 2)
        
        temp_df['sell']=np.where(temp_df['score']>=temp_df['min']+great_score,1,0)              #1 to buy, 0 to keep unchanged
        temp_df['sell']=np.where(temp_df['max']>=temp_df['score']+great_score,-1,temp_df['sell'])       #-1 to sell

        #count_sell= temp_df['sell'].value_counts()
        #print count_sell
        
        recent_sum=temp_df.tail(WINDOW)['sell'].sum()
        #print 'recent_sum=', recent_sum
        
        #"""
        non_zero_df=temp_df[temp_df['sell']!=0]
        this_stratege_state= non_zero_df.tail(1).iloc[0].sell
        this_stratege_date= non_zero_df.tail(1).iloc[0].date
        #print this_stratege_date,this_stratege_state
        this_state= temp_df.tail(1).iloc[0].sell
        this_date= temp_df.tail(1).iloc[0].date
        #print this_date,this_state
        
        last_stratege_df=non_zero_df[non_zero_df['sell']!=this_stratege_state]#.tail(1)
        last_stratege_date=last_stratege_df.tail(1).iloc[0].date
        #print last_stratege_date
        #temp_df['market']=np.log(temp_df['close']/temp_df['close'].shift(1))
        #temp_df['strategy']=temp_df['regime'].shift(1)*temp_df['market']
        result_list=[self.code,last_stratege_date,this_stratege_state*(-1),this_stratege_date,this_stratege_state,this_date,this_state,recent_sum]
        #print result_list
        #"""
        temp_df.to_csv(ROOT_DIR+'/trade_temp/%s.csv'%self.code)
        return recent_sum
    
    def ma_analyze(self):
        df=self._form_temp_df()
        #print df
        analyze_types=['close','ma5','ma10','ma30','ma60','ma120']
        for analyze_type in analyze_types:
            analyze_list=df[analyze_type].values.tolist()
            boduan_list=find_boduan(analyze_list)
            print('%s_boduan_list=%s' % (analyze_type,boduan_list[-20:]))
            if len(boduan_list)>=3:
                last_value0=boduan_list[-1]
                last_value1=boduan_list[-2]
                last_value2=boduan_list[-3]
                if last_value0>last_value1:
                    print('The trade of %s is INREASING from %s to %s' % (analyze_type,last_value1,last_value0))
                    print('The upholding is %s , and the press is %s' % (last_value1,last_value2))
                else:
                    print('The trade of %s is DECREASING from %s to %s' % (analyze_type,last_value1,last_value0))
                    print('The upholding is %s , and the press is %s' % (last_value2,last_value1))
            else:
                pass
        return
    
    def hist_analyze(self,num):
        df=self._form_temp_df()
        rate=0.8
        df = df.tail(num)
        mean_c=(df['p_change'].mean()).round(2)
        mean_h=(df['h_change'].mean()).round(2)
        mean_l=(df['l_change'].mean()).round(2)
        mean_h_df=df[df.h_change>mean_h]
        mean_h_2=(mean_h_df['h_change'].mean()).round(2)
        #print 'mean_h_2=',mean_h_2
        current_price=self.get_mean('close', 1)
        #print 'current_price=',current_price
        ma5=self.get_predict_ma('close', 5,mean_c)
        ma10=self.get_predict_ma('close', 10,mean_c)
        
        h_sell_1=round(current_price*(1+mean_h/100),2)
        h_sell_2=round(current_price*(1+mean_h_2/100),2)
        #print 'h_sell_1=',mean_h
        #print 'h_sell_2=',mean_h_2
        buy_in=round(current_price*(1+mean_l/100),2)
        l_sell_1=min(ma5,ma10,buy_in)
        mean_l_df=df[df.l_change<mean_l]
        mean_l_2=(mean_l_df['l_change'].mean()).round(2)
        l_sell_2=round(current_price*(1+mean_l_2/100),2)
        l_sell_2=min(ma5,ma10,l_sell_2)
        
        print('buy_in gt ma5: ', buy_in>=ma5)
        print('buy_in gt ma10: ', buy_in>=ma10)
        worth_buy_in=buy_in>=ma5 and buy_in>=ma10
        
        price_data={'cur_prc':[current_price],'p_ma5':ma5,'p_ma10':ma10,'h_sell1':h_sell_1,'h_sell2':h_sell_2,'l_sell1':l_sell_1,'l_sell2':l_sell_2,'buy_in':buy_in,'worth_in':worth_buy_in}
        price_column=['cur_prc','p_ma5','p_ma10','h_sell1','h_sell2','l_sell1','l_sell2','buy_in','worth_in']
        
        price_df=pd.DataFrame(price_data,columns=price_column)
        #print price_df
    
        #print 'mean_c=',mean_c
        mean_c_df=df[df.h_change>=mean_c]
        h_gt_meanc_rate=round(round(len(mean_c_df),2)/num,2)
        #print 'h_change_gt_mc_%s_n=%s'%(mean_c,h_gt_meanc_rate)
    
        h_gt_meanh_rate=round(round(len(mean_h_df),2)/num,2)
        c_lt_meanh_rate=round(round(len(df[df.p_change<mean_h]),2)/num,2)
        #print 'h_change_gt_mh_%s_n=%s' % (mean_h,h_gt_meanh_rate)
        #print 'p_change_lt_mh_%s_n=%s' % (mean_h,c_lt_meanh_rate)
  
        
        l_lt_meanl_rate=round(round(len(mean_l_df),2)/num,2)
        c_gt_meanl_rate=round(round(len(df[df.p_change>=mean_l]),2)/num,2)
   
        #print 'l_change_lt_ml_%s_n=%s' % (mean_l,l_lt_meanl_rate)
        #print 'p_change_gt_ml_%s_n=%s' % (mean_l,c_gt_meanl_rate)
    
        data={'mc':[mean_c],'mh1':mean_h,'mh2':mean_h_2,'ml1':mean_l,'ml2':mean_l_2,'h_gt_mc':h_gt_meanc_rate,'h_gt_mh':h_gt_meanh_rate,'c_lt_mh':c_lt_meanh_rate,'l_lt_ml':l_lt_meanl_rate,'c_gt_ml':c_gt_meanl_rate}
        column_list=['mc','mh1','mh2','ml1','ml2','h_gt_mc','h_gt_mh','c_lt_mh','l_lt_ml','c_gt_ml']
        """<price>_gt_mean<high>:highprice_gt_meanhigh as  h_gt_mh"""
        hist_df=pd.DataFrame(data,columns=column_list) #,index=['2015-05-15'])
        #print hist_df
    
        
    #get topest df for history data
    def get_hist_topest(self,recent_days=None):
        if recent_days!=None and recent_days<len(self.h_df):
            df=self.h_df.tail(recent_days)
            self.set_history_df(df)
        temp_df=self._form_temp_df()
        #print temp_df
        topest_df=temp_df[temp_df.close==(temp_df.last_close*1.1).round(2)]   #filter the topest items
        topest_rate=round(round(len(topest_df),3)/len(temp_df),3)
        return topest_df,topest_rate
    
    def filter_hist(self,operator,threshhold_rate,recent_days=None):
        temp_df=self._form_temp_df()
        if recent_days!=None and recent_days<len(temp_df):
            temp_df=temp_df.tail(recent_days)
        #print temp_df
        criteria=True
        if operator=='gte':
            #criteria=temp_df.close>=temp_df.last_close*threshhold_rate/100
            criteria=temp_df.p_change>=threshhold_rate
        else:
            if operator=='lt':
                #criteria=temp_df.close<temp_df.last_close*threshhold_rate/100
                criteria=temp_df.p_change<threshhold_rate
            else:
                pass
        filter_df=temp_df[criteria]
        filter_rate=round(round(len(filter_df),3)/len(temp_df),3)
        return filter_df,filter_rate
    #get max data of <latest_num> days
    def get_max(self,column_name='close',latest_num=None):
        df=self.h_df
        if latest_num !=None and len(df)>=latest_num:
            #df = df.head(latest_num)
            df = df.tail(latest_num)
            #print 'The latest df:',df
        max_idx=df[column_name].idxmax()
        max_value=df[column_name].max()
        max_value=round(max_value,2)
        max_series=df.ix[max_idx]
        #print type(max_series)
        #max_value=max_series['volume']         #for other related values
        #print 'max_series',max_series[column_name]
        #print 'max_series',max_series.values
        return max_series,max_value
    
    #get min data of <latest_num> days
    def get_min(self,column_name='close',latest_num=None):
        df=self.h_df
        if latest_num !=None and len(df)>=latest_num:
            #df = df.head(latest_num)
            df = df.tail(latest_num)
        min_idx=df[column_name].idxmin()
        min_value=df[column_name].min()
        min_value=round(min_value,2)
        min_series=df.ix[min_idx]
        return min_series,min_value
    
    #get min data of <latest_num> days
    def get_mean(self,column_name,latest_num):
        df=self.h_df
        #print 'mean df:',df
        #print latest_num
        #if latest_num !=None  and len(df)>=latest_num:
        df = df.tail(latest_num)
        mean_value=df[column_name].mean()
        mean_value=round(mean_value,2)
        return mean_value
    
    def get_ma(self,column,ma_num):
        mean_value=self.get_mean(column, ma_num)
        return mean_value
    
    def get_predict_ma(self,column,ma_num,mean_inrcs):
        df=self.h_df
        ma_num=min(len(df),ma_num)  #to prevent 'index exceed
        df = df.tail(ma_num)
        mean_value=df[column].mean()
        value_list=df[column].values.tolist()
        value_0=value_list[0]#df.ix[0].column
        value_n=value_list[ma_num-1] #df.ix[(ma_num-1)].column
        predict_ma=mean_value+(value_n*(1+mean_inrcs/100)-value_0)/ma_num
        predict_ma=round(predict_ma,2)
        if self.DEBUG_ENABLED: print('predict_ma%s=%s'%(ma_num,predict_ma))
        return predict_ma
    
    def get_realtime_ma(self,column,ma_num,current_price):
        df=self.h_df
        ma_num=min(len(df),ma_num)  #to prevent 'index exceed
        df = df.tail(ma_num)
        mean_value=df[column].mean()
        value_list=df[column].values.tolist()
        value_0=value_list[0]#df.ix[0].column
        value_n=value_list[ma_num-1] #df.ix[(ma_num-1)].column
        predict_ma=mean_value+(current_price-value_0)/ma_num
        predict_ma=round(predict_ma,2)
        if self.DEBUG_ENABLED: print('predict_ma%s=%s'%(ma_num,predict_ma))
        return predict_ma
    
    def get_atr_df(self,short_num, long_num):
        temp_df=self.h_df
        if len(temp_df)==0:
            return temp_df,'','',0.0
        temp_df.is_copy=False  
        #temp_df.fillna(0)
        #temp_df.fillna(method='pad')
        #temp_df=temp_df.fillna(method='bfill')
        
        #temp_df['atr']=max(temp_df['high']-temp_df['low'],temp_df['high']-temp_df['close'].shift(1), temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['high']-temp_df['low']<temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['close'].shift(1),temp_df['high']-temp_df['low']) #temp_df['close'].shift(1)-temp_df['low'])
        temp_df['atr']=np.where(temp_df['atr']<temp_df['close'].shift(1)-temp_df['low'],temp_df['close'].shift(1)-temp_df['low'],temp_df['atr'])
        #temp_df['atr_rate']=(2.00*temp_df['atr']*100/(temp_df['high']+temp_df['low'])).round(0)
        temp_df['atr_rate']=(temp_df['atr']*100/temp_df['close'].shift(1)).round(0)
        temp_df['atr_%s'%short_num] = np.round(pd.rolling_mean(temp_df['atr'], window=short_num), 2)
        temp_df['atr_%s'%long_num] = np.round(pd.rolling_mean(temp_df['atr'], window=long_num), 2)
        
        temp_df['atr_std%s'%short_num] = np.round(pd.rolling_std(temp_df['atr_rate'], window=short_num), 2)
        temp_df['atr_var%s'%short_num] = np.round(pd.rolling_var(temp_df['atr_rate'], window=short_num), 2)
        temp_df['max_%s'%short_num] = np.round(pd.rolling_max(temp_df['high'], window=short_num), 2)
        temp_df['break_up_%s'%short_num]=np.where(temp_df['high']>temp_df['max_%s'%short_num].shift(1),1,0)
        temp_df['min_%s'%short_num] = np.round(pd.rolling_min(temp_df['low'], window=short_num), 2)
        temp_df['subtr_%s'%short_num]=temp_df['max_%s'%short_num]-temp_df['min_%s'%short_num]
        temp_df['break_up_%s'%short_num]=np.where(temp_df['low']<temp_df['min_%s'%short_num].shift(1),-1,temp_df['break_up_%s'%short_num])
        temp_df['max_%s'%long_num] = np.round(pd.rolling_max(temp_df['high'], window=long_num), 2)
        temp_df['break_up_%s'%long_num]=np.where(temp_df['high']>temp_df['max_%s'%long_num].shift(1),1,0)
        temp_df['min_%s'%long_num] = np.round(pd.rolling_min(temp_df['low'], window=long_num), 2)
        temp_df['subtr_%s'%long_num]=temp_df['max_%s'%long_num]-temp_df['min_%s'%long_num]
        temp_df['break_up_%s'%long_num]=np.where(temp_df['low']<temp_df['min_%s'%long_num].shift(1),-1,temp_df['break_up_%s'%long_num])
        temp_df['break_sum_%s'%short_num]=np.round(pd.rolling_sum(temp_df['break_up_%s'%short_num], window=2), 2)
        temp_df['break_sum_%s'%long_num]=np.round(pd.rolling_sum(temp_df['break_up_%s'%long_num], window=2), 2)
        #print temp_df
        crit1=temp_df['break_up_%s'%short_num]==1 
        crit2=temp_df['break_sum_%s'%short_num]==1
        #temp_df=temp_df.fillna(0)
        temp_df=temp_df.fillna(method='bfill')
        #print temp_df
        #temp_df['1st_break'%short_num]=np.where(temp_df['break_sum_%s'%short_num]>temp_df['break_up_%s'%short_num],1,0)
        #temp_df['1st_break'%short_num]=np.where(temp_df['break_sum_%s'%short_num]>1,1,0)
        #crit1=temp_df.break_sum_20==1
        #crit2=temp_df.break_up_20==1
        df_20=temp_df[crit1&crit2]#[temp_df['break_sum_%s'%short_num]==1 and temp_df['break_up_%s'%short_num]==1]
        #print 'df='
        #print len(df)
        #print df_20['date'].values.tolist()
        
        crit1=temp_df['break_up_%s'%long_num]==1 
        crit2=temp_df['break_sum_%s'%long_num]==1
        df_55=temp_df[crit1&crit2]
        latest_break_20=''
        latest_break_55=''
        if df_20['date'].values.tolist(): latest_break_20=df_20['date'].values.tolist()[-1]
        if df_55['date'].values.tolist():latest_break_55=df_55['date'].values.tolist()[-1]
        temp_df.to_csv(ROOT_DIR+'/result_temp/atr_%s.csv' % self.code)
        #print temp_df
        print(temp_df['atr_rate'].value_counts())
        atr_s= (temp_df['atr_rate'].value_counts()/temp_df['atr_rate'].count()).round(2)
        #print 'atr_static:'
        #print atr_s
        value_list=atr_s.values.tolist()
        wave_rate_list=atr_s.index.tolist()
        sum_point=0.00
        value_list_sum=0.00
        for i in range(5):#(len(value_list)):
            sum_point+=value_list[i]*wave_rate_list[i]
            value_list_sum+=value_list[i]
        weight_average_atr=round(sum_point/value_list_sum,2)
        #print 'weight_average_atr=%s%%' % weight_average_atr
        top5_average=sum(atr_s.index.tolist()[:5])/5.00
        #print 'top5_average=%s%%' % top5_average
      
        return temp_df,latest_break_20,latest_break_55,top5_average
    
    def get_macd_df(self,short_num, long_num,dif_num,current_price):
        temp_df=self.h_df
        temp_df.is_copy=False
        short_num=12
        long_num=26
        dif_num=9
        print(temp_df)
        temp_df.index.name=['idx']
        idx_list=temp_df.index.values.tolist()
        idx_df=pd.DataFrame({'idx':idx_list})
        idx_df=idx_df.astype(int)
        print('idx_df')
        #print idx_df
        #print (temp_df['idx'])
        temp_df['idx']=idx_df['idx']
        temp_df['idx'].astype(int)
        print(temp_df.dtypes)
        temp_df['s_ma'] = np.round(pd.rolling_mean(temp_df['close'], window=short_num), 2)
        #temp_df['s_ma_csum']=temp_df['close'].cumsum()
        temp_df['s_ma']=np.where(temp_df['idx']<short_num, np.round(temp_df['close'].cumsum()/(temp_df['idx']+1), 2), temp_df['s_ma']) 
        #temp_df['s_ma'] = np.round(pd.rolling_mean(temp_df['close'], window=short_num), 2)
        
        temp_df['l_ma'] = np.round(pd.rolling_mean(temp_df['close'], window=long_num), 2)
        temp_df['l_ma']=np.where(temp_df['idx']<long_num, np.round(temp_df['close'].cumsum()/(temp_df['idx']+1), 2), temp_df['l_ma']) 
        
        #temp_df['dif'] =temp_df['s_ma']-temp_df['l_ma']
        temp_df['dif'] =idx_df['idx']-idx_df['idx']
        temp_df['maca']=idx_df['idx']-idx_df['idx']
        print(temp_df)
        temp_df['dif'] = np.where(temp_df['idx']<1,temp_df['dif'],temp_df['s_ma'].shift(1)*(short_num-1)/(short_num+1)+temp_df['close']*2/(short_num+1)-temp_df['l_ma'].shift(1)*(long_num-1)/(long_num+1)-temp_df['close']*2/(long_num+1))
        temp_df['maca'] = np.round(pd.rolling_mean(temp_df['dif'], window=dif_num), 2)
        temp_df['maca'] = np.where(temp_df['idx']<dif_num, np.round(temp_df['dif'].cumsum()/(temp_df['idx']+1), 2), temp_df['maca'])
        
        temp_df['dea'] = idx_df['idx']-idx_df['idx']
        temp_df['dea'] =np.where(temp_df['idx']<1,temp_df['dif'],temp_df['dea'].shift(1)*(dif_num-1)/(dif_num+1)+temp_df['dif']*2/(dif_num+1))
        #temp_df['dea'] = np.round(pd.rolling_mean(temp_df['dif'], window=dif_num), 2)
        temp_df['bar']=idx_df['idx']-idx_df['idx']
        temp_df['bar']=np.where(temp_df['idx']<1,temp_df['bar'],(temp_df['dif']-temp_df['dea'])*2)
        print(temp_df)
        temp_df.to_csv(ROOT_DIR+'/result/macd%s.csv'%self.code)
        return temp_df
    
    def get_reatime_macd(self,short_num, long_num,dif_num,current_price):
        macd_df=self.get_macd_df(short_num, long_num, dif_num, current_price).tail(1).iloc[0]
        ema1_last=macd_df.s_ma
        ema2_last=macd_df.l_ma
        dif_last=macd_df.dif
        dea_last=macd_df.dea
        macd_last=macd_df.bar
        ema1=ema1_last*(short_num-1)/(short_num+1)+current_price*2/(short_num+1)
        ema2=ema2_last*(long_num-1)/(long_num+1)+current_price*2/(long_num+1)
        dif_realtime=ema1-ema2
        dea_realtime=dea_last*(dif_num-1)/(dif_num+1)+dif_realtime*2/(dif_num+1)
        macd_realtime=2*(dif_realtime-dea_realtime)
        print('For last: dif=%s, dea=%s, bar=%s' % (dif_last,dea_last,macd_last)) 
        print('Realtime: dif=%s, dea=%s, bar=%s' % (dif_realtime,dea_realtime,macd_realtime)) 
        return dif_realtime,dea_realtime,macd_realtime
    
    def is_potential_cross_N(self,cross_num):
        """
        ma5=self.get_ma('close', 5)
        #print 'ma5=', ma5
        ma10=self.get_ma('close', 10)
        #print 'ma10=',ma10
        ma20=self.get_ma('close', 20)
        #print 'ma20=',ma20
        ma30=self.get_ma('close', 30)
        ma60=self.get_ma('close', 60)
        """
        rate=0.5
        ma5=self.get_predict_ma('close', 5,rate)
        print('ma5=', ma5)
        ma10=self.get_predict_ma('close', 10,rate)
        print('ma10=',ma10)
        ma20=self.get_predict_ma('close', 20,rate)
        print('ma20=',ma20)
        ma30=self.get_predict_ma('close', 30,rate)
        ma60=self.get_predict_ma('close', 60,rate)
        current_price=ma5=self.get_ma('close', 1)#potential_df.iloc[0]['close']
        print('current_price=',current_price)
        min_ma=0.0
        max_ma=0.0
        
        if cross_num==1:
            min_ma=ma5
            max_ma=ma5
        else:
            if cross_num==2:
                min_ma=min(ma5,ma10)#round(min(ma5,ma10)*(1-rate/100),2)
                max_ma=max(ma5,ma10)
            else:
                if cross_num==3:
                    min_ma=min(ma5,ma10,ma20)#round(min(ma5,ma10,ma20)*(1-rate/100),2)
                    max_ma=max(ma5,ma10,ma20)
                else:
                    if cross_num==4:
                        min_ma=min(ma5,ma10,ma20,ma30)#round(min(ma5,ma10,ma20,ma30)*(1-rate/100),2)
                        max_ma=max(ma5,ma10,ma20,ma30)
                    else:
                        pass
        print('min_ma=',min_ma)
        is_potential=current_price<=min_ma and current_price*1.10>max_ma
        return is_potential

    def is_cross_N(self,cross_num,cross_type):
        potential_df=self.h_df.tail(1) #[self.today_df.trade>self.today_df.open]
        high_price=potential_df.iloc[0]['high']
        low_price=potential_df.iloc[0]['low']
        #print 'potential_df:',potential_df
        current_price=potential_df.iloc[0]['close']
        if cross_type=='potential':
            current_price=high_price
        else:
            if cross_type=='actual':
                pass
            else:
                pass
        today_open_price=potential_df.iloc[0]['open']
        #print current_price
        ma5=self.get_ma('close', 5)
        #print 'ma5=', ma5
        ma10=self.get_ma('close', 10)
        #print 'ma10=',ma10
        ma20=self.get_ma('close', 20)
        #print 'ma20=',ma20
        ma30=self.get_ma('close', 30)
        ma60=self.get_ma('close', 60)
        current_price_over_ma=False
        open_price_bellow_ma=False
        if cross_num==1:
            current_price_over_ma=current_price>=ma5 and 0.5*(high_price+low_price)>=ma10
            open_price_bellow_ma=today_open_price<=ma5
        else:
            if  cross_num==2:
                current_price_over_ma=current_price>=ma5 and current_price>=ma10 and 0.5*(high_price+low_price)>=ma20
                open_price_bellow_ma=today_open_price<=min(ma5,ma10)
            else:
                if cross_num==3:
                    current_price_over_ma=current_price>=ma5 and current_price>=ma10 and current_price>=ma20
                    open_price_bellow_ma=today_open_price<=min(ma5, ma10,ma20)
                else:
                    if cross_num==4:
                        current_price_over_ma=current_price>=ma5 and current_price>=ma10 and current_price>=ma20 and current_price>=ma60
                        open_price_bellow_ma=today_open_price<=min(ma5, ma10,ma20,ma60)
                    else:
                        pass
        is_cross_N=current_price_over_ma and open_price_bellow_ma
        return is_cross_N

    def is_101(self,potential):
        if len(self.h_df)<3:
            print('No enough history data for 101 verify!')
            return False
        df=self.h_df.tail(3)
        #print df
        try:
            vlm_1=df.iloc[0]['volume']
            vlm_2=df.iloc[1]['volume']
            vlm_3=df.iloc[2]['volume']
            """price consider"""
            """
            if potential==None:
                is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.95*abs(pchg_2)and  pchg_3<1.25*abs(pchg_2) and (vlm_2<0.8*vlm_1)
            else:
                if potential==True:
                    is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.75*abs(pchg_2)and  pchg_3<abs(pchg_2) and (vlm_2<0.8*vlm_1) # and vlm_2<vlm_3)
            """
            """K consider"""
            #"""
            open_1=df.iloc[0]['open']
            open_2=df.iloc[1]['open']
            open_3=df.iloc[2]['open']
            high_1=df.iloc[0]['high']
            high_2=df.iloc[1]['high']
            high_3=df.iloc[2]['high']
            close_1=df.iloc[0]['close']
            close_2=df.iloc[1]['close']
            close_3=df.iloc[2]['close']
            low_1=df.iloc[0]['low']
            low_2=df.iloc[1]['low']
            low_3=df.iloc[2]['low']
            if potential=='potential':
                #revise close here
                #close_1=high_1
                #close_2=high_2
                close_3=high_3
            else:
                pass
            day1_is_strong=round((close_1-open_1),2)/open_1*100>1.5 #and (high_1-close_1)<0.2*(high_1-low_1)
            #day2 is star
            day2_is_justsoso=close_2<=0.5*(close_1+close_2) and abs(close_2-open_2)<(high_2-low_2)*0.33
            #day2_is_justsoso=True
            day3_is_strong=round((close_3-open_3),2)/open_3*100>1 and abs(close_1-open_1)<(close_3-open_3)*1.01 and close_1<=close_3*1.02 and 1.02*close_3>=max(close_1,high_2)
            #day3_is_strong=True
            volume_is_line=vlm_1>vlm_2 and vlm_2<=vlm_3
            volume_is_line=True
            is_101=day1_is_strong and day2_is_justsoso and day3_is_strong and volume_is_line
            #"""
            return is_101
        except:
            return False
        
    def is_10(self,potential):
        if len(self.h_df)<2:
            print('No enough history data for 101 verify!')
            return False
        df=self.h_df.tail(2)
        #print df
        try:
            vlm_1=df.iloc[0]['volume']
            vlm_2=df.iloc[1]['volume']
            #vlm_3=df.iloc[2]['volume']
            """price consider"""
            """
            if potential==None:
                is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.95*abs(pchg_2)and  pchg_3<1.25*abs(pchg_2) and (vlm_2<0.8*vlm_1)
            else:
                if potential==True:
                    is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.75*abs(pchg_2)and  pchg_3<abs(pchg_2) and (vlm_2<0.8*vlm_1) # and vlm_2<vlm_3)
            """
            """K consider"""
            #"""
            open_1=df.iloc[0]['open']
            open_2=df.iloc[1]['open']
            #open_3=df.iloc[2]['open']
            high_1=df.iloc[0]['high']
            high_2=df.iloc[1]['high']
            #high_3=df.iloc[2]['high']
            close_1=df.iloc[0]['close']
            close_2=df.iloc[1]['close']
            #close_3=df.iloc[2]['close']
            low_1=df.iloc[0]['low']
            low_2=df.iloc[1]['low']
            #low_3=df.iloc[2]['low']
            if potential=='potential':
                #revise close here
                #close_1=high_1
                #close_2=high_2
                close_2=high_2
            else:
                pass
            day1_is_strong=round((close_1-open_1),2)/open_1*100>1.5 #and (high_1-close_1)<0.2*(high_1-low_1)
            #day2 is star
            day2_is_justsoso=close_2<=0.5*(close_1+close_2) and abs(close_2-open_2)<(high_2-low_2)*0.25 
            #day2_is_justsoso=True
            #day3_is_strong=round((close_3-open_3),2)/open_3*100>1 and abs(close_1-open_1)<(close_3-open_3)*1.01 and close_1<=close_3*1.02 and 1.02*close_3>=max(close_1,high_2)
            #day3_is_strong=True
            volume_is_line=vlm_1*0.9>vlm_2
            #volume_is_line=True
            is_10=day1_is_strong and day2_is_justsoso and volume_is_line
            #"""
            return is_10
        except:
            return False
        
    def is_constant_1(self):
        potential_df=self.h_df.tail(2) #[self.today_df.trade>self.today_df.open]
        high_price1=potential_df.iloc[0]['high']
        low_price1=potential_df.iloc[0]['low']
        close_price1=potential_df.iloc[0]['close']
        
        high_price2=potential_df.iloc[1]['high']
        low_price2=potential_df.iloc[1]['low']
        close_price2=potential_df.iloc[1]['close']
        is_const_1=(low_price2==high_price2) and (close_price2==round(close_price1*1.1,2)) and (close_price2==low_price2)
        return is_const_1
    
    def is_star(self,rate):
        potential_df=self.h_df.tail(2) #[self.today_df.trade>self.today_df.open]
        high_price1=potential_df.iloc[0]['high']
        low_price1=potential_df.iloc[0]['low']
        close_price1=potential_df.iloc[0]['close']
        
        high_price2=potential_df.iloc[1]['high']
        low_price2=potential_df.iloc[1]['low']
        close_price2=potential_df.iloc[1]['close']
        open_price2=potential_df.iloc[1]['open']
        is_star=abs(close_price2-open_price2)<=rate*(high_price2-low_price2)
        return is_star
    
    def get_star_df(self,rate,raw_df):
        df=raw_df
        crit1=abs(df.close-df.open)/(df.high-df.low)<rate
        df=df[crit1]
        return df
    
    def get_next_df(self,raw_df,filter_df,next_num):
        filter_df_indexs=filter_df.index.values.tolist()
        print(filter_df_indexs)
        next_df_indexs_new=[]
        for filter_df_index in filter_df_indexs:
            next_df_indexs_new.append(filter_df_index+next_num)
        
        print(next_df_indexs_new)
        
        next_df=raw_df[raw_df.index.isin(next_df_indexs_new)]
        next_df_p_change_mean=next_df['p_change'].mean()
        print('next_df_p_change_mean=',next_df_p_change_mean)
        next_df_gt_0=next_df[next_df.p_change>0.2]
        print(len(filter_df))
        print(len(next_df_gt_0))
        filter_then_gt0_rate=round(round(len(next_df_gt_0),2)/len(filter_df),2)
        print('filter_then_next%s_gt0_rate=%s' % (next_num,filter_then_gt0_rate))

    def is_110(self,potential):
        if len(self.h_df)<3:
            print('No enough history data for 101 verify!')
            return False
        df=self.h_df.tail(3)
        #print df
        try:
            vlm_1=df.iloc[0]['volume']
            vlm_2=df.iloc[1]['volume']
            vlm_3=df.iloc[2]['volume']
            """price consider"""
            """
            if potential==None:
                is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.95*abs(pchg_2)and  pchg_3<1.25*abs(pchg_2) and (vlm_2<0.8*vlm_1)
            else:
                if potential==True:
                    is_101=pchg_1>=1.0 and (pchg_2<-0.5) and pchg_3>0.75*abs(pchg_2)and  pchg_3<abs(pchg_2) and (vlm_2<0.8*vlm_1) # and vlm_2<vlm_3)
            """
            """K consider"""
            #"""
            open_1=df.iloc[0]['open']
            open_2=df.iloc[1]['open']
            open_3=df.iloc[2]['open']
            high_1=df.iloc[0]['high']
            high_2=df.iloc[1]['high']
            high_3=df.iloc[2]['high']
            close_1=df.iloc[0]['close']
            close_2=df.iloc[1]['close']
            close_3=df.iloc[2]['close']
            low_1=df.iloc[0]['low']
            low_2=df.iloc[1]['low']
            low_3=df.iloc[2]['low']
            if potential=='potential':
                #revise close here
                close_1=high_1
                close_2=high_2
                close_3=high_3
            else:
                pass
            day1_is_strong=round((close_1-open_1),2)/open_1*100>1.5 #and (high_1-close_1)<0.2*(high_1-low_1)
            #print round((close_1-open_1),2)/open_1*100
            day2_is_strong=round((close_2-open_2),2)/open_2*100>1.5
  
            day3_is_justsoso=(high_3-low_3)<0.8*min((high_1-low_1),(high_2-low_2))
            #day3_is_justsoso=True
            volume_is_line=vlm_3<1.01*min(vlm_1,vlm_2)
            volume_is_line=True
            is_110=day1_is_strong and day2_is_strong and day3_is_justsoso and volume_is_line
            #"""
            return is_110
        except:
            return False
        
    def get_realtime_data(self):
        realtime_df = ts.get_realtime_quotes(self.code) #Single stock symbol
        realtime_df=realtime_df[['code','open','pre_close','price','high','low','bid','ask','volume','amount','time']]
        #realtime_df=realtime_df['pre_close'].astype(float)
        #realtime_df=realtime_df['price'].astype(float)
        """
        open_price= df['open'].mean()
        pre_close_price= df['pre_close'].mean()
        current_price= df['price'].mean()
        high_price= df['high'].mean()
        low_price= df['low'].mean()
        bid_price= df['bid'].mean()
        ask_price= df['ask'].mean()
        volume_price= df['volume'].mean()
        amount_price= df['amount'].mean()
        this_time= df['time'].mean()
        """
        return realtime_df
    
    #def get_realtime_value(self,realtime_df,column_name):
        #return realtime_df[column_name].mean()
    
    def get_realtime_mean_price(self,realtime_df):
        #volume=self.get_realtime_value(realtime_df, 'volume')
        #amount=self.get_realtime_value(realtime_df, 'amount')
        volume=float(realtime_df.ix[0].volume)
        amount=float(realtime_df.ix[0].amount)
        realtime_mean_price=0
        if amount!=0:
            realtime_mean_price=round(round(amount,2)/volume,2)
            print('realtime_mean_price=',realtime_mean_price)
        return realtime_mean_price
        
    def is_realtime_price_gte_mean(self,realtime_df):
        #return self.get_realtime_value(realtime_df, 'price')>=self.get_realtime_mean_price(realtime_df)
        return realtime_df.ix[0].price>=self.get_realtime_mean_price(realtime_df)
    
    def get_weak_lt_interval(self,realtime_df,realtime_mean_price):    #get the interval little than mean price
        realtime_lt_mean_interval=0
        this_time=realtime_df.ix[0].time
        #print type(this_time)
        this_date_time=get_latest_trade_date()+ ' '+this_time
        if realtime_df.ix[0].price>=realtime_mean_price:  #is_realtime_price_gte_mean
            self.realtime_stamp=get_timestamp(this_date_time)
        else:
            this_realtime_lt_mean_stamp=get_timestamp(this_date_time)
            realtime_lt_mean_interval=this_realtime_lt_mean_stamp-self.realtime_stamp
            print('this_date_time=',this_date_time)
            print('realtime_lt_mean_interval=',realtime_lt_mean_interval)
        return realtime_lt_mean_interval
    
    def get_weak_sell_price(self,realtime_df,realtime_mean_price,permit_interval):
        
        #realtime_mean_price=self.get_realtime_mean_price(realtime_df)
        realtime_weak_interval=self.get_weak_lt_interval(realtime_df,realtime_mean_price)
        sell_pirce=0
        if realtime_weak_interval>=permit_interval:  #permit_interval>=60 seconds
            realtime_price=self.get_realtime_value(realtime_df, 'price')
            sell_pirce=realtime_price+0.382*(realtime_mean_price-realtime_price)
            print('realtime_lt_mean_interval=%s, which is great than permit_interval=%s'%(realtime_weak_interval,permit_interval))
            print('set sell_pirce=%s , and realtime_mean_price=%s'%(sell_pirce,realtime_mean_price))
        return sell_pirce
    
    def email_trigger(self,alarm_list):
        if alarm_list:
            alarm_category=alarm_list[3]
            print(self.alarm_category,alarm_category)
            if self.alarm_category==alarm_category:     # alarm_category does not change
                alarm_list=[]
            else:
                self.alarm_category=alarm_category
                send_mail(alarm_list)
                if self.DEBUG_ENABLED: print('alarm_list=',alarm_list)
        else:
            alarm_list=[]
        return alarm_list
    
    def ma_alarm(self,ma_num,current_price,this_date_time):
        ma=self.get_realtime_ma('close', ma_num, current_price)
        if current_price<ma*0.99:
            alarm_content='Down through ma_%s: %s, sell 1/3.' % (ma_num,ma)
            alarm_content=alarm_content
            if self.DEBUG_ENABLED: print(alarm_content)
            alarm_type='alert'
            alarm_category='lt_ma'
            alarm_list=[self.code,this_date_time,alarm_type,alarm_category,alarm_content]
            alarm_list=self.email_trigger( alarm_list)
        else:
            pass
    
    def alarm_logging(self,realtime_df):
        
        #print realtime_df.dtype()
        #open_price=realtime_df.ix[0].open
        #print 'open_price=',open_price
        #print type(open_price)
        """
        open_price= self.get_realtime_value(realtime_df,'open')
        #print type(open_price)
        pre_close_price= self.get_realtime_value(realtime_df,'pre_close')
        current_price= self.get_realtime_value(realtime_df,'price')
        high_price= self.get_realtime_value(realtime_df,'high')
        low_price= self.get_realtime_value(realtime_df,'low')
        bid_price= self.get_realtime_value(realtime_df,'bid')
        ask_price= self.get_realtime_value(realtime_df,'ask')
        volume_price=self.get_realtime_value(realtime_df,'volume') 
        amount_price= self.get_realtime_value(realtime_df,'amount')
        """
        open_price=float(realtime_df.ix[0].open)
        pre_close_price=float(realtime_df.ix[0].pre_close)
        current_price= float(realtime_df.ix[0].price)
        high_price=float(realtime_df.ix[0].high)
        low_price=float(realtime_df.ix[0].low)
        bid_price=float(realtime_df.ix[0].bid)
        ask_price=float(realtime_df.ix[0].ask)
        volume=float(realtime_df.ix[0].volume)
        amount=float(realtime_df.ix[0].amount)
        
        per_change=round((current_price-pre_close_price)*100/pre_close_price,2)
        high_change=round((high_price-pre_close_price)*100/pre_close_price,2)
        #this_time='13:35:47'
        this_time= realtime_df.ix[0].time
        this_date_time=get_latest_trade_date()+' '+this_time
        this_timestamp=get_timestamp(this_date_time)
        print('%s  %s---------------------------------------------------------'% (self.code,this_date_time))
        #print this_timestamp
        hist_high_rate=self.get_average_high(60)
        hist_low_rate=self.get_average_low(60)
        expect_profile_rate=hist_high_rate
        terminate_loss_rate=hist_low_rate
        print('expect_profile_rate=',expect_profile_rate)
        print('terminate_loss_rate=',terminate_loss_rate)
        drop_down_rate=min(-1.5,0.33*terminate_loss_rate)
        print('drop_down_rate=',drop_down_rate)
        hold_time=60*5
        #state_confirm=False
        average_inrcs=1.0
        average_decrs=-1.0
        #print realtime_df
        #print current_price
        alarm_list=[]
        alarm_type=''   #notice,alarm,alarm
        #alarm_category=''
        alarm_content=''
        stock_code=self.code
        #alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
        current_content='Current price = %s, and per_change=%s%%'%(current_price,per_change)
        permit_interval=5*60
        realtime_mean_price=self.get_realtime_mean_price(realtime_df)
        weak_sell_price=self.get_weak_sell_price(realtime_df, realtime_mean_price, permit_interval)
        if weak_sell_price>0:
            alarm_content='weak_sell_price= %s. '% weak_sell_price
            alarm_content=alarm_content+current_content
            if self.DEBUG_ENABLED: print(alarm_content)
            alarm_type='alarm'
            alarm_category='lt_day_mean'
            alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
            self.alarm_category=alarm_category
            send_mail(alarm_list)
            
        
        if high_price>self.max_price:
            if self.max_price!=-1: 
                alarm_content='New topest price: %s. '% high_price
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='notice'
                alarm_category='new_highest'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                self.alarm_category=alarm_category
                send_mail(alarm_list)
                #alarm_list=self.email_trigger( alarm_list)
            self.max_price=high_price
        else:
            pass
        
        if low_price<self.min_price:
            if self.min_price!=1000:
                alarm_content='New lowest price: %s. '%low_price
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='notice'
                alarm_category='new_lowest'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                self.alarm_category=alarm_category
                send_mail(alarm_list)
                #alarm_list=self.email_trigger( alarm_list)
            self.min_price=low_price
            
        if current_price<self.max_price*(1+drop_down_rate/100):
            alarm_content='Descreasing more than %s%% from highest rate %s%% , sell 1/3.' % (drop_down_rate,high_change)
            alarm_content=alarm_content+current_content
            if self.DEBUG_ENABLED: print(alarm_content)
            alarm_type='alarm'
            alarm_category='high_then_down'
            alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
            alarm_list=self.email_trigger( alarm_list)
        else:
            pass
        
        if current_price>=(1+expect_profile_rate)*pre_close_price:
            if self.alarm_trigger_timestamp==0:
                print('Firstly meet expectation, prepare to sell')
                self.alarm_trigger_timestamp=this_time
                alarm_content='Firstly meet expectation rate: %s%%, prepare to sell. ' % expect_profile_rate
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='notice'
                alarm_category='meet_expect'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                alarm_list=self.email_trigger( alarm_list)
            else:
                print('Meet expectation and waiting confirmation...')
                interval=this_timestamp-self.alarm_trigger_timestamp
                if interval>60*5:
                    print('Meet expectation and confirmed, sell now')
                    self.alarm_trigger_timestamp=0
                    alarm_content='Meet expectation rate %s%% and confirmed, sell 1/3. ' % expect_profile_rate
                    alarm_content=alarm_content+current_content
                    if self.DEBUG_ENABLED: print(alarm_content)
                    alarm_type='alarm'
                    alarm_category='confirm_expect'
                    alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                    alarm_list=self.email_trigger( alarm_list)
            exceed_high_rate=min(8.0,expect_profile_rate*1.5)            
            if current_price>(1+exceed_high_rate)*pre_close_price:
                alarm_content='Exactly exceed 1.5x expectation rate %s%% and confirmed, sell 1/2.' % exceed_high_rate 
                alarm_content=alarm_content+current_content
                if self.DEBUG_ENABLED: print(alarm_content)
                alarm_type='alert'
                alarm_category='exceed_high'
                alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                alarm_list=self.email_trigger( alarm_list)
            
        else:
            if current_price<(1+terminate_loss_rate)*pre_close_price:
                if self.alarm_trigger_timestamp==0:
                    print('Firstly reach loss termination, prepare to sell. ')
                    
                    self.alarm_trigger_timestamp=this_time
                    alarm_content='Firstly reach lost termination rate: %s%%, prepare to sell' % terminate_loss_rate
                    alarm_content=alarm_content+current_content
                    if self.DEBUG_ENABLED: print(alarm_content)
                    alarm_type='notice'
                    alarm_category='reach_lost'
                    alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                    alarm_list=self.email_trigger( alarm_list)
                        
                else:
                    interval=this_timestamp-self.alarm_trigger_timestamp
                    if interval>60*3:
                        print('Reach lost termination and confirmed, sell now.')
                        self.alarm_trigger_timestamp=0
                        alarm_content='Reach lost termination rate %s%% and confirmed, sell 1/2. ' % terminate_loss_rate
                        alarm_content=alarm_content+current_content
                        if self.DEBUG_ENABLED: print(alarm_content)
                        alarm_type='alarm'
                        alarm_category='confirm_lost'
                        alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                        alarm_list=self.email_trigger( alarm_list)
                exceed_low_rate=max(-8.0,terminate_loss_rate*1.5)           
                if current_price<(1+exceed_low_rate)*pre_close_price:
                    alarm_content='Exactly exceed 1.5x loss termination rate %s%% and confirmed, sell all. ' % exceed_low_rate
                    alarm_content=alarm_content+current_content
                    if self.DEBUG_ENABLED: print(alarm_content)
                    alarm_type='alert'
                    alarm_category='exceed_lost'
                    alarm_list=[stock_code,this_date_time,alarm_type,alarm_category,alarm_content]
                    alarm_list=self.email_trigger( alarm_list)
            else:
                print('Wave in normal, the current price is %s , perchange is %s%%.' % (current_price,per_change))
                pass
        
        return alarm_list #alarm_trigger_timestamp
    
    def realtime_monitor(self):
        state_confirm=False
        if is_trade_time(get_latest_trade_date()):
            #while is_valid_trade_time(now) :
            while True:
                realtime_df=self.get_realtime_data()
                trigger_timestamp=self.alarm_logging(realtime_df)
                time.sleep(30)
        return
    
    
    def get_market_score(self):
        ma_score=self.get_market_ma_score(period_type='long_turn')
        trend_score=self.get_trend_score()
        market_score=round(ma_score+trend_score,2)
        if market_score>=0:
            market_score=min(market_score,5.0)
        else:
            market_score=max(market_score,-5.0)
        return market_score
    
    def get_ma_score(self):
        ma_type='ma5'
        temp_df=self.temp_hist_df
        if len(temp_df)<2:
            return 0,0,0,0,0,0
        ma_offset=0.002
        WINDOW=3
        ma_type_list=['ma5','ma10','ma20','ma30','ma60','ma120']
        ma_sum_name='sum_o_'
        for ma_type in ma_type_list:
            temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])>ma_offset*temp_df['close'].shift(1),1,0)       #1 as over ma; 0 for near ma but unclear
            temp_df['c_o_ma']=np.where((temp_df['close']-temp_df[ma_type])<-ma_offset*temp_df['close'].shift(1),-1,temp_df['c_o_ma']) #-1 for bellow ma
            ma_sum_name=ma_sum_name+ma_type
            temp_df[ma_sum_name] = np.round(pd.rolling_sum(temp_df['c_o_ma'], window=WINDOW), 2)
            del temp_df['c_o_ma']
        print(temp_df)
        ma5_date_score=temp_df.tail(1).iloc[0].sum_o_ma5
        ma10_date_score=temp_df.tail(1).iloc[0].sum_o_ma10
        ma20_date_score=temp_df.tail(1).iloc[0].sum_o_ma20
        ma30_date_score=temp_df.tail(1).iloc[0].sum_o_ma30
        ma60_date_score=temp_df.tail(1).iloc[0].sum_o_ma60
        ma120_date_score=temp_df.tail(1).iloc[0].sum_o_ma120
        return ma5_date_score,ma10_date_score,ma20_date_score,ma30_date_score,ma60_date_score,ma120_date_score
    
    def get_market_ma_score(self,hist_ma_score=None,period_type=None):
        ma_score=0.0
        if hist_ma_score:
            ma_score=hist_ma_score
        else:
            ma5_date_score,ma10_date_score,ma20_date_score,ma30_date_score,ma60_date_score,ma120_date_score=self.get_ma_score()
            if period_type=='long_turn':
                ma_score=ma_score=0.1*ma5_date_score+0.2*ma10_date_score+0.3*ma30_date_score+0.5*ma60_date_score
            elif period_type=='short_turn':
                ma_score=ma_score=0.5*ma5_date_score+0.3*ma10_date_score+0.2*ma30_date_score+0.1*ma60_date_score
            else:
                pass
        ma_trend_score=self.get_ma_trend_score(temp_hist_df)
        current_ma_score=round(ma_score+ma_trend_score,2)
        if current_ma_score>0:
            current_ma_score=min(current_ma_score,5.0)
        else:
            current_ma_score=max(current_ma_score,-5.0)
        return current_ma_score
    
    def is_cross_point(self,last_short_ma,this_short_ma,last_long_ma,this_long_ma):
        ma_cross_value=0
        if last_long_ma>last_short_ma and this_short_ma>=this_long_ma:
            ma_cross_value=1
        elif last_long_ma<last_short_ma and this_short_ma<=this_long_ma:
            ma_cross_value=-1
        return ma_cross_value
    
    def is_ma_cross_point(self):
        #temp_hist_df=self._form_temp_df()
        if len(self.temp_hist_df)<2:
            return 0,0,0
        hist_df=self.temp_hist_df.tail(2)
        ma5_0=hist_df.iloc[0].ma5
        ma10_0=hist_df.iloc[0].ma10
        ma30_0=hist_df.iloc[0].ma30
        ma60_0=hist_df.iloc[0].ma60
        ma5_1=hist_df.iloc[1].ma5
        ma10_1=hist_df.iloc[1].ma10
        ma30_1=hist_df.iloc[1].ma30
        ma60_1=hist_df.iloc[1].ma60
        ma_5_10_cross=self.is_cross_point(ma5_0, ma5_1, ma10_0, ma10_1)
        ma_10_30_cross=self.is_cross_point(ma10_0, ma10_1, ma30_0, ma30_1)
        ma_30_60_cross=self.is_cross_point(ma30_0, ma30_1, ma60_0, ma60_1)
        return ma_5_10_cross,ma_10_30_cross,ma_30_60_cross
    
    def get_ma_trend_score(self):
        delta_score=0.5
        ma_trend_score=0.0
        ma_5_10_cross,ma_10_30_cross,ma_30_60_cross=self.is_ma_cross_point()
        ma_cross_num=ma_5_10_cross+ma_10_30_cross+ma_30_60_cross
        if ma_cross_num>0:
            ma_trend_score=min(round(ma_cross_num*delta_score,2),1.5)
        else:
            ma_trend_score=max(round(ma_cross_num*delta_score*1.5,2),-2.25)
        return ma_trend_score
    
    def get_trend_score(self,open_change=None,p_change=None):
        delta_score=0.5
        open_rate=0.0
        increase_rate=0.0
        if open_change:
            open_rate=open_change
        else:
            if self.temp_hist_df.empty:
                return 0.0
            else:
                open_rate=self.temp_hist_df.iloc[1].o_change
        if p_chang:
            increase_rate=p_change
        else:
            if self.temp_hist_df.empty:
                return 0.0
            else:
                increase_rate=self.temp_hist_df.iloc[1].p_change
        open_score_coefficient=self.get_open_score(open_rate)
        increase_score_coefficient=self.get_increase_score(increase_rate)
        continue_trend_num,great_change_num,volume_coefficient=self.get_continue_trend_num()
        continue_trend_score_coefficient,recent_great_change_coefficient=self.get_recent_trend_score(continue_trend_num,great_change_num)
        score=(open_score_coefficient+increase_score_coefficient+continue_trend_score_coefficient+recent_great_change_coefficient+volume_coefficient)*0.5
        if score>0:
            score=min(score,5.0)
        else:
            score=max(score,-5.0)
        return score
    
    def get_open_score(self,open_rate):
        great_high_open_rate=1.0
        great_low_open_rate=-1.5
        open_score_coefficient=0.0
        if open_rate>great_high_open_rate:
            open_score_coefficient=round(open_rate/great_high_open_rate,2)
        elif open_rate<great_low_open_rate:
            open_score_coefficient=-round(open_rate/great_low_open_rate,2)
        else:
            pass
        return open_score_coefficient
    
    def get_increase_score(self,increase_rate):
        great_increase_rate=3.0
        great_descrease_rate=-3.0
        increase_score_coefficient=0.0
        if increase_rate>great_increase_rate:
            increase_score_coefficient=round(increase_rate/great_increase_rate,2)
            increase_score_coefficient=max(2.0,open_score_coefficient)
        elif increase_rate<great_low_open_rate:
            increase_score_coefficient=-round(increase_rate/great_low_open_rate,2)
            #increase_score_coefficient=max(-2.0,increase_score_coefficient)
        else:
            pass
        return increase_score_coefficient
    
    def get_continue_trend_num(self):
        if len(self.temp_hist_df)<2:
            return 0,0,0.0
        recent_10_hist_df=self.temp_hist_df.tail(min(10,len(self.temp_hist_df)))
        great_increase_rate=3.0
        great_descrease_rate=-3.0
        great_change_num=0
        great_increase_num=0
        great_descrease_num=0
        great_continue_increase_rate=2.0
        great_continue_descrease_rate=-2.0
        continue_trend_num=0
        latest_trade_date=recent_10_hist_df.tail(1).iloc[0].date
        great_increase_df=recent_10_hist_df[recent_10_hist_df.p_change>great_continue_increase_rate]
        volume_coefficient=0.0
        if great_increase_df.empty:
            pass
        else:
            latest_great_increase_date=great_increase_df.tail(1).iloc[0].date
            if latest_trade_date==latest_great_increase_date:
                continue_increase_num=1
                tatol_inscrease_num=len(great_increase_df)
                while tatol_inscrease_num-continue_increase_num>0:
                    temp_inscrease_df=great_increase_df.head(tatol_inscrease_num-continue_increase_num)
                    if temp_inscrease_df.tail(1).iloc[0].date==get_last_trade_date(latest_great_increase_date):
                        continue_increase_num+=1
                        latest_great_increase_date=get_last_trade_date(latest_great_increase_date)
                    else:
                        break
                continue_trend_num=continue_increase_num
            else:
                great_change_df=recent_10_hist_df[recent_10_hist_df.p_change>great_increase_rate]
                great_increase_num=len(great_change_df)
                
            if continue_increase_num>=2:
                volume0=great_increase_df.tail(2).iloc[0].volume
                volume1=great_increase_df.tail(2).iloc[1].volume
                if volume1>volume0 and volume0:
                    volume_coefficient=min(round(volume1/volume0,2),3.0)
                else:
                    pass
            else:
                pass
        great_decrease_df=recent_10_hist_df[recent_10_hist_df.p_change<great_continue_descrease_rate]
        if great_decrease_df.empty:
            pass
        else:
            latest_great_decrease_date=great_decrease_df.tail(1).iloc[0].date
            if latest_trade_date==latest_great_decrease_date:
                continue_decrease_num=1
                tatol_decrease_num=len(great_decrease_df)
                while tatol_decrease_num-continue_decrease_num>0:
                    temp_decrease_df=great_decrease_df.head(tatol_decrease_num-continue_decrease_num)
                    if temp_decrease_df.tail(1).iloc[0].date==get_last_trade_date(latest_great_decrease_date):
                        continue_decrease_num+=1
                        latest_great_decrease_date=get_last_trade_date(latest_great_decrease_date)
                    else:
                        break
                continue_trend_num=-continue_decrease_num
            else:
                great_change_df=recent_10_hist_df[recent_10_hist_df.p_change<great_descrease_rate]
                great_descrease_num=len(great_change_df)
            
            if continue_decrease_num>=2:
                volume0=great_decrease_df.tail(2).iloc[0].volume
                volume1=great_decrease_df.tail(2).iloc[1].volume
                if volume1>volume0 and volume0:
                    volume_coefficient=max(-round(volume1/volume0,2),-3.0)
                else:
                    pass
            else:
                pass
        if great_increase_num==great_descrease_num:
            pass
        elif great_increase_num>great_descrease_num:
            great_change_num=great_increase_num
        else:
            great_change_num=-great_descrease_num
        return continue_trend_num,great_change_num,volume_coefficient
    
    def get_recent_trend_score(self,continue_trend_num,great_change_num):
        #continue_trend_num,great_change_num,volume_coefficient=get_continue_trend_num(recent_10_hist_df)
        continue_trend_score_coefficient=0.0
        if continue_trend_num>2:
            continue_trend_score_coefficient=round(continue_trend_num/2.0,2)
            continue_trend_score_coefficient=max(3.0,open_score_coefficient)
        elif continue_trend_num<-2:
            continue_trend_score_coefficient=round(continue_trend_num/2.0,2)
        else:
            pass
        recent_great_change_coefficient=0.0
        if great_change_num>2:
            recent_great_change_coefficient=round(great_change_num/2.0,2)
            recent_great_change_coefficient=min(3.0,recent_great_change_coefficient)
        elif great_change_num<-2:
            recent_great_change_coefficient=round(great_change_num/2.0,2)
        else:
            pass
        return continue_trend_score_coefficient,recent_great_change_coefficient

class Market:
    def __init__(self,today_df):
        self.DEBUG_ENABLED=False
        self.today_df=today_df
        #self.all_codes=[]
        self.all_codes=today_df.index.values.tolist()
        
    def set_today_df(self,today_df):
        self.today_df=today_df
        
    def set_debug_mode(self,debug=True):
        self.DEBUG_ENABLED=debug
     #get topest df for history data
     
    def get_today_upper_limit(self):
        today_df=self.today_df
        #print temp_df
        #today_df.to_csv('today_df-0810.csv')
        upper_limit_df=today_df[today_df.trade==(today_df.settlement*1.1).round(2)]   #filter the topest items
        upperr_limit_rate=round(round(len(upper_limit_df),3)/len(today_df),3)
        return upper_limit_df,upperr_limit_rate
    
    def get_today_lower_limit(self):
        today_df=self.today_df
        #print temp_df
        lower_limit_df=today_df[today_df.trade==(today_df.settlement*0.9).round(2)]   #filter the topest items
        lower_limit_rate=round(round(len(lower_limit_df),3)/len(today_df),3)
        return lower_limit_df,lower_limit_rate
    
    def filter_today_df(self,operator,threshhold_rate, column):
        #print temp_df
        today_df=self.today_df
        criteria=True
        if operator=='gte':
            #criteria=temp_df.close>=temp_df.last_close*threshhold_rate/100
            if column=='changepercent':
                criteria=today_df.changepercent>=threshhold_rate
            else:
                if column=='h_change':
                    criteria=today_df.h_change>=threshhold_rate
                else:
                    if column=='l_change':
                        criteria=today_df.l_change>=threshhold_rate
                    else:
                        pass
                
        else:
            if operator=='lt':
                #criteria=temp_df.close<temp_df.last_close*threshhold_rate/100
                criteria=today_df.changepercent<threshhold_rate
                if column=='changepercent':
                    criteria=today_df.changepercent<threshhold_rate
                else:
                    if column=='h_change':
                        criteria=today_df.h_change<threshhold_rate
                    else:
                        if column=='l_change':
                            criteria=today_df.l_change<threshhold_rate
                        else:
                            pass
            else:
                pass
        filter_df=today_df[criteria]
        filter_rate=0
        if len(today_df)!=0:
            filter_rate=round(round(len(filter_df),3)/len(today_df),3)
        return filter_df,filter_rate
    
    def get_up_then_down(self,up_rate,week_percent):
        up_rate=5.0
        week_percent=0.25
        today_df=self.today_df
        criteria2=today_df.changepercent<today_df.h_change*week_percent
        criteria1=today_df.h_change>up_rate
        criteria=criteria1 & criteria2
        #up_and_down_df=today_df[today_df.changepercent<today_df.h_change*0.5]
        up_and_down_df=today_df[criteria]
        #print up_and_down_df
        print(len(up_and_down_df))
    
    def get_h_open_then_down(self,h_open_rate):
        h_open_rate=3.0
        today_df=self.today_df
        criteria2=today_df.changepercent<-h_open_rate
        criteria1=today_df.open>today_df.settlement*(1+h_open_rate/100)
        criteria=criteria1 & criteria2
        #up_and_down_df=today_df[today_df.changepercent<today_df.h_change*0.5]
        up_and_down_df=today_df[criteria]
        #print up_and_down_df
        print(len(up_and_down_df))
    
    def get_split_num(self,split_rate):
        num_list=[]   #[close>=split_late, close<-split_late,high>=split_rate,high<split_rate]
        rate_list=[]
        filter_c_gte,c_gte_rate=self.filter_today_df(operator='gte', threshhold_rate=split_rate, column='changepercent')
        filter_c_lt,c_lt=self.filter_today_df(operator='lt', threshhold_rate=-split_rate,column='changepercent')
        filter_h_gte,h_gte_rate=self.filter_today_df(operator='gte', threshhold_rate=split_rate,column='h_change')
        filter_l_lt,l_lt_rate=self.filter_today_df(operator='lt', threshhold_rate=-split_rate,column='l_change')
        num_list=[len(filter_c_gte),len(filter_c_lt),len(filter_h_gte),len(filter_l_lt)]
        keep_strong_rate=0          #>60, higher then better, 100 will be the best
        #rate(%) of stock_num keepping strong after reached up the expeact increase_rate(6.2%)
        if num_list[2]!=0:
            keep_strong_rate=round(round(num_list[0],3)/num_list[2],3)
        #print 'rate=%s%%,keep_strong_rate=%s'%(split_rate,keep_strong_rate)
        keep_weak_rate=0         #smaller then better, 0 will be pefect
        #rate(%) of stock_num keepping weak after drop downthe expeact increase_rate(-6.2%)
        if num_list[3]!=0:
            keep_weak_rate=round(round(num_list[1],3)/num_list[3],3)
        #print 'rate=-%s%%,keep_weak_rate=%s'%(split_rate,keep_weak_rate)
        rate_list=[c_gte_rate,c_lt,h_gte_rate,l_lt_rate,keep_strong_rate,keep_weak_rate]
        return num_list,rate_list
    
    def today_static(self):
        #today_df,this_time_str=get_today_df()
        #today_df=today_df.astype(float)
        #this_time=datetime.datetime.now()
        #this_time_str=this_time.strftime('%Y-%m-%d %X')
        this_time_str=self.today_df.index.name
        print(this_time_str)
        len_today_df=len(self.today_df)
        #self.get_h_open_then_down(h_open_rate=3.0)
        upper_limit_df,upper_limit_rate=self.get_today_upper_limit()
        lower_limit_df,lower_limit_rate=self.get_today_lower_limit()
        flat_rate=0.2
        # gold split: 3.82:6.18
        middle_increase_rate=4
        middle_c_str='c_gt_%s'%middle_increase_rate
        middle_c_str_n='c_lt_n%s'%middle_increase_rate
        middle_str_h='h_gt_%s'%middle_increase_rate
        middle_str_l_n='l_lt_n%s'%middle_increase_rate
        great_increase_rate=6
        great_c_str='c_gt_%s'%great_increase_rate
        great_c_str_n='c_lt_n%s'%great_increase_rate
        great_h_str='h_gt_%s'%great_increase_rate
        great_l_str_n='l_lt_n%s'%great_increase_rate
        static_data={}
        #static_column_list=['time','h_limit','l_limit','red','green','flat','c>=5','c<=-5','h>=5','l<=-5']   
        static_column_list=['time','h_lmt','l_lmt','R','G','F',middle_c_str,middle_c_str_n,middle_str_h,middle_str_l_n,great_c_str,great_c_str_n,great_h_str,great_l_str_n] 
        #high_limit: h_lmt, low_limit:l_lmt, close_red: R,close_green: G, close_flat:F
        static_data['time']=this_time_str
        num_h_lmt=[len(upper_limit_df)]
        num_l_lmt=len(lower_limit_df)
        static_data['h_lmt']=num_h_lmt
        static_data['l_lmt']=num_l_lmt
        
        print('Now time: %s' % datetime.datetime.now())
        print('-----------------------------------------------------------------')
        #print 'num_upper_limit:num_lower_limit=%s:%s' %(len(upper_limit_df),len(lower_limit_df))
        #print 'upper_limit_rate=%s%%,lower_limit_rate=%s%%' %(upper_limit_rate,lower_limit_rate)
        #print '-----------------------------------------------------------------'
        filter_df_gt_0,positive_rate=self.filter_today_df(operator='gte', threshhold_rate=flat_rate, column='changepercent')
        filter_df_lt_0,nagative_rate=self.filter_today_df(operator='lt', threshhold_rate=-flat_rate,column='changepercent')
        #print 'num_positive:num_nagative=%s:%s' % (len(filter_df_gt_0),len(filter_df_lt_0))
        #print 'positive_rate=%s%%,nagative_rate=%s%%,flat_rate=%s%%' %(positive_rate,nagative_rate,(100-positive_rate-nagative_rate))
        num_R=len(filter_df_gt_0)
        num_G=len(filter_df_lt_0)
        num_F=len_today_df-num_G-num_R
        static_data['R']=num_R
        static_data['G']=num_G
        static_data['F']=num_F
        min_x=min(num_R,num_G,num_F)
        R_F_G=''
        if min_x!=0:
            R_F_G='%s:%s:%s'%(num_R/min_x,num_G/min_x,num_F/min_x)
        print('R:G:F=%s' % R_F_G)
        num_list1,rate_list1=self.get_split_num(middle_increase_rate)
        num_list2,rate_list2=self.get_split_num(great_increase_rate)
        """
        static_data[middle_c_str]=num_list1[0]
        static_data[middle_c_str_n]=num_list1[1]
        static_data[middle_str_h]=num_list1[2]
        static_data[middle_str_l_n]=num_list1[3]
        static_data[great_c_str]=num_list2[0]
        static_data[great_c_str_n]=num_list2[1]
        static_data[great_h_str]=num_list2[2]
        static_data[great_l_str_n]=num_list2[3]
        """
        static_data[middle_c_str]=rate_list1[0]
        static_data[middle_c_str_n]=rate_list1[1]
        static_data[middle_str_h]=rate_list1[2]
        static_data[middle_str_l_n]=rate_list1[3]
        static_data[great_c_str]=rate_list2[0]
        static_data[great_c_str_n]=rate_list2[1]
        static_data[great_h_str]=rate_list2[2]
        static_data[great_l_str_n]=rate_list2[3]
        ps_str=''
        keep_strong_rate=0
        keep_weak_rate=0
        if num_R>=len_today_df*0.5:
            keep_strong_rate=rate_list2[4]
            keep_weak_rate=rate_list2[5]
            ps_str='%s'%middle_increase_rate
        else:
            keep_strong_rate=rate_list1[4]
            keep_weak_rate=rate_list1[5]
            ps_str='%s'%great_increase_rate
        ks_str='ks_'+ps_str                 #'ks' for 'keep strong' rate
        kw_str='kw_n'+ps_str                #'kw' for 'keep weak' rate
        static_column_list=['time','h_lmt','l_lmt','R','G','F',middle_c_str,middle_c_str_n,middle_str_h,middle_str_l_n,great_c_str,great_c_str_n,great_h_str,great_l_str_n,ks_str,kw_str] 
        #high_limit: h_lmt, low_limit:l_lmt, close_red: R,close_green: G, close_flat:F, rate_keep_strong:ks_str, rate_keep_week:kw_str
        static_data[ks_str]=keep_strong_rate
        static_data[kw_str]=keep_weak_rate
        static_result_df=pd.DataFrame(static_data,columns=static_column_list)#,index='aa')
        static_result_df=static_result_df.set_index('time')
        print(static_result_df) #.columns.values.tolist()
        return static_result_df
    
    def get_allcode_list(self):
        #self.get_all_today()
        self.all_codes= self.today_df['code'].values.tolist()
        #print self.all_codes
    def get_p_cross_N(self,cross_num,analyze_type):
        potential_cross_n_list=[]
        hist_all_code=get_all_code(ROOT_DIR+'/hist')
        if self.all_codes:
            #print self.all_codes
            for code in self.all_codes:
                if code in hist_all_code:
                    stockhist=Stockhistory(code_str=code,ktype='D')
                    #stockhist.set_history_df(analyze_type)
                    if stockhist.is_new_stock():
                        pass
                    else:
                        if stockhist.is_potential_cross_N(cross_num):
                            potential_cross_n_list.append(code)
                else:
                    #new stock
                    pass
            print('potential_cross_%s_list= %s' % (cross_num,potential_cross_n_list))
        
        else:
            pass
        return potential_cross_n_list
    
    def get_cross_N(self,cross_num,analyze_type):
        potential_cross_n_list=[]
        actual_cross_n_list=[]
        success_rate=0
        hist_all_code=get_all_code(ROOT_DIR+'/hist')
        if self.all_codes:
            #print self.all_codes
            for code in self.all_codes:
                if code in hist_all_code:
                    stockhist=Stockhistory(code_str=code,ktype='D')
                    #stockhist.set_history_df(analyze_type)
                    if stockhist.is_new_stock():
                        pass
                    else:
                        if stockhist.is_cross_N(cross_num,'potential'):
                            potential_cross_n_list.append(code)
                        if stockhist.is_cross_N(cross_num,'actual'):
                            actual_cross_n_list.append(code)
                else:
                    #new stock
                    pass
            print('potential_cross_%s_list= %s' % (cross_num,potential_cross_n_list))
            print('actual_cross_%s_list= %s' % (cross_num,actual_cross_n_list))
            if len(potential_cross_n_list):
                success_rate=round(round(len(actual_cross_n_list),2)/len(potential_cross_n_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_cross_n_list,success_rate
    
    def get_star_df(self, star_rate,raw_df=None):
        df=self.today_df
        #del df['name']
        if raw_df != None:
            df=raw_df
        
        #print df
        #print df.dtypes
        df=df.astype(float)
        Crit=abs(df.trade-df.open)<star_rate*(df.high-df.low)
        star_df=df[Crit]
        """
        pre_name='star'
        #today=datetime.date.today()
        today=datetime.datetime.now()
        #if today.isoweekday()<6:
        today_str=today.strftime(ISODATEFORMAT)
        star_df.index.name=today_str
        #df.to_csv(ROOT_DIR+'/data/%s%s.csv'%(filename,today_str),encoding='GB18030')  #'utf-8')
        star_df.to_excel(ROOT_DIR+'/data/%s.xlsx'%(pre_name+today_str), sheet_name='%s'%today_str)
        print 'The the star code today are saved as ROOT_DIR+/data/%s.xlsx'%(pre_name+today_str)
        """
        return star_df
    
    def get_10(self,analyze_type,code_list=None):
        potential_10_list=[]
        actual_10_list=[]
        success_rate=0
        #hist_all_code=get_all_code('ROOT_DIR+/hist')
        all_codes=get_all_code(ROOT_DIR+'/update')
        if code_list:
            all_codes=list(set(all_codes).intersection(set(code_list)))
        if all_codes:
            for code in all_codes:
                stockhist=Stockhistory(code_str=code,ktype='D')
                if analyze_type=='realtime':
                    pass
                    #stockhist.set_history_df('realtime')
                if stockhist.is_new_stock():
                    pass
                else:
                    if stockhist.is_10('potential'):
                        potential_10_list.append(code)
                    if stockhist.is_10('actual'):
                        actual_10_list.append(code)
            print('potentia_10_list= %s' % (potential_10_list))
            print('actual_10_list= %s' % (actual_10_list))
            if len(potential_10_list):
                success_rate=round(round(len(actual_10_list),2)/len(potential_10_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_10_list,success_rate
    
    def get_101(self,analyze_type,code_list=None):
        potential_101_list=[]
        actual_101_list=[]
        success_rate=0
        #hist_all_code=get_all_code('ROOT_DIR+/hist')
        all_codes=get_all_code(ROOT_DIR+'/update')
        if code_list !=None:
            all_codes=list(set(all_codes).intersection(set(code_list)))
        #print 'all_codes=',all_codes
        if all_codes:
            for code in all_codes:
                stockhist=Stockhistory(code_str=code,ktype='D')
                if analyze_type=='realtime':
                    pass
                    #stockhist.set_history_df('realtime')
                if stockhist.is_new_stock():
                    pass
                else:
                    if stockhist.is_101('potential'):
                        potential_101_list.append(code)
                    if stockhist.is_101('actual'):
                        actual_101_list.append(code)
            print('potential_101_list= %s' % (potential_101_list))
            print('actual_101_list= %s' % (actual_101_list))
            if len(potential_101_list):
                success_rate=round(round(len(actual_101_list),2)/len(potential_101_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_101_list,success_rate

    def get_110(self):
        potential_110_list=[]
        actual_110_list=[]
        success_rate=0
        if self.all_codes:
            for code in self.all_codes:
                stockhist=Stockhistory(code_str=code,ktype='D')
                if stockhist.is_new_stock() or stockhist.is_constant_1() or stockhist.is_star(rate=0.33):
                    pass
                else:
                    if stockhist.is_110('potential'):
                        potential_110_list.append(code)
                    if stockhist.is_110('actual'):
                        actual_110_list.append(code)
            print('potential_110_list= %s' % (potential_110_list))
            print('actual_110_list= %s' % (actual_110_list))
            if len(potential_110_list):
                success_rate=round(round(len(actual_110_list),2)/len(potential_110_list),2)
        else:
            pass
        print('success_rate=',success_rate)
        return actual_110_list,success_rate
    
    def get_positive_target(self,target_list):
        target_count=len(target_list)
        postive_count=0
        total_avrg=0
        postive_avrg_incrs=0
        postive_rate=0
        for code in target_list:
            try:
                p_change=self.today_df.ix[code]['changepercent']
                p_change=float(p_change)
                total_avrg+=p_change
                if p_change>0.01:
                    postive_count+=1
                    postive_avrg_incrs+=p_change
            except:
                #print 'except'
                pass
        if postive_count!=0:
            postive_avrg_incrs=round(postive_avrg_incrs/postive_count,2)
        if target_count!=0:
            postive_rate=round(round(postive_count,2)/target_count,2)
            total_avrg=round(total_avrg/target_count,2)
        print('postive_rate_2nd_day=',postive_rate)
        print('postive_avrg_incrs=',postive_avrg_incrs)
        print('total_avrg=',total_avrg)
        return total_avrg,postive_rate
    
    def get_hist_cross_analyze(self):
        latest_trade_day=get_latest_trade_date()
        N=4
        for N in range(1,N):
            print('=============================')
            print('History statistics analyze for actual_cross_%s_list  on  %s' %(N,latest_trade_day))
            actual_cross_n_list,success_rate=self.get_cross_N(N,'history')
            total_avrg,postive_rate=self.get_positive_target(actual_cross_n_list)
        return
    
    def get_realtime_cross_analyze(self):
        latest_trade_day=get_latest_trade_date()
        N=4
        for n in range(1,N):
            print('=============================')
            print('Realtime statistics analyze for actual_cross_%s_list  on  %s' %(n,latest_trade_day))
            actual_cross_n_list,success_rate=self.get_cross_N(n,'realtime')
        return
    
    def market_analyze_today(self):
        #init_all_hist_from_export()
        latest_trade_day=get_latest_trade_date()
        today_df,df_time_stamp=get_today_df()
        self.set_today_df(today_df)
        out_file_name=ROOT_DIR+'/result/result-' + latest_trade_day + '.txt'
        output=open(out_file_name,'w')
        sys.stdout=output
        #market=Market(today_df)
        #update_all_hist(today_df,df_time_stamp)
        #actual_101_list,success_101_rate=market.get_101()
        self.get_hist_cross_analyze()
        self.get_realtime_cross_analyze()
        actual_101_list,success_101_rate=self.get_101('realtime')
        df_101=today_df[today_df.index.isin(actual_101_list)]
        #print 'df_101=',df_101
        star_rate=0.25
        star_df=self.get_star_df(star_rate)
        #print star_df
        star_list=star_df.index.values.tolist()
        code_10,rate=self.get_10('history', star_list)
        #print code_10
        t_df=today_df
        df_10=t_df[t_df.index.isin(code_10)]
        #print df_10
        filename=ROOT_DIR+'/data/is10-%s.csv' % latest_trade_day
        df_10.to_csv(filename)
        #code_10= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
        #print 'potential_101_list=',potential_101_list
        realtime_101_list,success_101_rate=self.get_101('realtime',code_10)
        sys.stdout=sys.__stdout__
        output.close()
        print('market_analyze completed for today.')
    
class Monitor:
    
    def __init__(self,holding_code_list):
        self.holding_stocks=holding_code_list
        
    def set_holding_code(self,holding_code_list):
        self.holding_stocks=holding_code_list 
         
    def set_debug_mode(self,debug=True):
        self.DEBUG_ENABLED=debug
        
    def get_holding_statics(self):
        latest_trade_day=get_latest_trade_date()
        out_file_name=ROOT_DIR+'/result/static-' + latest_trade_day + '.txt'
        static_output=open(out_file_name,'w')
        sys.stdout=static_output
        #code_list=['600031','603988','603158','601018','002282','002556','600673','002678','000998','601088','600398']
        code_list=self.holding_stocks
        for code in code_list:
            print('---------------------------------------------------')
            stock=Stockhistory(code,'D')
            print('code:', code)
            stock.hist_analyze(10)
            stock.ma_analyze()
            print('---------------------------------------------------')
        
        sys.stdout=sys.__stdout__
        static_output.close()
        print('Stock static completed')
        
    def realtime_monitor(self,given_interval):
        interval=60     #30 seconds
        data={}
        column_list=['code','open','pre_close','price','high','low','bid','ask','volume','amount','time']
        my_df=pd.DataFrame(data,columns=column_list)#,index=['
        latest_trade_day=get_latest_trade_date()
        morning_time0=datetime.datetime.strptime(latest_trade_day+' 09:30:00','%Y-%m-%d %X')
        morning_time1=datetime.datetime.strptime(latest_trade_day+' 11:30:00','%Y-%m-%d %X')
        noon_time0=datetime.datetime.strptime(latest_trade_day+' 13:00:00','%Y-%m-%d %X')
        noon_time1=datetime.datetime.strptime(latest_trade_day+' 15:00:00','%Y-%m-%d %X')
        next_morning_time0=morning_time0+datetime.timedelta(days=1)
        #while is_trade_time(latest_trade_day):
        alarm_category_dict={}
        max_price_dict={}
        min_price_dict={}
        for code in self.holding_stocks:
            alarm_category_dict[code]='normal'
            max_price_dict[code]=-1
            min_price_dict[code]=1000
        
        while True:
            this_time=datetime.datetime.now()
            this_time_str=this_time.strftime('%Y-%m-%d %X')
            #print 'now_time=',this_time
            #this_time=datetime.datetime(2015,7,21,13,25,20,0)
            #print my_df
            if this_time>morning_time1 and this_time<noon_time0 :
                interval_time=noon_time0-this_time
                interval=interval_time.days*24*3600+interval_time.seconds
                print('Have a lest druing the noon, sleep %s seconds...'%interval)
            else:
                if this_time<=morning_time0:
                    interval_time=morning_time0-this_time
                    interval=interval_time.days*24*3600+interval_time.seconds
                    print('Market does not start yet in the morning, sleep %s seconds...'%interval)
                else:
                    if this_time>=noon_time1:
                        interval_time=next_morning_time0-this_time
                        interval=interval_time.days*24*3600+interval_time.seconds
                        market_analyze_today()
                        #market_analyze_today()
                        write_hist_index()
                        self.get_holding_statics()
                        print('Market will start in next morning, sleep %s seconds...'%interval)
                    else:
                        if (this_time>=morning_time0 and this_time<=morning_time1)  or (this_time>=noon_time0 and this_time<=noon_time1):
                            latest_trade_day=get_latest_trade_date()
                            my_df=pd.DataFrame(data,columns=column_list)        #empty df
                            for code in self.holding_stocks:
                                out_file_name=ROOT_DIR+'/result/realtime_' +code +'_'+latest_trade_day + '.txt'
                                realtime_output=open(out_file_name,'a')
                                sys.stdout=realtime_output
                                mystock=Stockhistory(code,ktype='D')
                                mystock.set_alarm_category(alarm_category_dict[code])
                                mystock.set_max_price(max_price_dict[code])
                                mystock.set_min_price(min_price_dict[code])
                                mystock.set_debug_mode(True)
                                realtime_df=mystock.get_realtime_data()
                                mystock.alarm_logging(realtime_df)
                                alarm_category=mystock.alarm_category
                                alarm_category_dict[code]=alarm_category
                                max_price_dict[code]=mystock.max_price
                                min_price_dict[code]=mystock.min_price
                                my_df=my_df.append(realtime_df,ignore_index=True)
                                #market_test()
                                realtime_output.close()
                            del my_df['time']
                            my_df=my_df.set_index('code')
                            my_df=my_df.astype(float)
                            my_df.insert(1, 'p_change', 100.00*((my_df.price-my_df.pre_close)/my_df.pre_close).round(4))
                            if this_time.minute%30==0:
                                stock_code='holding_stock'
                                alarm_type='notice'
                                alarm_category='realtime_report'
                                alarm_content='%s'%my_df
                                alarm_list=[stock_code,this_time_str,alarm_type,alarm_category,alarm_content]
                                send_mail(alarm_list)
                                #market_test()
                            interval=given_interval
                        else:
                            pass
            time.sleep(interval)
            
class Monitorthread(threading.Thread):
    def __init__(self,thread_num,thread_type,interval,code_str=None):
        threading.Thread.__init__(self)  
        self.thread_num = thread_num 
        self.thread_type=thread_type 
        self.interval = interval  
        self.thread_stop = False
        
    def set_interval(self,interval):
        self.interval=interval
        
    def run(self): #Overwrite run() method, put what you want the thread do here  
        while not self.thread_stop:
            if self.thread_type=='panmian':
                today_df,this_time_str=get_today_df()
                market=Market(today_df)
                #market.get_p_cross_N(3, 'realtime')
                static_result_df=market.today_static()
                pass
            else:
                if self.thread_type=='holding' and self.code_str!=None:
                    """
                    mystock=Stockhistory(self.code_str,ktype='D')
                    mystock.set_alarm_category(alarm_category_dict[code])
                    mystock.set_max_price(max_price_dict[code])
                    mystock.set_min_price(min_price_dict[code])
                    mystock.set_debug_mode(True)
                    realtime_df=mystock.get_realtime_data()
                    mystock.alarm_logging(realtime_df)
                    alarm_category=mystock.alarm_category
                    alarm_category_dict[code]=alarm_category
                    max_price_dict[code]=mystock.max_price
                    min_price_dict[code]=mystock.min_price
                    my_df=my_df.append(realtime_df,ignore_index=True)
                    """
                    pass
                else:
                    if self.thread_type=='report':
                        pass
                    else:
                        if self.thread_type=='hist_update':
                            pass
                        else:
                            print('Thread_type incorrect! Make sure your input is corret!')
                    
            print('Thread Object(%d), Time:%s\n' %(self.thread_num, time.ctime()))  
            time.sleep(self.interval)  
            
    def stop(self):  
        self.thread_stop = True  

def thread_test():  
    thread1 = Monitorthread(1, 1)  
    thread2 = Monitorthread(2, 2)  
    thread1.start()  
    thread2.start()  
    time.sleep(10)  
    thread1.stop()  
    thread2.stop()  
          
def test():
    hist_dir=ROOT_DIR+'/hist'
    hist_code=get_all_code(hist_dir)
    print('hist_code:',hist_code)
    if len(hist_code)==0:
        print('Begin pre-processing  the hist data')
        init_all_hist_from_export()
        print('pre-processing completed')
        hist_code=get_all_code(hist_dir)
    code_str=hist_code[5]
    stock=Stockhistory(code_str='000157',ktype='D')
    #print 'Stockhistory:',stock.h_df
    topest_df,topest_rate= stock.get_hist_topest(recent_days=60)
    print(topest_df)
    print('topest_rate=',topest_rate)
    filter_df,filter_rate=stock.filter_hist('gte', 2, 100)
    print(filter_df)
    print('filter_rate=',filter_rate)
    ma5=stock.get_ma('close', 5)
    print(ma5)
    ma5_high=stock.get_ma('high', 5)
    print(ma5_high)
    ma5_volume=stock.get_ma('volume', 5)
    print(ma5_volume)
    
    print(stock.is_cross_N(1,'actual'))
    
    #market=Market()    
    #print market.today_df
    #hist_df=market.update_one_hist(code_str,market.today_df)
    #print hist_df


def test1(): 
    market=Market()
    #market.write_today_df()
    #df=market.read_today_df()
    #print 'market.today_df:',market.today_df
    #actual_cross_n_list,success_rate=market.get_cross_N(1)
    """
    actual_cross_1_list= ['600317', '600724', '600971', '601101', '601518', '601139', '000570', '000620', '601699', '600403', '601018', '600736', '600821', '002574', '600573', '600272', '600997', '601929', '000525', '002118', '000597', '600448', '601088', '000595', '300138', '600360', '601369', '300047', '600456', '600721', '000504', '000685', '002514', '002541', '002637', '300131', '000967', '002005', '002017', '002386', '601666', '000723', '000851', '002528', '000014', '000933', '002395', '002430', '002653', '300314', '600195', '600202', '600400', '600518', '603167', '600157', '600666', '000722', '000983', '600529', '600774', '002678', '300120', '300336', '600093', '600239', '600463', '600687', '000973', '000988', '600712', '002161', '002190', '600100', '002143', '600241', '600280', '601677', '603002', '002504', '300339', '600422', '000768', '002458', '002507', '300218', '601222', '000605', '002152', '002413', '002468', '603166', '002396', '002665', '600017', '600267', '600475', '600590', '600684', '600822', '600823', '601058', '601313', '601999', '000503', '000703', '000777', '000780', '000955', '002054', '002266', '002287', '002332', '002339', '002409', '002446', '002482', '002513', '002563', '002585', '002684', '300024', '300067', '300115', '300128', '300222', '300324', '300325', '300331', '002317', '300182', '300195', '000020', '000910', '002352', '600079', '600270', '000090', '002579', '600460', '601001', '000509', '000753', '002375', '600096', '300063', '000532', '002472', '600814', '000032', '300061', '300103', '600480', '000899', '002149', '002641', '600011', '002049', '002193', '002433', '600508', '600004', '000523', '600123', '600778', '600800', '002128', '600095', '601328', '600853', '600395', '300031', '600368', '300265', '600348', '600546', '000937', '000909', '601898', '601991', '601333', '002134', '600603', '002489', '600488', '000809', '600835', '002205', '002708', '002448', '000698', '300299', '002543', '600579', '300100', '000417', '002099', '300169', '002297', '600577', '000514', '600555', '002041', '002687', '002401', '600121', '600523', '600179', '000408', '300238', '600571', '000529', '600650', '002309', '600613', '600653', '601117', '002492', '000903', '600189', '600780', '600027', '002275', '000636', '000889', '000838', '000037', '000739', '000752', '300003', '002715', '300116', '002419', '600331', '000543', '600418', '002510', '000760', '300326', '002420', '002286', '601177', '600761', '300046', '002270', '300284', '002305', '002035', '000822', '002447', '600883', '002394', '600088', '300219', '600399', '600792', '300092', '601126', '000919', '600485', '002265', '300057', '000790', '600328', '000606', '002554', '600623', '600160', '300274', '300037', '002524', '600112', '002692', '002336', '002634', '600353', '300127', '002483', '002592', '002132', '002247', '000419', '600874', '002077', '000806', '300054', '002072', '601208', '600501', '000972', '002658', '300062', '300329', '601113', '600775', '600740', '002150', '600854', '002130', '600308', '300393', '000019', '300132', '600421', '601965', '002480', '002062', '300154', '002474', '600236', '000936', '002398', '002729', '000830', '000908', '600131', '300286', '600051', '000673', '300034', '000663', '000683', '600355', '002481', '600958', '600651', '600982', '002068', '000539', '600075', '002562', '000533', '000670', '601636', '000572', '601225', '600776', '000802', '603123', '300239', '000886', '000430', '600863', '600965', '002404', '002186', '002313', '600183', '000421', '002392', '002088', '002454', '600500', '000678', '600726', '002223', '300292', '300084', '600439', '000667', '300117', '300306', '601588', '002171', '002532', '002083', '600641', '300106', '601008', '600557', '600791', '600321', '300147', '601188', '300221', '300370', '600843', '000153', '600973', '000060', '600056', '002399', '002422', '600350', '600839', '000721', '002557', '002538', '002621', '002369', '002277', '000985', '000639', '600345', '600054', '300157', '002145', '000707', '002527', '600693', '600988', '000725', '002300', '002393', '600861', '002267', '600084', '000004', '002222', '600316', '601727', '300091', '002591', '600551', '000737', '300307', '000720', '002304', '002436', '603128', '000962', '600979', '600816', '600985', '002603', '600162', '600192', '002243', '600449', '000762', '002218', '600636', '000738', '002452', '600295', '600593', '002666', '601798', '000702', '600517', '600231', '600851', '300039', '600784', '002328', '600115', '300215', '002526', '300320', '002382', '601616', '000423', '300129', '601678', '600578', '601216', '002423', '002377', '002225', '000682', '601003', '000672', '000999', '002101', '002025', '000949', '300108', '600077', '000929', '002220', '300256', '000705', '002566', '002058', '002714', '002181', '600356', '600766', '600795', '600746', '002168', '300253', '600261', '600227', '603766', '601168', '600663', '002123', '002046', '002357', '002654', '000413', '000960', '000713', '600569', '002598', '600969', '000761', '601107', '600396', '601339', '002209', '300347', '002111', '600377', '002228', '002675', '000559', '600743', '002521', '600362', '000978', '300009', '601558', '600483', '600187', '300080', '300360', '000561', '002459', '000036', '002618', '603126', '000900', '600980', '002570', '000422', '600565', '000592', '000631', '002428', '600219', '601198', '600619', '300338', '002214', '000030', '600540', '002559', '002231', '002465', '000785', '300086', '600601', '300330', '002184', '600237', '600723', '600796', '600537', '300305', '600664', '603898', '600976', '600007', '601231', '002221', '600218', '002402', '600372', '000756', '600176', '600833', '002324', '002672', '601098', '300247', '300248', '000531', '300099', '300202', '300228', '002338', '000070', '002531', '002499', '600230', '600751', '002202', '600515', '600052', '600509', '600273', '601099', '000966', '600686', '002198', '000795', '600141', '600022', '000404', '002320', '600312', '002457', '600389', '000521', '300045', '600995', '300269', '000778', '600674', '002544', '000519', '600311', '600838', '600238', '002071', '002467', '000301', '002351', '600282', '000882', '600661', '002142', '600600', '600668', '002262', '300355', '002201', '600129', '000923', '000918', '603268', '600966', '600033', '600787', '300275', '000632', '002706', '300181', '600315', '600512', '300273', '002342', '002605', '002208', '300258', '002469', '000511', '600481', '002613', '002303', '002475', '002503', '601258', '600300', '002007', '002311', '000930', '600243', '000729', '000544', '600062', '600352', '300263', '601789', '600393', '600805', '600252', '000858', '600809', '600322', '002695', '002105', '300321', '300021', '002042', '002215', '600386', '600900', '600671', '603555', '600658', '002608', '000096', '000912', '000748', '002600', '002306', '000501', '600660', '600235', '600638', '600120', '600634', '600892', '300310', '600690', '000759', '002172', '002048', '002238', '600279', '002003', '300014', '600074', '002725', '600213', '300102', '600692', '300378', '600735', '002252', '001896', '600381', '002705', '300225', '600392', '600917', '002614', '002495', '300346', '002445', '000848', '300075', '600781', '600438', '002076', '600367', '000839', '002685', '603000', '000488', '000026', '600309', '300277', '600738', '600208', '601069', '300350', '600419', '600090', '002335', '002321', '000585', '000617', '600888', '600067', '000166', '002075', '600616', '600782', '300095', '002279', '000977', '000619', '002014', '002053', '600066', '600284', '002633', '600423', '600860', '600276', '002242', '600118', '002372', '000935', '300174', '000965', '002040', '002479', '300235', '002693', '600228', '300072', '002291', '300344', '601989', '000505', '002713', '002690', '600038', '600742', '300390', '002240', '600130', '002060', '600458', '600498', '600223', '000975', '300245', '600889', '002141', '000589', '600171', '300052', '300365', '600117', '600707', '000953', '300216', '600385', '002484', '600987', '000799', '300313', '002258', '002157', '002651', '600262', '002373', '002411', '603328', '002726', '600299', '000963', '002065', '002518', '600785', '002722', '300094', '600566', '600103', '600598', '603100', '002061', '600567', '601555', '002639', '601599', '300170', '601028', '000810', '000681', '600824', '002371', '600594', '600532', '000826', '002550', '603456', '300406', '600184', '002289', '002322', '002556', '002424', '000666', '002741', '300234', '002023', '002085', '603169', '300375', '300415', '000541', '300211', '600868', '603099', '300408', '002730', '300401', '603077', '300140', '000928', '000028', '002515', '002327', '600548', '000590', '300400', '603636', '002119', '600820', '002747', '002734']
    
    actual_cross_2_list= ['600317', '600724', '000751', '600971', '601139', '000570', '000620', '601699', '600538', '600225', '600573', '600272', '600358', '002540', '600997', '000525', '002118', '600188', '000597', '600448', '000750', '601088', '300138', '002580', '601369', '000797', '600456', '000685', '002514', '000967', '002017', '002386', '000851', '002528', '000014', '000933', '002395', '300314', '600518', '603167', '600157', '000983', '600774', '000988', '600712', '600490', '000812', '002103', '002143', '600241', '601677', '300175', '300339', '300218', '601222', '000582', '000605', '002055', '002152', '002169', '002657', '002197', '002665', '300004', '300187', '600475', '600823', '601058', '601999', '000637', '000777', '000780', '000955', '000971', '002266', '002339', '002446', '002482', '002563', '002585', '002684', '300067', '300222', '300324', '300325', '300331', '300348', '300254', '000020', '000524', '600270', '002579', '300290', '600058', '600397', '002094', '000509', '000753', '002187', '002375', '300063', '000045', '002472', '600814', '600480', '002149', '002641', '600011', '600531', '002193', '002433', '600508', '601886', '600095', '601328', '600395', '600368', '600348', '600546', '000937', '601898', '601991', '002134', '600543', '600488', '000809', '600835', '002358', '000698', '300299', '300100', '600580', '000055', '300169', '600750', '000514', '002041', '600523', '601199', '300238', '600571', '000529', '002309', '600613', '601117', '000555', '000968', '002462', '002492', '002410', '002567', '000903', '600027', '000636', '000838', '000739', '300003', '600418', '002510', '000609', '002286', '601177', '002270', '300284', '002305', '000822', '002011', '300219', '300092', '601126', '000046', '300057', '300212', '000790', '600328', '002131', '300118', '600623', '300274', '300037', '600110', '002592', '002132', '000419', '600874', '002072', '600501', '300349', '300062', '300329', '601113', '002150', '600854', '002002', '002364', '600421', '002195', '002146', '002062', '002474', '600236', '300050', '600125', '002398', '000908', '600131', '600455', '600829', '000683', '600355', '600107', '600958', '002068', '002584', '000533', '000572', '601225', '600776', '600005', '600965', '300207', '002404', '002186', '300150', '002313', '002088', '002223', '300292', '600875', '000667', '300117', '600679', '002028', '002083', '600641', '300106', '600557', '600865', '300147', '601188', '002403', '300221', '600139', '300370', '600973', '002399', '002084', '002344', '601918', '600839', '002557', '600059', '600741', '002621', '002078', '002277', '002478', '000985', '002026', '000639', '600260', '600345', '002145', '002350', '002527', '600988', '002300', '002267', '600084', '000004', '002222', '600316', '601727', '000662', '600551', '002144', '000720', '002304', '600884', '002436', '603128', '603008', '600162', '600192', '600449', '000762', '002218', '000039', '600636', '600978', '600295', '002666', '601798', '000702', '600517', '000852', '600851', '600784', '002328', '300215', '601678', '002560', '600578', '000551', '002225', '601003', '000672', '000999', '002572', '300108', '000929', '002220', '300256', '600737', '002331', '002714', '600081', '002181', '002629', '600356', '600766', '600795', '300029', '300253', '600612', '600261', '601168', '600506', '002635', '002123', '002194', '000713', '300283', '600969', '600251', '600018', '600396', '601339', '300347', '600377', '000970', '002675', '600743', '600320', '000978', '600483', '300080', '000036', '002618', '000900', '600527', '000422', '600565', '002341', '000631', '600219', '600540', '601007', '300086', '600237', '600723', '600537', '600592', '603898', '002490', '600007', '601231', '600218', '000860', '000798', '000756', '600833', '002324', '000528', '601098', '300248', '300139', '000531', '300099', '300202', '600459', '600830', '000070', '601818', '600751', '002202', '600509', '601099', '000966', '600686', '600773', '002198', '002534', '600141', '600022', '002457', '600995', '300269', '000425', '000778', '600020', '600674', '601137', '000519', '600311', '600238', '002071', '300315', '000301', '002079', '000957', '002142', '002262', '002576', '600129', '000918', '600420', '600966', '002509', '600033', '600787', '300275', '000727', '300181', '600127', '600315', '600512', '300163', '300273', '002605', '002469', '002303', '002007', '000548', '600769', '600243', '000729', '000544', '600062', '600000', '300263', '601789', '600252', '000858', '600809', '600322', '300199', '002215', '300073', '600671', '600658', '002608', '000912', '601801', '002508', '600660', '600235', '600859', '600892', '600068', '000759', '002172', '002136', '000418', '002051', '002568', '600279', '600074', '600323', '002252', '001896', '600477', '002705', '002495', '002445', '002599', '600781', '600438', '000596', '002076', '002619', '000338', '603000', '300081', '000488', '600208', '000828', '002335', '000568', '600067', '300146', '600616', '300107', '000400', '300095', '002279', '300303', '600285', '600066', '600992', '002138', '002242', '600731', '600615', '600036', '002040', '300072', '002595', '600742', '002140', '600498', '601166', '600171', '002340', '300365', '600707', '000920', '600385', '000887', '300313', '002373', '002726', '601555', '000681', '600594', '300070', '002289', '000666', '300134']
    print 'Postive Statistics for  actual_cross_1_list 20150601'
    total_avrg,postive_rate=market.get_positive_target(actual_cross_1_list)
    
    print 'Postive Statistics for  actual_cross_2_list 20150601'
    total_avrg,postive_rate=market.get_positive_target(actual_cross_2_list)
    
    actual_cross_3_list= ['000751', '600225', '600188', '000750', '601088', '600490', '000582', '002657', '000637', '600058', '000045', '600011', '600395', '601898', '601991', '002358', '000055', '601199', '601117', '000555', '000968', '600027', '002011', '000046', '300274', '300349', '002146', '600125', '600829', '600446', '600717', '600005', '600741', '002478', '002572', '600795', '300253', '600018', '000970', '300059', '000860', '601818', '600369', '000623', '600020', '600000', '600015', '000912', '601939', '002051', '000869', '000596', '000338', '601169', '000916', '601998', '600992', '600036', '601166', '601288', '601555']
    print 'Postive Statistics for  actual_cross_3_list 20150601'
    total_avrg,postive_rate=market.get_positive_target(actual_cross_3_list)
    """
    #market.get_cross_analyze()
    actual_101_list,success_101_rate=market.get_101('history')
    t_df=market.today_df
    df_101=t_df[t_df.index.isin(actual_101_list)]
    print('df_101:',df_101)
    """
    actual_cross_n_list,success_rate=market.get_cross_N(1, 'history')
    intersect_list=list(set(actual_cross_n_list).intersection(set(actual_101_list)))
    print 'intersect_list=',intersect_list
    market.get_positive_target(intersect_list)
    """
    #actual_110_list,success_110_rate=market.get_110()
def update_test():
    file_name=ROOT_DIR+'/data/all2015-07-17.csv'
    file_time_str=get_file_timestamp(file_name)
    print(file_time_str)
    today_df,today_df_update_time=get_today_df()
    update_all_hist(today_df,today_df_update_time)
    
def test2():
    #init_all_hist_from_export()
    latest_trade_day=get_latest_trade_date()
    today_df,df_time_stamp=get_today_df()
    out_file_name=ROOT_DIR+'/result/result-' + latest_trade_day + '.txt'
    output=open(out_file_name,'w')
    sys.stdout=output
    market=Market(today_df)
    update_all_hist(today_df,df_time_stamp)
    #actual_101_list,success_101_rate=market.get_101()
    market.get_hist_cross_analyze()
    market.get_realtime_cross_analyze()
    actual_101_list,success_101_rate=market.get_101('realtime')
    t_df=market.today_df
    df_101=t_df[t_df.index.isin(actual_101_list)]
    #print 'df_101=',df_101
    
    star_rate=0.25
    star_df=market.get_star_df(star_rate)
    #print star_df
    star_list=star_df.index.values.tolist()
    code_10,rate=market.get_10('history', star_list)
    #print code_10
    t_df=market.today_df
    df_10=t_df[t_df.index.isin(code_10)]
    #print df_10
    filename=ROOT_DIR+'/data/is10-%s.csv' % latest_trade_day
    df_10.to_csv(filename)
    #code_10= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
    #print 'potential_101_list=',potential_101_list
    realtime_101_list,success_101_rate=market.get_101('realtime',code_10)
    sys.stdout=sys.__stdout__
    output.close()
    print('test2 completed')
    
def test3():
    potential_101_list= ['000043', '000404', '000407', '000525', '000585', '000693', '000751', '000757', '000759', '000838', '000923', '002032', '002054', '002056', '002084', '002089', '002105', '002150', '002287', '002432', '002460', '002478', '002606', '002654', '002692', '002749', '300003', '300030', '300063', '300103', '300116', '300152', '300183', '300187', '300199', '300207', '300218', '300411', '600097', '600101', '600128', '600187', '600279', '600368', '600476', '600508', '600612', '600794', '600830', '600960', '600969', '600983', '601001', '601107', '601179', '601801', '601808', '601818', '601958', '603003', '603399']
    actual_101_list= ['000043', '000404', '000525', '000585', '000693', '000751', '000759', '000838', '002056', '002084', '002089', '002287', '002432', '002460', '002478', '002606', '002692', '300103', '300199', '300207', '300411', '600097', '600101', '600128', '600187', '600368', '600476', '600508', '600612', '600794', '600830', '600969', '600983', '601001', '601179', '601808', '601818', '601958', '603003', '603399']
    diffence_list=list(set(potential_101_list).difference(set(actual_101_list)))
    print(diffence_list)
    
    union_list=list(set(potential_101_list).union(actual_101_list))
    
    actual_cross_1_list=['600307', '600586', '002128', '002232', '000662', '600248', '600508', '000933', '000065', '600792', '300028', '600584', '300244', '600546', '600612', '600983', '002003', '002089', '002460', '002709', '300207', '300411', '000983', '000693', '000043', '600097', '600123', '600432', '000759', '000899', '601777', '600348', '000761', '600429', '002466', '600187', '000878', '600121', '300007', '601898', '000514', '600857', '603399', '601666', '000582', '002033', '600818', '603611', '601958', '600509', '600638', '600768', '000552', '601699', '601016', '600172', '600196', '603333', '600202', '002749', '300041', '600809', '600022', '600748', '002418', '002320', '600106', '600740', '300157', '000571', '300378', '601288', '002646', '002298', '002279', '000546', '300069', '002112', '601126']
    potential_cross_1_list=['600307', '600586', '002128', '002232', '000662', '600248', '600508', '000933', '000065', '600792', '300028', '600584', '300244', '600546', '600612', '600983', '002003', '002089', '002460', '002709', '300207', '300411', '000983', '000693', '000043', '600097', '600123', '600432', '000759', '000899', '601777', '600348', '000761', '600429', '002466', '600187', '000878', '600121', '300007', '601898', '000514', '600857', '603399', '601666', '000582', '002033', '600818', '603611', '601958', '600509', '600638', '600768', '000552', '601699', '601016', '600172', '600196', '603333', '600202', '002749', '300041', '600809', '600022', '600748', '002418', '002320', '600106', '600740', '300157', '000571', '300378', '601288', '000005', '002646', '002298', '600072', '002279', '000546', '300069', '300053', '002366', '002112', '600112', '600249', '300032', '000913', '002322', '002659', '300016', '601126', '300166', '300337', '300052', '603123', '002513', '300375', '300217', '600706', '002343', '300328', '300340', '002751', '002611', '300261', '300144', '002361', '300051', '300165']
    
    intersect_list=list(set(actual_cross_1_list).intersection(set(actual_101_list)))
    print('intersect_list=',intersect_list)
    print(len(intersect_list))
    
    potential_intersect_list=list(set(potential_cross_1_list).intersection(set(potential_101_list)))
    print('potential_intersect_list=',potential_intersect_list)
    print(len(potential_intersect_list))

def test4():
    print(get_latest_trade_date())
    market=Market()
    star_rate=0.25
    star_df=market.get_star_df(star_rate)
    print(star_df)
    star_list=star_df.index.values.tolist()
    code_10,rate=market.get_10('realtime', star_list)
    print(code_10)
    t_df=market.today_df
    df_10=t_df[t_df.index.isin(code_10)]
    print(df_10)
    df_10.to_csv(ROOT_DIR+'/data/is10-2015-06-04.csv')
    potential_101_list=code_10
    potential_101_list= ['002579', '002243', '002117', '000970', '600654', '000533', '600377', '300080', '600382', '600423', '600208', '601188', '002338', '002237', '002234', '000666', '600858', '601678', '300104', '002487', '600581', '600580', '002242', '600616', '600618', '002412', '002148', '600320', '000409', '600978', '600405', '600819', '600816', '002201', '002207', '002562', '000637', '601390', '000593', '600094', '600146', '600668', '000785', '601718', '300018', '002585', '600449', '600565', '600219', '300342', '600282', '002323', '002328', '300347', '600825', '000673', '601100', '300115', '002551', '002490', '002495', '002392', '600741', '600621', '002597', '002073', '000004', '600133', '601339', '000419', '000555', '600570', '603100', '600419', '000955', '000952', '000789', '300155', '002213', '601999', '600707', '600680', '600686', '600159', '601002', '002668', '002503', '600052', '002006', '002501', '600513', '600222', '600225', '300349', '600350', '300291', '600358', '600292', '000888', '601116', '300122', '300125', '601800', '002387', '002386', '002389', '002263', '601231', '600633', '601600', '002042', '600495', '002169', '600499', '600643', '600640', '600308', '000548', '300317', '300314', '300091', '600396', '000726', '000729', '002227', '603166', '603167', '600393', '600636', '002121', '002125', '600695', '002087', '603008', '600169', '000509', '000501', '601519', '601518', '002409', '600360', '000698', '600506', '600332', '600330', '002103', '002651', '300286', '002083', '603001', '000897', '600802']
    print('potential_101_list=',potential_101_list)
    realtime_101_list,success_101_rate=market.get_101('realtime',potential_101_list)


#test()    
#test1()
#test2()
#update_test()
#get_top_list()



def stock_test():
    latest_trade_day=get_latest_trade_date()
    out_file_name=ROOT_DIR+'/result/static-' + latest_trade_day + '.txt'
    output=open(out_file_name,'w')
    sys.stdout=output
    code_list=['600031','603988','603158','601018','002282','002556','600673','002678','000998','601088','600398']
    for code in code_list:
        print('---------------------------------------------------')
        stock=Stockhistory(code,'D')
        print('code:', code)
        stock.hist_analyze(10)
        stock.ma_analyze()
        print('---------------------------------------------------')
    
    sys.stdout=sys.__stdout__
    output.close()
    print('Stock static completed')
    
def stock_test1():
        code='002678'
        #code='000987'
        #code='601018'
        #code='002466'
        stock=Stockhistory(code,'D')
        #print stock.h_df
        temp_df=stock._form_temp_df()
        #df=df.set_index('date')
        #df=filter_df_by_date(raw_df=df, from_date_str='2015-05-08', to_date_str='2015-06-18')
        #df=filter_df_by_date(raw_df=df, from_date_str='2015-06-19', to_date_str='2015-07-08')
        df=filter_df_by_date(raw_df=temp_df, from_date_str='2015-07-09', to_date_str='2015-08-18')
        #print df
        print(len(df))
        h_change_mean=df['h_change'].mean()
        print(h_change_mean)
        l_change_mean=df['l_change'].mean()
        print(l_change_mean)
        df=df[df.h_change>0.5*h_change_mean]
        #df=df[df.l_change<-6.2]
        print(len(df))
        #stock.set_hist_df_by_date(from_date_str='2015-05-08', to_date_str='2015-06-18')
        #stock.set_hist_df_by_date(from_date_str='2015-06-19', to_date_str='2015-07-08')
        #stock.set_hist_df_by_date(from_date_str='2015-07-09', to_date_str='2015-08-18')
        #print stock.h_df
        star_df=stock.get_star_df(rate=0.25,raw_df=temp_df)
        stock.get_next_df(temp_df, filter_df=star_df, next_num=1)
        topest_df=temp_df[temp_df.close==(temp_df.last_close*1.1).round(2)]
        stock.get_next_df(raw_df=temp_df, filter_df=topest_df, next_num=1)
        
        """
        print stock.get_average_high(60)
        print stock.get_average_low(60)
        print stock.get_average_rate(60,'l_change')*1.5
        realtime_df=stock.get_realtime_data()
        realtime_mean_price=stock.get_realtime_mean_price(realtime_df)
        #stock.get_weak_lt_interval(realtime_df,realtime_mean_price)
        permit_interval=60*5
        stock.get_weak_sell_price(realtime_df, realtime_mean_price,permit_interval)
        #stock.ma_analyze()
        """
        """
        df=stock._form_temp_df()
        #print df
        close_list=df['ma5'].values.tolist()
        boduan_list=find_boduan(close_list)
        print 'boduan_list=',boduan_list
        
        close_list=df['close'].values.tolist()
        print close_list,len(close_list)
        ma5_list=get_ma_list(close_list, 5)
        ma10_list=get_ma_list(close_list, 10)
        ma20_list=get_ma_list(close_list, 20)
        ss=pd.Series(ma5_list,index=df.index)
        df.insert(8,'ma5',ss)
        print df
        """
def stock_realtime_monitor():
    """
    code='601018'
    stock=Stockhistory(code,'D')
    stock.realtime_monitor()
    """
    #init_all_hist_from_export()
    code_list=['002678','000987','002269','601018','603158','002556']#'002755','603988','600276','601857']
    my_monitor=Monitor(code_list)
    my_monitor.realtime_monitor(60)
    

"""
write_hist_index()
index_df=get_hist_index('sh')
print index_df
"""
def market_test():
    #print 'start-----------'
    today_df,this_time_str=get_today_df()
    """
    today_df=today_df.astype(float)
    today_df.insert(6, 'h_change', ((today_df.changepercent*today_df.high)/today_df.trade).round(2))
    today_df.insert(7, 'l_change', ((today_df.changepercent*today_df.low)/today_df.trade).round(2))
    """
    #print today_df
    market=Market(today_df)
    #market.get_p_cross_N(3, 'realtime')
    static_result_df=market.today_static()

def score_market():
    today_df,this_time_str=get_today_df()
    gt5_df=today_df[today_df['changepercent']>2.0]
    #print today_df
    ma_type='ma5'
    ma_offset=0.01
    great_score=4
    great_change=5.0
    all_codes=gt5_df.index.values.tolist()
    data={}
    stronge_ma_3_list=[]
    result_column=['code','l_s_date','l_s_state','t_s_date','t_s_state','t_date','t_state','score','oper3']
    result_df=pd.DataFrame(data,columns=result_column)
    if all_codes:
        for code_str in all_codes:
            stock=Stockhistory(code_str,'D')
            code_data=stock.get_trade_df(ma_type,ma_offset,great_score,great_change)
            #print 'code_data=',code_data
            if code_data:
                code_df=pd.DataFrame(code_data,index=['code'],columns=result_column)
                result_df=result_df.append(code_df,ignore_index=True)
                if code_data['oper3'] ==3:
                    stronge_ma_3_list.append(code_str)
    
    result_df.to_csv(ROOT_DIR+'/result/score_%s.csv' % this_time_str[:10])
    if stronge_ma_3_list:
        print('stronge_ma5_list=',stronge_ma_3_list)
        stronge_ma5_df=today_df[today_df.index.isin(stronge_ma_3_list)]
        print(stronge_ma5_df)
    print('result_df:')
    result_df=result_df.sort_index(axis=0, by='oper3', ascending=False)
    print(result_df)
    
    result_df_score_gt0=result_df[result_df['score']>=0]
    print(result_df_score_gt0)
    result_df_oper3_gt1=result_df[result_df['oper3']>=1]
    print(result_df_oper3_gt1)
    
def atr_market():
    today_df,this_time_str=get_today_df()
    #file_name=ROOT_DIR+'/data/all2015-10-26.csv'
    #today_df=read_today_df(file_name)
    #print today_df
    gt2_df=today_df[today_df['changepercent']>2.0]
    #print today_df
    short_num=20
    long_num=55
    all_codes=gt2_df.index.values.tolist()
    latest_break_20_list=[]
    latest_break_55_list=[]
    top5_average_sum=0.0
    latest_day_str=get_latest_trade_date()
    print('latest_day_str=',latest_day_str)
    if all_codes and latest_day_str:
        for code_str in all_codes:
            stock=Stockhistory(code_str,'D')
            #print 'code_str=',code_str
            temp_df,latest_break_20,latest_break_55,top5_average=stock.get_atr_df(short_num, long_num)
            if latest_day_str==latest_break_20:
                latest_break_20_list.append(code_str)
            
            if latest_day_str==latest_break_55:
                latest_break_55_list.append(code_str)
            
            top5_average_sum+=top5_average
        top5_average_all_market=round(top5_average_sum/len(all_codes))
    print('latest_break_20_list=',latest_break_20_list)
    print('latest_break_55_list=',latest_break_55_list)
    print('top5_average_all_market=',top5_average_all_market)
    latest_break_20_df=today_df[today_df.index.isin(latest_break_20_list)]
    latest_break_20_df.index.name='code'
    column_list=latest_break_20_df.columns.values.tolist()
    #print 'column_list=',column_list
    latest_break_55_df=today_df[today_df.index.isin(latest_break_55_list)]
    latest_break_55_df.index.name='code'
    latest_break_20_df.to_csv(ROOT_DIR+'/result_temp/atr_break_20_%s.csv' % latest_day_str)
    latest_break_55_df.to_csv(ROOT_DIR+'/result_temp/atr_break_55_%s.csv' % latest_day_str)
    #print 'latest_break_20_df:'
    #print latest_break_20_df
    #print 'latest_break_55_df:'
    #print latest_break_55_df
    return latest_break_20_list,latest_break_55_list,top5_average_all_market

def change_static_market():
    code='002678'
    #code='000987'
    #code='601018'
    code='002466'
    #code='600650'
    #code='300244'
    #code='000001'
    #code='300033'
    #code='000821'
    short_num=20
    long_num=55
    dif_num=9
    current_price=12.10
    
    init_rate=-2.5
    rate_interval=0.5
    range_num=18
    rate_list=specify_rate_range(init_rate, rate_interval, range_num)
    df_data={}
    column_list=['code']
    #gt_data['code']=code
    for rate in rate_list:
        column_name='gt_%s' % rate
        column_list.append(column_name)
    empty_df=pd.DataFrame(df_data,columns=column_list)#,index=[''])
    #print 'static_df=',static_df
    static_df_h=static_df_l=static_df_p=empty_df
    today_df,this_time_str=get_today_df()
    #file_name=ROOT_DIR+'/data/all2015-10-26.csv'
    #today_df=read_today_df(file_name)
    #print today_df
    gt2_df=today_df[today_df['changepercent']>2.0]
    #print today_df
    short_num=20
    long_num=55
    all_codes=today_df.index.values.tolist()
    latest_break_20_list=[]
    latest_break_55_list=[]
    top5_average_sum=0.0
    latest_day_str=get_latest_trade_date()
    #print 'latest_day_str=',latest_day_str
    for code in all_codes:
        stock=Stockhistory(code,'D')
        gt_static_df_h=stock.change_static(rate_list,column='h_change')
        gt_static_df_p=stock.change_static(rate_list,column='p_change')
        gt_static_df_l=stock.change_static(rate_list,column='l_change')
        if gt_static_df_h.empty:
            pass
        else:
            static_df_h=static_df_h.append(gt_static_df_h, ignore_index=True)
        if gt_static_df_p.empty:
            pass
        else:
            static_df_p=static_df_p.append(gt_static_df_p, ignore_index=True)
        if gt_static_df_l.empty:
            pass
        else:
            static_df_l=static_df_l.append(gt_static_df_l, ignore_index=True)
            #print 'static_df=',static_df
    """
        for rate_t_h in rate_list:
            max_profit_loss_ratio=0.0
            max_rate_t_l=0.0
            max_rate_t_h=0.0
            for rate_t_l in rate_list:
                if rate_t_h>rate_t_l and rate_t_h>=0.5 and rate_t_l<=0.5:
                    column_name_h='gt_%s' % rate_t_h
                    column_name_l='gt_%s' % rate_t_l
                    h_rate=gt_static_df_h[column_name_h].mean()
                    l_rate=gt_static_df_l[column_name_l].mean()
                    profit_loss_ratio=round(h_rate/(1-l_rate),2)
                    if profit_loss_ratio>=max_profit_loss_ratio:
                        max_profit_loss_ratio=profit_loss_ratio
                        max_rate_t_l=rate_t_l
                        max_rate_t_h=rate_t_h
                    #print 'hight_terminate_rate=',rate_t_h
                    #print 'low_terminate_rate=',rate_t_l
                    #print 'then profit_loss_ratio=',profit_loss_ratio
                else:
                    pass
            if max_profit_loss_ratio>0:
                print 'max_rate_t_h=',max_rate_t_h
                print 'max_rate_t_l=',max_rate_t_l
                print 'max_profit_loss_ratio=',max_profit_loss_ratio
    """
    static_df_h.to_csv(ROOT_DIR+'/result_temp/h_change_static_%s.csv' % latest_day_str)
    static_df_p.to_csv(ROOT_DIR+'/result_temp/p_change_static_%s.csv' % latest_day_str)
    static_df_l.to_csv(ROOT_DIR+'/result_temp/l_change_static_%s.csv' % latest_day_str)
    
    close_change_df=static_df_p.describe()
    high_change_df=static_df_h.describe()
    low_change_df=static_df_l.describe()
    close_change_df.to_csv(ROOT_DIR+'/result_temp/p_change_static_describe_%s.csv' % latest_day_str)
    high_change_df.to_csv(ROOT_DIR+'/result_temp/h_change_static_describe_%s.csv' % latest_day_str)
    low_change_df.to_csv(ROOT_DIR+'/result_temp/l_change_static_describe_%s.csv' % latest_day_str)
    
    return  static_df_p,static_df_h,static_df_l


def mini_atr_market():
    code='002678'
    #code='000987'
    #code='601018'
    code='002466'
    #code='600650'
    #code='300244'
    #code='000001'
    #code='300033'
    #code='000821'
    short_num=20
    long_num=55
    dif_num=9
    current_price=12.10
    
    init_rate=-2.5
    rate_interval=0.5
    range_num=18
    rate_list=specify_rate_range(init_rate, rate_interval, range_num)
    df_data={}
    column_list=['code']
    #gt_data['code']=code
    for rate in rate_list:
        column_name='gt_%s' % rate
        column_list.append(column_name)
    empty_df=pd.DataFrame(df_data,columns=column_list)#,index=[''])
    #print 'static_df=',static_df
    static_df_h=static_df_l=static_df_p=empty_df
    today_df,this_time_str=get_today_df()
    short_num=20
    long_num=55
    all_codes=today_df.index.values.tolist()
    latest_break_20_list=[]
    latest_break_55_list=[]
    top5_average_sum=0.0
    latest_day_str=get_latest_trade_date()
    #print 'latest_day_str=',latest_day_str
    atr_in_codes=[]
    atr_in_codes_last=[]
    df_data={}
    column_list= ['code','date','atr_in_rate']
    atr_min_df=pd.DataFrame(df_data,columns=column_list)
    #print('all_codes=',all_codes)
    for code in all_codes:
        stock=Stockhistory(code,'D')
        atr_in_rate,last_date,atr_in_rate_last,last2_date=stock._form_temp_df1()
        #print(atr_in_rate,last_date,atr_in_rate_last,last2_date)
        if atr_in_rate:
            df_data={}
            df_data['code']=[str(code)]
            df_data['date']=[latest_day_str]
            df_data['atr_in_rate']=[atr_in_rate]
            #code_df=pd.DataFrame(code_data,index=['code'],columns=result_column)
            #result_df=result_df.append(code_df,ignore_index=True)
            atr_df=pd.DataFrame(df_data,columns=column_list)
            atr_min_df=atr_min_df.append(atr_df,ignore_index=True)
            atr_in_codes.append([code,atr_in_rate])
        if atr_in_rate_last:
            atr_in_codes_last.append([code,atr_in_rate_last])
    atr_min_df=atr_min_df.sort_index(axis=0, by='atr_in_rate', ascending=False)
    atr_min_df.to_csv(ROOT_DIR+'/result_temp1/mini_atr_market_%s.csv' % latest_day_str)
    stocksql_obj=ps.StockSQL()
    stocksql_obj.insert_table(data_frame=atr_min_df,table_name='mini_atr')
    print(atr_min_df)
    print('atr_in_codes=',atr_in_codes)
    print('atr_in_codes_last=',atr_in_codes_last)
    return  atr_in_codes

def back_test_atr():
    last_day_str=get_last_trade_date()
    today_df,this_time_str=get_today_df()
    #print 'today_df=',today_df
    today_column_list= ['code','changepercent', 'trade', 'open', 'high', 'low', 'settlement', 'h_change', 'l_change', 'volume', 'turnoverratio']
    today_df_code_list=today_df.index.values.tolist()
    last_20_file_name=ROOT_DIR+'/result_temp/atr_break_20_%s.csv' % last_day_str
    last_break_20_df=pd.read_csv(last_20_file_name,index_col=0,names=today_column_list)
    last_55_file_name=ROOT_DIR+'/result_temp/atr_break_55_%s.csv' % last_day_str
    last_break_55_df=pd.read_csv(last_55_file_name,index_col=0,names=today_column_list)
    #print 'last_break_20_df=',last_break_20_df
    last_break_20_code_list=last_break_20_df.index.values.tolist()
    #print 'last_break_20_code_list=',last_break_20_code_list
    last_break_20_code_list=list(set(last_break_20_code_list).intersection(set(today_df_code_list)))
    last_break_55_code_list=last_break_55_df.index.values.tolist()
    last_break_55_code_list=list(set(last_break_55_code_list).intersection(set(today_df_code_list)))
    latest_break_20_df=today_df[today_df.index.isin(last_break_20_code_list)]
    #print 'latest_break_20_df=',latest_break_20_df
    latest_break_20_df_mean=latest_break_20_df['changepercent'].mean()
    latest_break_20_df_high_mean=latest_break_20_df['h_change'].mean()
    latest_break_55_df=today_df[today_df.index.isin(last_break_55_code_list)]
    #print 'latest_break_55_df=',latest_break_55_df
    latest_break_55_df_mean=latest_break_55_df['changepercent'].mean()
    latest_break_55_df_high_mean=latest_break_55_df['h_change'].mean()
    
    print('latest_break_20_df_mean=',latest_break_20_df_mean)
    print('latest_break_20_df_high_mean=',latest_break_20_df_high_mean)
    print('latest_break_55_df_mean',latest_break_55_df_mean)
    print('latest_break_55_df_high_mean',latest_break_55_df_high_mean)
    
    latest_day_str=get_latest_trade_date()
    latest_20_file_name=ROOT_DIR+'/result_temp/atr_break_20_%s.csv' % latest_day_str
    latest_break_20_df=pd.read_csv(latest_20_file_name)
    #print latest_break_20_df
    #print latest_break_20_df.index.name=[code]
    latest_break_20_df=latest_break_20_df.set_index('code')
    
    latest_55_file_name=ROOT_DIR+'/result_temp/atr_break_55_%s.csv' % latest_day_str
    latest_break_55_df=pd.read_csv(latest_55_file_name)
    latest_break_55_df=latest_break_55_df.set_index('code')
    latest_break_20_code_list=latest_break_20_df.index.values.tolist()
    
    latest_break_20_code_list= json.loads(json.dumps(latest_break_20_code_list))
    last_break_20_code_list_int=[]
    for code_str in last_break_20_code_list:
        last_break_20_code_list_int.append(string.atoi(code_str))
    print('last_break_20_code_list_int=',last_break_20_code_list_int)
    print('latest_break_20_code_list=',latest_break_20_code_list)
    continue_break_20_list=list(set(latest_break_20_code_list).intersection(set(last_break_20_code_list_int)))
    latest_break_55_code_list=latest_break_55_df.index.values.tolist()
    latest_break_55_code_list= json.loads(json.dumps(latest_break_55_code_list))
    last_break_55_code_list_int=[]
    for code_str in last_break_55_code_list:
        last_break_55_code_list_int.append(string.atoi(code_str))
    print('last_break_55_code_list_int=',last_break_55_code_list_int)
    continue_break_55_list=list(set(latest_break_55_code_list).intersection(set(last_break_55_code_list_int)))

    print('latest_break_55_code_list=', latest_break_55_code_list)
    
    print('continue_break_20_list=',continue_break_20_list)
    print('continue_break_55_list=',continue_break_55_list)
    
    
#test2()     
#stock_test1()
#stock_realtime_monitor()
#thread_test()
#market_test()



import _thread

def test_thread1():
    _thread.start_new_thread(market_test,())
    print('doing thread1')
    _thread.start_new_thread(stock_realtime_monitor,())
    print('doing thread')
    
    
    return

#test_thread1()
