# Generated by Django 3.2.6 on 2021-09-21 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_transaction_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='coin',
            name='name_lc',
            field=models.CharField(default='bitcoin', max_length=50),
        ),
        migrations.AddField(
            model_name='coin',
            name='symbol_lc',
            field=models.CharField(default='btc', max_length=50),
        ),
        migrations.AlterField(
            model_name='coin',
            name='name',
            field=models.CharField(default='Bitcoin', max_length=50),
        ),
        migrations.AlterField(
            model_name='coin',
            name='symbol',
            field=models.CharField(default='BTC', max_length=50),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='price',
            field=models.CharField(default=3034.88, max_length=30),
        ),
    ]
