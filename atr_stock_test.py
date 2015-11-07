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
df=stock.get_atr_df(short_num, long_num)

