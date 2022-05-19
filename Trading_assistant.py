import pandas as pd
import requests as requests
import ta as ta
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import datetime as datetime

models = [LogisticRegression(),RandomForestClassifier(), GradientBoostingClassifier()] #create list of models

parameters = input("Select period, coin, fiat and time window (separated by space): ") #let user defined parameters in web scraping function
params = parameters.split() #create a list of input parameters

print("Press numbers corresponding to indicators you want to use (separate numbers by space):")
print("1:RSI")
print("2:EMA(8)")
print("3:EMA(14)")
print("4:EMA(20)")
print("5:EMA(34)")
print("6:PPO")
print("7:KAMA")
print("8:TSI")
print("9:William's R")
indicators = input() #let user choose the indicators. Here is space for adding as many indicators as desired

ind = indicators.split() #create a list of numbers that correspond to different indicators
ind_int = [int(i)+4 for i in ind] #make a list of numbers that correspond to different indicators and add 4 to each, in order to right subseting

print("Press number corresponding to model you want to use:")
print("1:Logistic regression")
print("2:Random forest")
print("3:Gradient boosting")
model = input()#let user choose the model
mod_selected = models[int(model)-1]#select the model from models list

def get_price(period,coin,fiat,limit):
    url = "https://min-api.cryptocompare.com/data/v2/histo"+period+"?fsym="+coin+"&tsym="+fiat+"&limit="+str(limit)
    req = requests.get(url).json()
    OHLC = [req["Data"]["Data"][1]["open"],req["Data"]["Data"][1]["high"],req["Data"]["Data"][1]["low"],req["Data"]["Data"][1]["close"]]
    return OHLC #function that scraps the historical data and return open, high, low, close format

def get_data(period,coin,fiat,limit):
    url = "https://min-api.cryptocompare.com/data/v2/histo" + period + "?fsym=" + coin + "&tsym=" + fiat + "&limit=" + str(limit)
    req = requests.get(url).json()

    s = pd.DataFrame({"o":[0],"h":[0],"l":[0],"c":[0]})#single row df which will be always filled by different values and concatenated to main df
    df = pd.DataFrame({"o":[0],"h":[0],"l":[0],"c":[0]}) #main df

    for i in req["Data"]["Data"]: #loop throught data in JSON format and subset desired values
        s["o"] = i["open"]
        s["h"] =  i["high"]
        s["l"] = i["low"]
        s["c"] = i["close"]
        df = pd.concat([df,s],axis=0) #create dataframe from scraped data with open, high, low, close in columns
    df = df.iloc[1:,:]
    lab = [1 if i >= j else 0 for i,j in zip(df["c"],df["o"])] + ["x"] #create dependent variable as close - open and shift it
    df["lab"] = lab[1:]
    return df

d = get_data(params[0],params[1],params[2],(int(params[3])+50)) #get data with user specified parameters

d["RSI"] = ta.momentum.RSIIndicator(d["c"],window=14).rsi()
d["EMA_8"] = ta.trend.EMAIndicator(d["c"], window = 8).ema_indicator().pct_change()
d["EMA_14"] = ta.trend.EMAIndicator(d["c"], window = 14).ema_indicator().pct_change()
d["EMA_20"] = ta.trend.EMAIndicator(d["c"], window=20).ema_indicator().pct_change()
d["EMA_34"] = ta.trend.EMAIndicator(d["c"], window=34).ema_indicator().pct_change()
d["ppo"] = ta.momentum.PercentagePriceOscillator(d["c"]).ppo()
d["kama"] = ta.momentum.KAMAIndicator(d["c"]).kama()
d["tsi"] = ta.momentum.TSIIndicator(d["c"]).tsi()
d["willR"] = ta.momentum.WilliamsRIndicator(d["h"],d["l"],d["c"]).williams_r()#add all indicators.Possible to add as many as desired

print("fitting the model...")
mod_selected.fit(d.iloc[50:(len(d.index)-1),ind_int],d.iloc[50:(len(d.index)-1),4].astype('int')) #fit selected model on selected indicators
print("model fitted")
d = d.iloc[(int(params[3])-50):,:5] #choose last values neccessary for recalculating the indicators

a = []
ss = pd.DataFrame({"o":[0],"h":[0],"l":[0],"c":[0],"lab":["x"]})

print("Waiting for the last candle to close...")
while True:
    a.append(datetime.datetime.now().minute)
    if len(a) == 1:
        pass #if the loop just start, do not predict the next value (minimize the volatility the last candle makes when the prediction is printed)
    else:
        if a[1] == a[0]: #when candle has not closed, no precition will be made. Original value in list a is replaced by new time value.
            a = [a[1]]
        else:
            a = [a[1]]#replace last timestamp with new one
            k = get_price(params[0],params[1],params[2], 1)#get single row of open high low close data
            if k[3] >= k[0]:
                d.iloc[-1,4] = 1
            else:
                d.iloc[-1, 4] = 0 #replace x in last row of dependent variable by observed

            ss["o"] = k[0]
            ss["h"] = k[1]
            ss["l"] = k[2]
            ss["c"] = k[3] #get data to df which will be concatenated to main df

            d = pd.concat([d,ss],axis=0) #concat DFs
            d = d.iloc[1:,:] #drop first value (so the lenght is kept the same)

            d["RSI"] = ta.momentum.RSIIndicator(d["c"], window=14).rsi().pct_change()
            d["EMA_8"] = ta.trend.EMAIndicator(d["c"], window=8).ema_indicator().pct_change()
            d["EMA_14"] = ta.trend.EMAIndicator(d["c"], window=14).ema_indicator().pct_change()
            d["EMA_20"] = ta.trend.EMAIndicator(d["c"], window=20).ema_indicator().pct_change()
            d["EMA_34"] = ta.trend.EMAIndicator(d["c"], window=34).ema_indicator().pct_change()
            d["ppo"] = ta.momentum.PercentagePriceOscillator(d["c"]).ppo()
            d["kama"] = ta.momentum.KAMAIndicator(d["c"]).kama()
            d["tsi"] = ta.momentum.TSIIndicator(d["c"]).tsi()
            d["willR"] = ta.momentum.WilliamsRIndicator(d["h"], d["l"], d["c"]).williams_r() #recalculate indicators

            p = mod_selected.predict_proba(d.iloc[[-2,-1],ind_int].astype('int'))#predict the probability of close>open of the candle which opened right now
            print(str(datetime.datetime.now())+" - ", "short: ", p[1][0],"," ,"long: ", p[1][1])#print timestamp and probablities for short and long position
            d = d.iloc[:,0:5] #clean main DF from indicators, so they can be recalculated with new data next iteration


