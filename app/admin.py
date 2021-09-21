# -*- encoding: utf-8 -*-

from django.contrib import admin

# Register your models here.

from .models import Portfolio, Transaction, BT_RSI_Strategy

admin.site.register(Portfolio)
admin.site.register(Transaction)
admin.site.register(BT_RSI_Strategy)