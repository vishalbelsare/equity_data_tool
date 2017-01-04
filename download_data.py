## Copyright Enzo Busseti 2016

from __future__ import print_function
import pandas as pd
import numpy as np
import datetime as dt
import quandl

assets=pd.read_csv('assets.txt').set_index('Symbol')

QUANDL={
    ## Get a key (free) from quandl.com and copy it here
    'authtoken':"",
    'start_date':dt.date(2007, 1, 1),
    'end_date':dt.date(2016, 12, 31)
}
RISK_FREE_SYMBOL = "USDOLLAR"

def data_query(asset):
    print('downloading %s from %s to %s' %(asset, QUANDL['start_date'], QUANDL['end_date']))
    return asset, quandl.get(assets.Quandlcode[asset], **QUANDL)

# download assets' data
data=list(map(data_query, assets.index))

def select_first_valid_column(df, columns):
    for column in columns:
        if column in df.columns:
            return df[column]

# extract prices
prices=pd.DataFrame.from_items([(k,select_first_valid_column(v, ["Adj. Close", "Close", "VALUE"])) for k,v in data])

#compute sigmas
high=pd.DataFrame.from_items([(k,select_first_valid_column(v, ["High"])) for k,v in data])
low=pd.DataFrame.from_items([(k,select_first_valid_column(v, ["Low"])) for k,v in data])
sigmas = (high-low) / (2*high)

# extract volumes
volumes=pd.DataFrame.from_items([(k,select_first_valid_column(v, ["Adj. Volume", "Volume"])) for k,v in data])

# fix risk free
prices[RISK_FREE_SYMBOL]=10000*(1 + prices[RISK_FREE_SYMBOL]/(100*250)).cumprod()



# filter NaNs - threshold at 2% missing values
bad_assets = prices.columns[prices.isnull().sum()>len(prices)*0.02]
if len(bad_assets):
    raise Exception('Assets %s have too many NaNs' % bad_assets)

# days on which many assets have missing values
bad_days1=sigmas.index[sigmas.isnull().sum(1) > 10]
bad_days2=prices.index[prices.isnull().sum(1) > 10]
bad_days3=volumes.index[volumes.isnull().sum(1) > 3]
bad_days=pd.Index(set(bad_days1).union(set(bad_days2)).union(set(bad_days3))).sort_values()
print ("Removing these days from dataset:")
print(pd.DataFrame({'nan price':prices.isnull().sum(1)[bad_days],
                    'nan volumes':volumes.isnull().sum(1)[bad_days],
                    'nan sigmas':sigmas.isnull().sum(1)[bad_days]}))

prices=prices.loc[~prices.index.isin(bad_days)]
sigmas=sigmas.loc[~sigmas.index.isin(bad_days)]
volumes=volumes.loc[~volumes.index.isin(bad_days)]

# extra filtering
print(pd.DataFrame({'remaining nan price':prices.isnull().sum(),
                    'remaining nan volumes':volumes.isnull().sum(),
                    'remaining nan sigmas':sigmas.isnull().sum()}))
prices=prices.fillna(method='ffill')
prices=prices.fillna(method='bfill')
sigmas=sigmas.fillna(method='ffill')
sigmas=sigmas.fillna(method='bfill')
volumes=volumes.fillna(method='ffill')

# make volumes in dollars
volumes = volumes*prices

# compute returns
returns = (prices.diff()/prices.shift(1)).fillna(method='ffill').ix[1:]
bad_assets = returns.columns[((-.5>returns).sum()>0)|((returns > 2.).sum()>0)]
if len(bad_assets):
    raise Exception('Assets %s have dubious returns' % bad_assets)

# save data
prices.to_csv('prices.txt', float_format='%.3f')
volumes.to_csv('volumes.txt', float_format='%d')
returns.to_csv('returns.txt', float_format='%.3e')
sigmas.to_csv('sigmas.txt', float_format='%.3e')
