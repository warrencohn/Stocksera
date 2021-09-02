from django.urls import path
# from django.conf.urls import (handler400, handler403, handler404, handler500)
from . import views

# handler404 = 'ViewStocks.views.custom_page_not_found_view'
# handler500 = 'ViewStocks.views.custom_error_view'
# handler403 = 'ViewStocks.views.custom_permission_denied_view'
# handler400 = 'ViewStocks.views.custom_bad_request_view'

urlpatterns = [
    path('', views.main, name='main'),
    path('ticker/', views.stock_price, name='ticker'),
    path('earnings_calendar/', views.earnings_calendar, name='earnings_calendar'),
    path('ticker/financial/', views.financial, name='financial'),
    path('ticker/options/', views.options, name='options'),
    path('ticker/short_volume/', views.short_volume, name='short_volume'),
    path('ticker/failure_to_deliver/', views.failure_to_deliver, name='failure_to_deliver'),
    path('reddit_analysis/', views.reddit_analysis, name='reddit_analysis'),
    path('reddit_ticker_analysis/', views.reddit_ticker_analysis, name='reddit_ticker_analysis'),
    path('market_overview/', views.market_overview, name='market_overview'),
    path('reverse_repo/', views.reverse_repo, name='reverse_repo'),
    path('daily_treasury/', views.daily_treasury, name='daily_treasury'),
    path('inflation/', views.inflation, name='inflation'),
    path('retail_sales/', views.retail_sales, name='retail_sales'),
    path('short_interest/', views.short_interest, name='short_interest'),
    path('low_float/', views.low_float, name='low_float'),
    path('ark_trades/', views.ark_trades, name='ark_trades'),
    path('historical_data/', views.historical_data, name='historical_data'),
    # path('sub_news/', views.sub_news, name='sub_news'),
    path('latest_news/', views.latest_news, name='latest_news'),
    path('google_trends/', views.google_trends, name='google_trends'),
    path('recommendations/', views.ticker_recommendations, name='recommendations'),
    path('major_holders/', views.ticker_major_holders, name='major_holders'),
    path('institutional_holders/', views.ticker_institutional_holders, name='institutional_holders'),
    path('mutual_fund_holders', views.ticker_mutual_fund_holders, name='mutual_fund_holders'),
    path('dividend_and_split/', views.dividend_and_split, name='dividend_and_split'),
    path('ticker_earnings', views.ticker_earnings, name='ticker_earnings'),
    path('subreddit_count/', views.subreddit_count, name='subreddit_count'),
    path('reddit_etf/', views.reddit_etf, name='reddit_etf'),
    path('amd_xlnx_ratio/', views.amd_xlnx_ratio, name='amd_xlnx_ratio'),
    path('beta/', views.beta, name='beta'),
    path('covid_beta/', views.covid_beta, name='covid_beta'),
    path('about/', views.about, name='about'),

]
