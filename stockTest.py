from tradeStrategy import *
"""
code='002678'
#code='000987'
#code='601018'
#code='002466'
code='600650'
stock=Stockhistory(code,'D')
start_time = datetime.datetime.now()
temp_df=stock.get_trade_df()

print temp_df

end_time = datetime.datetime.now()

delta_second=get_delta_seconds(start_time, end_time)
print 'delta_second=',delta_second
#sp500[['close', '5d', '10d']].plot(grid=True, figsize=(8, 5))
#temp_df=stock._form_temp_df()
"""
stronge_ma_3_list=[]
start_time = datetime.datetime.now()
today_df,this_time_str=get_today_df()
gt5_df=today_df[today_df['changepercent']>3.0]
#print today_df
ma_type='ma5'
ma_offset=0.01
great_score=4
great_change=5.0
all_codes=gt5_df.index.values.tolist()
print len(all_codes)
all_codes=['002678']
#all_codes=['002542']


stronge_ma5_list= ['600368', '002341', '300234', '000802', '300358', '300130', '002407', '300065', '300306', '603308', '300004', '300208', '002581', '300016', '300291', '603085', '603616', '002640', '002642', '300295', '600576', '300376', '300451', '000681', '002329', '002488', '300226', '300252', '300392', '002366', '000801', '600391', '002373', '002690', '300308', '300318', '002184', '300075', '600339', '002227', '300001', '300147', '002284', '600865', '300370', '300373', '000099', '600536', '002213', '300083', '002489', '300324', '600038', '300465', '300013', '601002', '002518', '300462', '300468', '000768', '300248', '002658', '002232', '300049', '002145', '002063', '300136', '002584', '300378', '002280', '300044', '002169', '600728', '300034', '600783', '002460', '300223', '002579', '300074', '300219', '300041', '002659', '300036', '000559', '000721', '300174', '300139', '000070', '600055', '002197', '300077', '300292', '600271', '300183', '300206', '300253', '002261', '300293', '300055', '300386', '002104', '002120', '300068', '300481', '300415', '601311', '300235', '002037', '300007', '600850', '002711', '600260', '002108', '002065', '300395', '002215', '002077', '000777', '000159', '300259', '000158', '600203', '002713', '002089', '002139', '300307', '300374', '600584', '300061', '603019', '002649', '300435', '300477', '002017', '002389', '300100', '002130', '002182', '002163', '603969', '300195', '002398', '300141', '603799', '002291', '000733', '002708', '600198', '002350', '601633', '300038', '300437', '002421', '000524', '002517', '002623', '000915', '300449', '300440', '300302', '300240', '300231', '600363', '300050', '000880', '000920', '002501', '300202', '300447', '002498', '300014', '300073', '300229', '002396', '300037', '300172', '002195', '000925', '300047', '300381', '002189', '002087', '300455', '300400', '601011', '002660', '300053', '300389', '000026', '300175', '002466', '002618', '300372', '300344', '002056', '603678', '601636', '300379', '600063', '002312', '300022', '000551', '300315', '300203', '002050', '603015', '002101', '603918', '002161', '000410', '000616', '600335', '000973', '002171', '002160', '603606', '002696', '600836', '300342', '002504', '601908', '600249', '002192', '000409', '300156', '600375', '002634', '600330', '002297', '000546', '600390', '600149', '000985', '300224', '300237', '002296', '000090', '002540', '000544', '002187', '300200', '600678', '600596', '300330', '002469', '000811', '002243', '600152', '300402', '600328', '300201', '600833', '300032', '002735', '002692', '000055', '000020', '600288', '600161', '000837', '603636', '002725', '002074', '000962', '000045', '002200', '603100', '002679', '600386', '600581', '000009', '300448', '600701', '002495', '002583', '002185', '600618', '300097', '000710', '600366']
stronge_ma5_df=today_df[today_df.index.isin(stronge_ma5_list)]
this_mean=stronge_ma5_df['changepercent'].mean()

#all_codes= ['300113', '300193', '002270', '002573', '300367', '002771', '603001', '002480', '002254', '002355', '300017', '600348', '603368', '603456', '002332', '002675', '600761', '000531', '600197', '600740', '000848', '000639', '002644', '002737', '603699', '000916', '600694', '601558', '300359', '002775', '600688', '600020', '002356', '000935', '002508', '600351', '600219', '600007', '002393', '002653', '600600', '600207']
last_stronge_ma5_df=today_df[today_df.index.isin(all_codes)]
last_mean=last_stronge_ma5_df['changepercent'].mean()

print 'this_mean=%s, last_mean=%s' % (this_mean,last_mean)

data={}
result_column=['code','l_s_date','l_s_state','t_s_date','t_s_state','t_date','t_state','score','oper3']
result_df=pd.DataFrame(data,columns=result_column)
if all_codes:
    for code_str in all_codes:
        stock=Stockhistory(code_str,'D')
        code_data=stock.get_trade_df(ma_type,ma_offset,great_score,great_change)
        if code_data:
            code_df=pd.DataFrame(code_data,index=['code'],columns=result_column)
            result_df=result_df.append(code_df,ignore_index=True)
            if code_data['oper3'] ==3:
                stronge_ma_3_list.append(code_str)

if stronge_ma_3_list:
    print 'stronge_ma5_list=',stronge_ma_3_list
    stronge_ma5_df=today_df[today_df.index.isin(stronge_ma_3_list)]
    print stronge_ma5_df
print 'result_df:'
result_df=result_df.sort_index(axis=0, by='oper3', ascending=False)
print result_df

result_df_score_gt0=result_df[result_df['score']>=0]
print result_df_score_gt0
result_df_oper3_gt1=result_df[result_df['oper3']>=1]
print result_df_oper3_gt1

result_df.to_csv(ROOT_DIR+'/result/score_ma10.csv')
end_time = datetime.datetime.now()
delta_second=get_delta_seconds(start_time, end_time)/len(all_codes)



#stronge_ma5_list_20150918= ['300113', '300193', '002270', '002573', '300367', '002771', '603001', '002480', '002254', '002355', '300017', '600348', '603368', '603456', '002332', '002675', '600761', '000531', '600197', '600740', '000848', '000639', '002644', '002737', '603699', '000916', '600694', '601558', '300359', '002775', '600688', '600020', '002356', '000935', '002508', '600351', '600219', '600007', '002393', '002653', '600600', '600207']

print 'delta_second=',delta_second