from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import backtrader as bt
#import backtrader.feeds as btfeeds

import pandas

"""
# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
"""
class TestStrategy(bt.Strategy):
    """
    params = (
        ('stake', 4000),
        ('exitbars', 4),
    )
    """
    params = (
        ('s_maperiod', 5),
        ('l_maperiod', 10),
        ('stake', 100),
        ('exit_point',1.0),
        ('buy_point_atr',1),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        
        # Set the sizer stake from the params
        self.sizer.setsizing(self.params.stake)

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # Add a MovingAverageSimple indicator
        self.s_sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.s_maperiod)
        self.l_sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.l_maperiod)
        self.atr=bt.indicators.ATR(self.datas[0])
        # Indicators for the plotting show
        self.highest=bt.indicators.Highest(self.datas[0],period=20)
        self.lowest=bt.indicators.Lowest(self.datas[0],period=20)
        #self.highest=bt.indicators.Highest(self.datahigh,period=20)
        #self.lowest=bt.indicators.Lowest(self.datalow,period=20)
        """
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        """
        #bt.indicators.ATR(self.datas[0], subplot=True)#plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        self.log('High, %.2f' % self.datahigh[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            """
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > 1.01*self.dataclose[-1]: #and self.dataclose[0] > 1.03*self.dataclose[-1]:
                    # current close less than previous close

                    if self.dataclose[-1] > 1.01*self.dataclose[-2]:
            """
            if self.datahigh[0] > self.highest[0]:
                        # previous close less than the previous close

                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])
                        self.log('atr of BUY point, %.2f' % self.atr[0])
                        self.params.exit_point=self.dataclose[0]-2.0*self.atr[0]
                        self.params.buy_point_atr=self.atr[0]

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()

        else:

            # Already in the market ... we might sell
            #if len(self) >= (self.bar_executed +  self.params.exitbars):
            #if self.datalow[0] < self.lowest[0] or  self.dataclose[0] < self.params.exit_point:
            if self.datalow[0] < self.lowest[0] or  self.dataclose[0] <(self.datahigh[0]-1.0*self.params.buy_point_atr):#self.dataclose[0] < self.l_sma[0]
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
def runstrat():
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Get a pandas dataframe
    datapath = ('E:/work/stockAnalyze/update/002678.csv')

    # Simulate the header row isn't there if noheaders requested
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0
    column_list=['Date','Open','High','Low','Close','Volume']
    dataframe = pandas.read_csv(datapath,
                                skiprows=skiprows,
                                header=header,
                                parse_dates=True,
                                index_col=0,
                                names=column_list)
    #dataframe.index.name='date'
    
    if not args.noprint:
        print('--------------------------------------------------')
        print(dataframe)
        print('--------------------------------------------------')
    
    dataframe[str('Openinterest')]=0.0
    print ("dataframe with openinterest column:")
    print(dataframe)

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)
   

    cerebro.adddata(data)
    
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.0025)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())


    # Run over everything
    cerebro.run()
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    cerebro.plot(style='bar')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()