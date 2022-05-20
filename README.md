# Trading-assistant
Discretionary trading support app 

This application was developed in order to support crypto traders during their (primary) intraday trading session. After input parameters are specified by user, it simply prints out the probabilities whether the candle which has opened right now, will close above the opening price or below. Trader can combine this information with other techniques, like fundamental analysis or chart patterns.

After the app is opened, user has to specify following parameters:

* Data related parameters - time frame, crypto ticker, fiat ticker and lenght of initial time window on which model will be fitted
* Technical indicators by pressing those numbers which are printed before the name of indicator
* Classification model (three models available - logistic regression, random forest and gradient boosting)
  
After all parameters are specified, model is fitted on data. The independent data are technical indicators with one period lag and dependent one is binary pice close > price open. After the model is fitted, the app waits until the last candle closes, because if there passed too much time between candle opening and parameter specificaton, the information given by model is no longer relevant. After last pending candle closes and new one opens, the time of current candle and probabilities of opening long and short positions are printed. See screenshot below, how the app's interface looks like:

![image](https://user-images.githubusercontent.com/76043407/169515746-cb151be6-a482-431b-82cf-83b036d8361b.png)

The mechanics works as follows: after the parameters are specified, data in JSON format are downloaded from the cryptocompare API, and tranformed to the pandas data frame. Then the dependent variable is calculated and leaded. Next are calculated technical indicators - here is the space for adding as many indicators as user wants. This can be highly individual and user should backtest the performance of some models before. After tech indicators are calculated, model is fitted only on those indicators, which are specified by user. Finally, the infinite loop will start, where will be firstly tested, whether the last candle closes and new one opened. If so, the prediction is printed, new row of data are downloaded and last data are droped. Technicals are recalculated again. There are kept as many data as needed for the indicators calculation.   
