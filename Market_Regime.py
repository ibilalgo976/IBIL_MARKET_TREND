import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import talib as ta
import streamlit as st
from scipy.signal import argrelextrema



#st.write("Hello ,let's learn how to build a streamlit app together")

st.title ("Market Regime")
#st.header("this is the markdown")
#st.markdown("this is the header")
#st.subheader("this is the subheader")
#st.caption("this is the caption")
#st.code("x=2021")
#st.latex(r''' a+a r^1+a r^2+a r^3 ''')





ticker = '^VIX'
MACD_FAST = 10
MACD_SLOW = 30
MACD_SIGNAL = 5
Y_AXIS_SIZE = 16
df1 = yf.download(ticker,start='2021-01-01',progress=False)
df1['macd'], df1['macdSignal'], df1['macdHist'] = ta.MACD(df1['Close'], fastperiod=MACD_FAST, slowperiod=MACD_SLOW, signalperiod=MACD_SIGNAL)

st.subheader("VIX")
st.write(df1)

# Prepare plot
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(16,9), gridspec_kw={'height_ratios': [2, 1]})
ax1.set_ylabel(ticker, size=20)

#size plot
#fig.set_size_inches(16,9)

# Plot candles
#candlestick(ax1, df1, width=0.5, colorup='g', colordown='r', alpha=1)
df1.Close.plot(ax=ax1, color='b', label='^VIX')

# Draw MACD computed with ta
ax2.set_ylabel('MACD: '+ str(MACD_FAST) + ', ' + str(MACD_SLOW) + ', ' + str(MACD_SIGNAL), size=Y_AXIS_SIZE)
df1.macd.plot(ax=ax2, color='b', label='Macd')
df1.macdSignal.plot(ax=ax2, color='g', label='Signal')
df1.macdHist.plot(ax=ax2, color='r', label='Hist')
ax2.axhline(0, lw=2, color='0')
handles, labels = ax2.get_legend_handles_labels()
ax2.legend(handles, labels)

st.pyplot(fig)



st.subheader("SPY")
df = yf.download('SPY',period='2y',progress=False,auto_adjust=True)
#df = yf.download('SPY',start='2021-01-01',progress=False)
#df_yahoo = yf.download('FB',start='2020-09-15',end='2020-11-15',progress=False,auto_adjust=True,actions="inline")
df['Prev Close'] = df['Close'].shift(1)   
df['MA200'] = ta.MA(df['Close'], timeperiod=200)
df['MA50'] = ta.MA(df['Close'], timeperiod=50)
df['ATR'] = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
df['ADX'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
df['WILLR3'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=3)
df['WILLR10'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=10)
df['WILLR30'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=30)
df['WILLR90'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=90)
df['WILLR270'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=270)
df['VIX Close'] = df1['Close']
df['VIX Prev Close'] = df1['Close'].shift(1)
df['VIX MACD'] = df1['macd']

df['Market Trend Signal'] = (df['Close'] - df['MA200']) / df['ATR']
df['Market Trend'] = 'SIDE'
df.loc[df['Market Trend Signal'] >  2,'Market Trend'] = 'BULL'
df.loc[df['Market Trend Signal'] < -2,'Market Trend'] = 'BEAR'

df['MID Market Trend Signal'] = (df['Close'] - df['MA50']) / df['ATR']
df['MID Market Trend'] = 'SIDE'
df.loc[df['MID Market Trend Signal'] >  1,'MID Market Trend'] = 'BULL'
df.loc[df['MID Market Trend Signal'] < -1,'MID Market Trend'] = 'BEAR'

df['MID MKT STRENGTH Signal'] = df['ADX']
df['MID MKT STRENGTH'] = 'NORMAL'
df.loc[df['MID MKT STRENGTH Signal'] > 25,'MID MKT STRENGTH'] = 'STRONG'
df.loc[df['MID MKT STRENGTH Signal'] < 15,'MID MKT STRENGTH'] = 'WEAK'

df['MKT VOLATILTY Signal'] =  df['ATR'] / df['Close']
df['BB3100Z1UP'], df['BB100Z1MID'], df['BB100Z1LO'] = ta.BBANDS(df['MKT VOLATILTY Signal'], timeperiod=100, nbdevup=1, nbdevdn=1, matype=0)
df['MKT VOLATILTY'] = 'NORMAL'
df.loc[df['MKT VOLATILTY Signal'] > df['BB3100Z1UP'],'MKT VOLATILTY'] = 'HIGH'
df.loc[df['MKT VOLATILTY Signal'] < df['BB100Z1LO'] ,'MKT VOLATILTY'] = 'LOW'

df['MKT RISK Signal'] =  (df['VIX MACD'] < 0) * 1.0
df['MKT RISK'] = 'OFF'
df.loc[df['MKT RISK Signal'] == 1,'MKT RISK'] = 'ON'

df = df.dropna()

st.write(df)



# Plot
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True, figsize=(16,9), gridspec_kw={'height_ratios': [4, 1, 1, 1]})

ax1.set_ylabel('SPY', size=20)
ax1.plot(df['Close'], color='b', label='Close')
ax1.legend(loc="upper left")
ax1.plot(df['MA200'], color='r', label='MA200')
ax1.legend(loc="upper left")
ax1.plot(df['MA50'], color='g', label='MA50')
ax1.legend(loc="upper left")
ax2.set_ylabel('ATR 14', size=10)
ax2.plot(df['ATR'], color='b')
ax3.set_ylabel('ADX 14', size=10)
ax3.plot(df['ADX'], color='b')
ax4.set_ylabel('WILLR 3', size=10)
ax4.plot(df['WILLR3'], color='b')


#plt.rcParams["figure.figsize"] = [16, 9]
plt.rcParams["figure.autolayout"] = False

st.pyplot(fig)




bull = df.copy()
side = df.copy()
bear = df.copy()

bull[df['Market Trend'] != 'BULL'] = np.nan
side[df['Market Trend'] != 'SIDE'] = np.nan
bear[df['Market Trend'] != 'BEAR'] = np.nan

side.reset_index(inplace = True)
bull_x = bull['Close']
side_x = side['Close']
bear_x = bear['Close']
y = side['Date']

#plotting
fig = plt.figure(figsize=(16,9))
#plt.plot(bull['Close'], c='g')
plt.title('SPY 1d Market Regime',size=20)
plt.plot(df['Close'], c='b')
plt.plot(y,bull_x, label='BULL', c='g')
plt.plot(y,side_x, label='SIDE', c='b')
plt.plot(y,bear_x, label='BEAR', c='r')
plt.legend(loc="upper left")
#y
st.pyplot(fig)




bull = df.copy()
side = df.copy()
bear = df.copy()

bull[df['MID Market Trend'] != 'BULL'] = np.nan
side[df['MID Market Trend'] != 'SIDE'] = np.nan
bear[df['MID Market Trend'] != 'BEAR'] = np.nan

side.reset_index(inplace = True)
bull_x = bull['Close']
side_x = side['Close']
bear_x = bear['Close']
y = side['Date']

#plotting
fig = plt.figure(figsize=(16,9))
#plt.plot(bull['Close'], c='g')
plt.title('SPY 1d Mid Market Regime',size=20)
plt.plot(df['Close'], c='b')
plt.plot(y,bull_x, label='BULL', c='g')
plt.plot(y,side_x, label='SIDE', c='b')
plt.plot(y,bear_x, label='BEAR', c='r')
plt.legend(loc="upper left")
#y
st.pyplot(fig)





