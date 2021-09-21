# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template

from core.settings import CORE_DIR

from .models import BT_RSI_Strategy
from .utils import parse_unix, bt_rsi_strategy
from .utils import get_live_prices, CURRENCIES

import decimal
import json
import time
from datetime import datetime
import urllib.request
import pdb

@login_required(login_url="/login/")
def index(request):
    
    context = {}
    context['segment'] = 'index'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def dashboard(request):

    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.

    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template

        if (load_template == 'dashboard.html'):

            savechanges= request.POST.get('Save Changes')
            if savechanges:

                # strings that require parsing
                temp_start = request.POST.get('start')
                temp_end = request.POST.get('end')
                temp_timeframe = request.POST.get('timeframe')
                temp_frequency = request.POST.get('frequency')
                temp_begin_balance = request.POST.get('begin_balance')
                temp_overbought_threshold = request.POST.get('overbought_threshold')
                temp_oversold_threshold = request.POST.get('oversold_threshold')
                temp_interval = request.POST.get('interval')

                dt = datetime.strptime(temp_start, "%Y/%m/%d %H:%M")
                temp_start = str(int(time.mktime(dt.timetuple())))
                dt = datetime.strptime(temp_end, "%Y/%m/%d %H:%M")
                temp_end = str(int(time.mktime(dt.timetuple())))

                timeframe = int(temp_timeframe)
                frequency = int(temp_frequency)
                begin_balance = round(decimal.Decimal(temp_begin_balance), 2)
                overbought_threshold = round(decimal.Decimal(temp_overbought_threshold),2)
                oversold_threshold = round(decimal.Decimal(temp_oversold_threshold), 2)

                # calculate results
                results_dictionary = bt_rsi_strategy(temp_start, temp_end, timeframe, frequency, float(begin_balance), temp_interval, float(overbought_threshold), float(oversold_threshold))

                start = parse_unix(temp_start)
                end = parse_unix(temp_end)

                strat = BT_RSI_Strategy(strategy_name='Backtest RSI Strategy', end_balance=100.00, start=start, end=end, interval=temp_interval, timeframe=timeframe, frequency=frequency, begin_balance=1000, overbought_threshold=overbought_threshold, oversold_threshold=oversold_threshold)
                strat.save()
                strategies = BT_RSI_Strategy.objects.filter(id=strat.id)

                context['strategies'] = strategies           
                context['rsi_results'] = ("rsi", results_dictionary["rsi"])
                context['time_results'] = ("time", results_dictionary["time"])
                context['closing_results'] = ("closing", results_dictionary["closing"])

            else:
                with urllib.request.urlopen("https://raw.githubusercontent.com/HakunaKp/historical_data/main/backtest_results.json") as url:
                    backtest_results = json.loads(url.read().decode())

                temp_start = backtest_results["start"]
                dt = datetime.strptime(temp_start, "%Y-%m-%d %H:%M:%S")
                temp_start = str(int(time.mktime(dt.timetuple())))

                temp_end = backtest_results["end"]
                dt = datetime.strptime(temp_end, "%Y-%m-%d %H:%M:%S")
                temp_end = str(int(time.mktime(dt.timetuple())))

                strat = BT_RSI_Strategy(strategy_name='Backtest RSI Strategy', end_balance=10000, start=parse_unix(temp_start), end=parse_unix(temp_end), interval=backtest_results["interval"], timeframe=backtest_results["timeframe"], frequency=backtest_results["frequency"], begin_balance=backtest_results["begin_balance"], overbought_threshold=backtest_results["overbought_threshold"], oversold_threshold=backtest_results["oversold_threshold"])
                strat.save()
                strategies = BT_RSI_Strategy.objects.filter(id=strat.id)
                context['strategies'] = strategies

                context['rsi_results'] = backtest_results["rsi"]
                context['time_results'] = backtest_results["time"]
                context['closing_results'] = backtest_results["closing"]

            context['coins'] = get_live_prices()
            context['url'] = CURRENCIES

        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
            
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):

    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
