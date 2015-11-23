from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import functools

df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,30,20,40],'CCC' : [100,50,-30,-50]})
df=df.set_index('AAA')
print(df)
print(df.loc(4).BBB)
print(df.ix[0].AAA)
print(df.describe())
print(df[2:])
df.index.values



df.ix[df.AAA >= 5,'BBB'] = -1
df.ix[df.AAA >= 5,['BBB','CCC']] = 555

df.sort_index(axis=0, by='CCC', ascending=True)

df= df.set_index("AAA")

"""to keep the 'true', and replace the 'false'"""
df_mask = pd.DataFrame({'AAA' : [True] * 4, 'BBB' : [False] * 4,'CCC' : [True,False] * 2})
df.where(df_mask,-1000)

df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
df['logic'] = np.where(df['AAA'] > 5,'high','low')               #new column

dflow = df[df.AAA <= 5]
dfhigh = df[df.AAA > 5]


df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
len(df.index) 


newseries = df.loc[(df['BBB'] < 25) & (df['CCC'] >= -40), 'AAA']        #'loc' ---row,  &: 'and'
newseries = df.loc[(df['BBB'] > 25) | (df['CCC'] >= -40), 'AAA']        #|:'or'

df.loc[(df['BBB'] > 25) | (df['CCC'] >= 75), 'AAA'] = 0.1           #'=': return a df


df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
aValue = 43.0
df.ix[(df.CCC-aValue).abs().argsort()]              #return the previous df: sort by '(df.CCC-aValue).abs().argsort()'


df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
Crit1 = df.AAA <= 5.5
Crit2 = df.BBB == 10.0
Crit3 = df.CCC > -40.0
AllCrit = Crit1 & Crit2 & Crit3
df[AllCrit]

#or:
CritList = [Crit1,Crit2,Crit3]
AllCrit = functools.reduce(lambda x,y: x & y, CritList)
#http://docs.python.org/library/functools.html


#functools:
l=[1,2,3,4,5,6]
value=functools.reduce(lambda x,y:x+y,l)   #is:(((1+2)+3)+4)+5)+6
#value=21



df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
df[(df.AAA <= 6) & (df.index.isin([0,2,4]))]


data = {'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]}
df = pd.DataFrame(data=data,index=['foo','bar','boo','kar'])
"""row"""
df.loc['bar':'kar'] #Label
df.ix[0:3] #Same as .iloc[0:3]
df.ix['bar':'kar'] #Same as .loc['bar':'kar']

df2 = pd.DataFrame(data=data,index=[1,2,3,4]); #Note index starts at 1
df2.iloc[1:3] #Position-oriented
df2.iloc[1:2] #Position-oriented
df2.iloc[:,1:3] #Position-oriented
#row:2,3
df2.loc[1:3] #Label-oriented
#row: 1,2,3
df2.ix[1:3] #General, will mimic loc (label-oriented)
#row: 1,2,3
df2.ix[0:3] #General, will mimic iloc (position-oriented), as loc[0:3] would raise
#row: 1,2,3

"""to get the lest"""
df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
df[~((df.AAA <= 6) & (df.index.isin([0,2,4])))]



#New Columns
df = pd.DataFrame({'AAA' : [1,2,1,3], 'BBB' : [1,1,2,2], 'CCC' : [2,1,3,1]})
source_cols = df.columns # or some subset would work too.
new_cols = [str(x) + "_cat" for x in source_cols]
categories = {1 : 'Alpha', 2 : 'Beta', 3 : 'Charlie' }
df[new_cols] = df[source_cols].applymap(categories.get)


df = pd.DataFrame({'AAA' : [1,1,1,2,2,2,3,3], 'BBB' : [2,1,3,4,5,1,2,3]})
df.loc[df.groupby("AAA")["BBB"].idxmin()]



df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})

#average, 0-->column, 1-row
df.mean(0)
df.mean(1)

df.max(0)
df.max(1)

df['AAA'].idxmax()
df['AAA'].idxmin()

df.min(0)
df.min(1)

df.idxmin(0)
df.idxmax(0)

df.sum(0,skipna=False)
df.sum(1)

#wu pian biaozhun cha
df.std(0)
df.std(1)



df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
#insert

df.insert(1, 'DDD', df['CCC'])

del df['CCC']

df.drop('DDD', axis=1)

df.drop(['DDD','CCC'], axis=1)
p1=df.pop('BBB')
df.insert(2, 'BBB', p1)

df.dtypes
df['AAA'].astype(float)

t_df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
actual_101_list=[4,6]
df_101=t_df[t_df.index.isin(actual_101_list)]



df['time']=pd.to_datetime(df['time'])
ss=pd.Series(list(df['lastprint']),index=df['time'])
ss.resample('30Min','max')


df = pd.DataFrame({'AAA' : [4,5,6,7], 'BBB' : [10,20,30,40],'CCC' : [100,50,-30,-50]})
df.order('CCC')


import numba as nb

import pandas.io.sql as psql


from sqlalchemy import create_engine
engine = create_engine('mysql+mysqldb://user:passwd@localhost/schema')
df.to_sql('data', engine)
df.to_sql('data_chunked', engine, chunksize=1000)

pd.read_sql_table('data', engine)
pd.read_sql_table('data', engine, index_col='id')
pd.read_sql_table('data', engine, columns=['Col_1', 'Col_2'])

df.to_sql('table', engine, schema='other_schema')
pd.read_sql_table('table', engine, schema='other_schema')

pd.read_sql_query('SELECT * FROM data', engine)
pd.read_sql_query("SELECT id, Col_1, Col_2 FROM data WHERE id = 42;", engine)

for chunk in pd.read_sql_query("SELECT * FROM data_chunks", engine, chunksize=5):
    print(chunk)
    
    
from pandas.io import sql
sql.execute('SELECT * FROM table_name', engine)
sql.execute('INSERT INTO table_name VALUES(?, ?, ?)', engine, params=[('id', 1, 12.2, True)])