# -*- coding:utf-8 -*-
from pdsql import *
from fileoperation import *
from tradeStrategy import *

def monitor_test():
    
    today_df,time_str=get_today_df()
    print(today_df)
    atr_min_df=today_df.sort_index(axis=0, by='atr', ascending=True)
    print(atr_min_df)
    #today_df=today_df.set_index('code')
    high_open_rate=0.5
    today_df_h_open=today_df[today_df.open>=today_df.settlement*(1+high_open_rate*0.01)]
    print('+++++++++++++++++++++++++++++++++++++++++++')
    print(today_df_h_open)
    print(len(today_df_h_open))
    print('+++++++++++++++++++++++++++++++++++++++++++')
    gap_code_list=[]
    for code in today_df_h_open.index.values.tolist():
        #print(today_df_h_open.index.values.tolist())
        #print(today_df_h_open.ix[code])
        this_open=today_df_h_open.ix[code].open
        this_trade=today_df_h_open.ix[code].trade
        this_high=today_df_h_open.ix[code].high
        this_low=today_df_h_open.ix[code].low
        
        stock_hist_obj=Stockhistory(code,'D')
        temp_df=stock_hist_obj._form_temp_df()
        #print(temp_df.tail(1))
        update_today=False
        if update_today:
            temp_df=temp_df.tail(2).head(1)
        else:
            temp_df=temp_df.tail(1)
        temp_df=temp_df.tail(2).head(1)
        last_open=temp_df.iloc[0].open
        last_close=temp_df.iloc[0].close
        last_high=temp_df.iloc[0].high
        last_low=temp_df.iloc[0].low
        if min(this_open,this_trade)>last_high*(1+0.01*high_open_rate) and (this_high!=this_low):
        #if min(this_open,this_trade)>max(last_open,last_close):
            print(code,this_open,this_trade,last_close,last_close)
            gap_code_list.append(code)
    print('gap_code_list=',gap_code_list)
    print(len(gap_code_list))
    great_change=4.0
    today_df_gt_3=today_df[today_df.changepercent>great_change]
    today_df_lt_n3=today_df[today_df.changepercent<-great_change]
    today_df_h_gt_3=today_df[today_df.h_change>great_change]
    today_df_l_lt_n3=today_df[today_df.l_change<-great_change]
    print(len(today_df_gt_3),len(today_df_h_gt_3),today_df_h_gt_3['changepercent'].mean())
    print(len(today_df_lt_n3),len(today_df_l_lt_n3),today_df_l_lt_n3['changepercent'].mean())
    strong_rate=round(round(len(today_df_gt_3),2)/len(today_df_lt_n3),2)
    print('strong_rate=',strong_rate)
    
    stock_sql_obj=StockSQL()
    madata=stock_sql_obj.query_data(table='madata',fields='code,reversal,extreme',condition='reversal!=0 and extreme!=0 limit 100')
    #madata=stock_sql_obj.query_data(table='madata',fields='code,reversal,extreme',condition='reversal>1.33 limit 100')
    filter_codes=madata['code'].values.tolist()
    filter_df=today_df[today_df.index.isin(filter_codes)]
    mean_inscrease=filter_df['changepercent'].mean()
    print(filter_df)
    print(mean_inscrease)
    return
monitor_test()