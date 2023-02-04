import json
import os.path
import time
import requests
from datetime import datetime

start = datetime.now()

with open('settings.json', 'r', encoding='utf-8') as settings:
    attributes = json.load(settings)
    API_KEY = attributes['API_KEY']
    dateFrom = attributes['dateFrom']
    dateBefore = attributes['dateBefore']
    dateStock = attributes['dateStock']

url_stocks = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks'
params_stocks = dict(key=API_KEY, dateFrom=dateStock)

url_orders = 'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
params_orders_from = dict(key=API_KEY, dateFrom=dateFrom)
params_orders_before = dict(key=API_KEY, dateFrom=dateBefore)


def update_data(url_ord, url_st, params_from, params_before, params_stock):
    # ---------------------------DATE FROM-----------------------------------------------------------------------------#
    print('first request started')
    if os.path.exists(f"orders_from_{params_from['dateFrom']}.txt"):
        pass
    else:
        r_from = requests.get(url_ord, params=params_from)
        json_from = r_from.json()
        with open(f"orders_from_{params_from['dateFrom']}.txt", 'w') as outfile:
            json.dump(json_from, outfile)
        print('sleeping for 1 minute')
        time.sleep(60)
    print('first request finished')

    # ---------------------------DATE BEFORE---------------------------------------------------------------------------#
    print('second request started')
    if os.path.exists(f"orders_before_{params_before['dateFrom']}.txt"):
        pass
    else:
        r_before = requests.get(url_ord, params=params_before)
        json_before = r_before.json()
        with open(f"orders_before_{params_before['dateFrom']}.txt", 'w') as outfile:
            json.dump(json_before, outfile)
    print('second request finished')

    # ---------------------------STOCKS--------------------------------------------------------------------------------#
    print('third request started')
    if os.path.exists(f"stocks_today_{params_before['dateFrom']}.txt"):
        pass
    else:
        r_stock = requests.get(url_st, params=params_from)
        json_stock = r_stock.json()
        with open(f"stocks_today_{params_before['dateFrom']}.txt", 'w') as outfile:
            json.dump(json_stock, outfile)
    print('third request finished')

    # -----------------------------------------------------------------------------------------------------------------#


def stock_balances(url, params):
    with open(f"stocks_today_{params['dateFrom']}.txt") as json_from:
        data = json.load(json_from)

    stocks = {}

    idx = 0
    for itr in data:
        if data[idx]['warehouseName'] not in stocks:
            stocks[data[idx]['warehouseName']] = []
        idx += 1

    idx = 0
    for itr in data:
        stocks[data[idx]['warehouseName']].append(
            [data[idx]['supplierArticle'], data[idx]['quantity'], data[idx]['quantity']])
        idx += 1

    return stocks


def orders_average(url, params_from, params_before):
    orders_from = {}
    orders_before = {}

    with open(f"orders_from_{params_from['dateFrom']}.txt") as json_from:
        data_from = json.load(json_from)
        idx = 0
        for itr in data_from:
            if itr['isCancel'] is False:
                if itr['supplierArticle'] not in orders_from:
                    orders_from[itr['supplierArticle']] = 1
                else:
                    orders_from[itr['supplierArticle']] += 1
            idx += 1

    with open(f"orders_before_{params_before['dateFrom']}.txt") as json_before:
        data_before = json.load(json_before)
        idx = 0
        for itr in data_before:
            if itr['isCancel'] is False:
                if itr['supplierArticle'] not in orders_before:
                    orders_before[itr['supplierArticle']] = 1
                else:
                    orders_before[itr['supplierArticle']] += 1
            idx += 1

    average_per_day = {}

    flag = False
    for itr in orders_from.items():
        for itr2 in orders_before.items():
            if itr[0] == itr2[0]:
                diff = itr[1] - itr2[1]
                if diff > 0:
                    # print(itr[0], diff, math.ceil(diff / 31))
                    average_per_day[itr[0]] = diff / 31
                flag = True
        if not flag and itr[1] > 0:
            # print(itr[0], itr[1], math.ceil(itr[1] / 31))
            average_per_day[itr[0]] = itr[1] / 31
        flag = False

    return average_per_day


def sum_of_articles(st_balance):
    articles = {}

    idx = 1

    for i in st_balance.items():
        article = i[idx]
        for j in article:
            article_name = j[0]
            if article_name not in articles:
                articles[article_name] = j[1]
            else:
                articles[article_name] += j[1]

    return articles


def sort_by_status(input_list):
    return input_list[2]


update_data(url_ord=url_orders, url_st=url_stocks, params_from=params_orders_from, params_before=params_orders_before,
            params_stock=params_stocks)
stocks_balance = stock_balances(url_stocks, params_stocks)

average_article_orders_per_day = orders_average(url_orders, params_orders_from, params_orders_before)

all_articles = sum_of_articles(stocks_balance)

result = []

for i in all_articles.items():
    if i[0] in average_article_orders_per_day:
        result.append([i[0], i[1], '?', average_article_orders_per_day[i[0]] * 20 - i[1]])

for i in average_article_orders_per_day.items():
    article_name = i[0]
    article_average = i[1]
    result_idx = 0
    for j in result:
        result_name = j[0]
        result_amount = j[1]
        result_type = j[2]
        if article_name == result_name:
            if result_amount / article_average <= 20:
                result[result_idx][2] = 0
            elif result_amount / article_average <= 40:
                result[result_idx][2] = 1
            else:
                result[result_idx][2] = 2

        result_idx += 1

sorted_result = sorted(result, key=sort_by_status)

for i in sorted_result:
    print(i)

with open(f'data{dateStock}.txt', 'w') as outfile:
    for i in sorted_result:
        outfile.write(str(i) + '\n')

end = datetime.now() - start

print('script completed in ', end)
