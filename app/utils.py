from django.utils.timezone import make_aware

from .models import Coin
from core.settings import CORE_DIR

from datetime import datetime
import requests, io
import csv
import urllib
import chardet

CURRENCIES = 'bitcoin%2Cethereum%2Ccardano%2Cbinancecoin'

def get_symbol(name):
 #   data_url = 'https://api.coingecko.com/api/v3/coins/{}/tickers'.format(name)
 #   symbol = requests.get(data_url).json()
 #   print(symbol)
 #   return symbol
    return name


def get_live_prices():
    coins = []

    # Price request every 5 seconds
 #   threading.Timer(2, get_live_prices).start()

    # Get current closing value for all currencies
    data_url = 'https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd'.format(CURRENCIES)
    price_dict = requests.get(data_url).json()
    for item in price_dict:
        #print(list(price_dict[item].values()))
        price = list(price_dict[item].values())
        close_input = float(price[0])
        namelc = item
        if (item=='bitcoin'): cs = 'BTC'
        elif (item=='ethereum'): cs = 'ETH'
        elif (item=='cardano'): cs = 'ADA'
        elif (item=='binancecoin'): 
            cs = 'BNB' 
            namelc = 'binance-coin'
        coin = Coin(name=item.title(), symbol=cs, name_lc = namelc, symbol_lc = cs.lower(), cur_val=close_input)
        coins.append(coin)

    return coins


def get_holdings(input):
    holdings = []
    url = 'https://raw.githubusercontent.com/HakunaKp/historical_data/main/ETH/' + input
    response = urllib.request.urlopen(url)
    content_bytes = response.read()
    content_string = content_bytes.decode(encoding='utf-8')
    data = io.StringIO(content_string)
    mycsv = csv.reader(data)
    for row in mycsv:
        holdings.append(row)
    response.close()
    return holdings
#    with open(path, encoding='utf-8') as f:
#        print(f)
#        reader = csv.reader(f)
#        for row in reader:
#            holdings.append(row)

def parse_unix(unix):

    if (type(unix) == str):
        temp = int(unix)
        unix = temp
    
    datetime_obj = datetime.fromtimestamp(unix)
    aware_datetime = make_aware(datetime_obj)

    return aware_datetime


# function to update, store, and return moving average gain and loss
def get_average_change(period, average_changes, cur_change, timeframe):

    # calculate initial (0) average gain
    if (len(average_changes) == 0):
        sum_num = 0
        for t in period:
            sum_num = sum_num + float(t)           

        # save value of previous average gain for next step
        cur_avg_change = sum_num / len(period)

    # calculate rest (1 - Nth) of average gains
    else:
        # Emphasis on recent values
        length = len(average_changes)
        prev_avg_change = average_changes[length-1]
        cur_avg_change = ((prev_avg_change * (timeframe - 1)) + cur_change) / timeframe

    average_changes.append(cur_avg_change)
    return cur_avg_change


def bt_rsi_strategy(start, end, timeframe, frequency, begin_balance, interval, overbought_threshold, oversold_threshold):    

    TIME_FRAME = timeframe
    FREQUENCY = frequency
    START = start
    END = end
    OVERBOUGHT_THRESHOLD = overbought_threshold
    OVERSOLD_THRESHOLD = oversold_threshold
    BEGIN_BALANCE = begin_balance

    # max size the array can be for one period (fixed value for max of len(CUR_PERIOD))
    MAX_PERIOD_SIZE = (TIME_FRAME * 24 * 60 * 60) / FREQUENCY

    # list of rsi, time, and closing values
    RSI = []
    TIME = []
    CLOSING = []

    # list of closing vals in current period
    CUR_PERIOD = []

    # average changes
    AVG_GAINS = []
    AVG_LOSSES = []

    if (interval == 'One Minute'):
        INPUT_DATA = 'ETHUSD_1.csv'
    elif (interval == 'Five Minute'):
        INPUT_DATA = 'ETHUSD_5.csv'
    elif (interval == 'Fifteen Minute'):
        INPUT_DATA = 'ETHUSD_15.csv'
    elif (interval == 'One Hour'):
        INPUT_DATA = 'ETHUSD_60.csv'
    elif (interval == 'Half Day'):
        INPUT_DATA = 'ETHUSD_720.csv'
    elif (interval == 'One Day'):
        INPUT_DATA = 'ETHUSD_1440.csv'

    holdings = get_holdings(INPUT_DATA)
    for i in range(1, len(holdings)):

        prev_unix = (holdings[i-1][0])
        unix = (holdings[i][0])

        # check if data entry in testing range and in sequential order
        if prev_unix > START and unix < END and prev_unix < unix:

            prev_close = float(holdings[i-1][4])
            close = float(holdings[i][4])

            length = len(CUR_PERIOD)
            
            # first timeframe period has not ended
            if length < MAX_PERIOD_SIZE:
                # get price change from most recent item
                if length >= 1:
                    prev_close = CUR_PERIOD[length-1]
                    CHANGE = float(close) - float(prev_close)
                CUR_PERIOD.append(close)
                rsi = 'NA'

            else:

                # get price change from most recent/latest item
                prev_close = CUR_PERIOD[length-1]
                CHANGE = float(close) - float(prev_close)
                # maintain price data size with moving period
                CUR_PERIOD.pop(0)
                CUR_PERIOD.append(close)
                
                if (CHANGE > 0):
                    # get current moving average gain and loss
                    avg_gain = get_average_change(CUR_PERIOD, AVG_GAINS, CHANGE, TIME_FRAME)
                    avg_loss = get_average_change(CUR_PERIOD, AVG_LOSSES, 0, TIME_FRAME)

                elif (CHANGE == 0):
                    # get current moving average gain and loss
                    avg_gain = get_average_change(CUR_PERIOD, AVG_GAINS, 0, TIME_FRAME)
                    avg_loss = get_average_change(CUR_PERIOD, AVG_LOSSES, 0, TIME_FRAME)

                elif (CHANGE < 0):
                    # get current moving average gain and loss
                    avg_gain = get_average_change(CUR_PERIOD, AVG_GAINS, 0, TIME_FRAME)
                    avg_loss = get_average_change(CUR_PERIOD, AVG_LOSSES, abs(CHANGE), TIME_FRAME)

                # calculate current rsi
                rs = avg_gain / avg_loss
                rsi = (100 - (100 / (1 + rs)))

                # add moving averages to our lists for next iteration
                AVG_GAINS.append(avg_gain)
                AVG_LOSSES.append(avg_loss)

            # format time
            t = datetime.fromtimestamp(int(unix))
            day = t.strftime("%Y-%m-%d %H:%M:%S")

            # add to our TIME, CLOSING, RSI lists
            RSI.append(rsi)
            TIME.append(day)
            CLOSING.append(close)

    # format start time
    start_t = datetime.fromtimestamp(int(START))
    start_day = start_t.strftime("%Y-%m-%d %H:%M:%S")

    # format end time
    end_t = datetime.fromtimestamp(int(END))
    end_day = end_t.strftime("%Y-%m-%d %H:%M:%S")

    results_dictionary = {'start': str(start_day), 'end': str(end_day), 'strategy_name': 'RSI Strategy', 'interval': interval, 'timeframe': TIME_FRAME, 
        'frequency': FREQUENCY, 'begin_balance': BEGIN_BALANCE, 'end_balance': 1000000000, 'overbought_threshold': OVERBOUGHT_THRESHOLD, 
        'oversold_threshold': OVERSOLD_THRESHOLD, 'rsi': RSI, 'time': TIME, 'closing': CLOSING}

    return results_dictionary
