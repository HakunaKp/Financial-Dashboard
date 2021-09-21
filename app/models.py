# -*- encoding: utf-8 -*-

import os, json, locale
from django.db import models
from django.conf import settings
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from django.forms import ModelForm

CG = CoinGeckoAPI()

locale.setlocale( locale.LC_ALL, '' )

class Coin(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=50)
    cur_val = models.DecimalField(default=100000.00, decimal_places=2, max_digits=20)

class BT_RSI_Strategy(models.Model):

    interval_options = (
        ('One Minute', 'One Minute'),
        ('Five Minute', 'Five Minute'),
        ('Fifteen Minute', 'Fifteen Minute'),
        ('One Hour', 'One Hour'),
        ('Half Day', 'Half Day'),
        ('One Day', 'One Day'),
    )
    
    start = models.DateTimeField(default=datetime.fromtimestamp(1609459200))
    end = models.DateTimeField(default=datetime.fromtimestamp(1622419200))
    strategy_name = models.CharField(default='Backtest RSI Strategy', max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    interval = models.CharField(max_length=20, choices=interval_options, default='One Day')
    timeframe = models.IntegerField(default=14)
    frequency = models.IntegerField(default=86400)
    begin_balance = models.DecimalField(default=1000.00, decimal_places=2, max_digits=20)
    end_balance = models.DecimalField(default = 1250.00, blank=True, decimal_places=2, max_digits=20)
    overbought_threshold = models.DecimalField(default=70.00, decimal_places=2, max_digits=20)
    oversold_threshold = models.DecimalField(default=30.00, decimal_places=2, max_digits=20)

    @property
    def format_begin_bal(self):
        return locale.currency(self.begin_balance, grouping=True)

    @property
    def format_end_bal(self):
        return locale.currency(self.end_balance, grouping=True)

    @property
    def net_change(self):
        percent_change = 100 * (self.end_balance - self.begin_balance) / self.begin_balance
        return locale.format_string('%.2f', percent_change, grouping=True)

class BT_RSI_StrategyForm(ModelForm):
    class Meta:
        model = BT_RSI_Strategy
        fields = ['start', 'end', 'interval', 'timeframe', 'frequency', 'begin_balance', 'overbought_threshold', 'oversold_threshold']

class Portfolio(models.Model):
    risk_options = (
        ('Low','Low'),
        ('Low medium','Low medium'),
        ('Medium','Medium'),
        ('Medium high', 'Medium high'),
        ('High', 'High')
    )

    date_time_created = models.DateTimeField(default=datetime.now, blank=True)
    portfolio_name = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    balance = models.IntegerField(default=0)
    risk = models.CharField(max_length=200, null=True, choices=risk_options)
    expected_return = models.FloatField(null=True)
    investment_horizion = models.DateField(null=True)

    def __str__(self):
        return self.portfolio_name

class Transaction(models.Model):

    type_options = (
        ('Buy','Buy'),
        ('Sell','Sell'),
        ('Hold', 'Hold')
    )

    ticker_options = (
        ('ETH', 'ETH'),
        ('BTC', 'BTC')
    )

    get_price = (list(((list(CG.get_price(ids='ethereum', vs_currencies='usd').values()))[0]).values()))[0]

    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)
    type = models.CharField(max_length=200, null=True, choices=type_options)
    ticker = models.CharField(max_length=10, null=True, choices=ticker_options)
    volume = models.IntegerField(null=True)
    date_time = models.DateTimeField(default=datetime.now, blank=True, null=True)
    price = models.CharField(default=get_price, max_length=30)

    def save(self, *args, **kwargs):
        self.price = CG.get_price(ids='ethereum', vs_currencies='usd')
        super(Transaction, self).save(*args, **kwargs)
