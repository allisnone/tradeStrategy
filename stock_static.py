from tradeStrategy import *

code='002678'
#code='000987'
#code='601018'
#code='002466'
#code='600650'
code='000002'
short_num=12
long_num=26
dif_num=9
current_price=12.10
stock=Stockhistory(code,'D')
high_open_rate=3
stock.get_open_static(high_open_rate)