""""
#coding=utf-8
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os,sys,time

import tushare as ts
import json
import string

import urllib2
import datetime
from bs4 import BeautifulSoup

import threading

import smtplib
from email.mime.text import MIMEText
"""

from tradeStrategy import *

#last_day_str=get_last_trade_day()
#today_df,this_time_str=get_today_df()
last_day_str='2015-10-26'
today_df=pd.read_csv(ROOT_DIR+'/data/all%s.csv' % last_day_str)
print today_df
