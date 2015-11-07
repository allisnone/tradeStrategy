from tradeStrategy import *
static_df_p,static_df_h,static_df_l=change_static_market()
close_change_df=static_df_p.describe()
high_change_df=static_df_h.describe()
low_change_df=static_df_l.describe()

print 'Static calculation completed, see more in DIR:' + ROOT_DIR+'/result_temp/'