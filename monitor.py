# -*- coding:utf-8 -*-
from pdsql import *
from fileoperation import *
from tradeStrategy import *

def monitor_test():
    stock_sql_obj=StockSQL()
    madata=stock_sql_obj.query_data(table='madata',fields='code,reversal,extreme',condition='reversal!=0 and extreme!=0 limit 100')
    #madata=stock_sql_obj.query_data(table='madata',fields='code,reversal,extreme',condition='reversal>1.33 limit 100')
    filter_codes=madata['code'].values.tolist()
    today_df,time_str=get_today_df()
    #print(today_df)
    atr_min_df=today_df.sort_index(axis=0, by='atr', ascending=True)
    print(atr_min_df)
    #today_df=today_df.set_index('code')
    great_change=4.0
    today_df_gt_3=today_df[today_df.changepercent>great_change]
    today_df_lt_n3=today_df[today_df.changepercent<-great_change]
    today_df_h_gt_3=today_df[today_df.h_change>great_change]
    today_df_l_lt_n3=today_df[today_df.l_change<-great_change]
    print(len(today_df_gt_3),len(today_df_h_gt_3),today_df_h_gt_3['changepercent'].mean())
    print(len(today_df_lt_n3),len(today_df_l_lt_n3),today_df_l_lt_n3['changepercent'].mean())
    strong_rate=round(round(len(today_df_gt_3),2)/len(today_df_lt_n3),2)
    print('strong_rate=',strong_rate)
    filter_df=today_df[today_df.index.isin(filter_codes)]
    mean_inscrease=filter_df['changepercent'].mean()
    print(filter_df)
    print(mean_inscrease)
    
    return

monitor_test()