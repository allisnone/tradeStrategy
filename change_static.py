from tradeStrategy import *

import pandas as pd

code='002678'
#code='000987'
#code='601018'
#code='002466'
#code='600650'
#code='300244'
#code='000001'
#code='300033'
code='000821'
short_num=20
long_num=55
dif_num=9
current_price=12.10
stock=Stockhistory(code,'D')
temp_df=stock._form_temp_df()
N=len(temp_df)
init_rate=-1.5
interval_rate=0.5
range_n=16
rate_list=[]
for i in range(0,range_n):
    rate=round(init_rate+i*interval_rate,1)
    rate_list.append(rate)
def change_static(rate_list,code,temp_df,column):
    gt_column=[]
    #gt_column=['code']
    gt_data={}
    #gt_data['code']=code
    for rate in rate_list:
        df=temp_df[temp_df[column]>rate]
        gt_rate_num=len(df)
        gt_rate=round(float(gt_rate_num)/N,2)
        column_name='gt_%s' % rate
        gt_data[column_name]=gt_rate
        gt_column.append(column_name)
    gt_static_df=pd.DataFrame(gt_data,columns=gt_column,index=[code])
    print 'static for %s:' % column
    print gt_static_df 
    return gt_static_df
change_static(rate_list, code, temp_df, column='h_change')
change_static(rate_list, code, temp_df, column='l_change')
change_static(rate_list, code, temp_df, column='p_change')