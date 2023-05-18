from config import WB_API, TG_TOKEN
from datetime import datetime
import pytz
import requests
import json
import aiohttp
import asyncio

BOT_URL = f'https://api.telegram.org/bot{TG_TOKEN}/'
url_stock = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
tz = pytz.timezone("Europe/Moscow")
current_time = str(datetime.now(tz).date())
print(current_time)
params = {'dateFrom': current_time}
header = {'Authorization': WB_API}
data = requests.get(url_stock, headers=header, params=params).json()
print(data)


# print(json_wb)

async def update_info(chat_id):
    FBS = {}
    with open('fbs.json', 'r') as fbs:
        fbs_info = json.load(fbs)
        if fbs_info['date'] == current_time:
            FBS = fbs_info
        else:
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

            articles = {}
            idx = 1

            for i in stocks.items():
                article = i[idx]
                for j in article:
                    article_name = j[0]
                    if article_name not in articles:
                        articles[article_name] = j[1]
                    else:
                        articles[article_name] += j[1]

            with open('remains.json', 'r') as remain_file:
                old_data = json.load(remain_file)
                # print(old_data)
                for article in articles.items():
                    if article not in old_data.items() and article[1] <= 10:
                        FBS[article[0]] = article[1]

            # print(FBS)

            FBS['date': current_time]
            with open('fbs.json', 'w') as fbs_file:
                json.dump(FBS, fbs_file)

            with open('remains.json', 'w') as remain_file:
                json.dump(articles, remain_file)
        FBS_text = ''
        for key, val in FBS.items():
            FBS_text += key + ': ' + str(val) + '\n'
        print(FBS_text)
    await send_message(chat_id=chat_id, text=FBS_text)


async def send_message(chat_id, text):
    async with aiohttp.ClientSession() as session:
        params = {'chat_id': chat_id, 'text': text}
        async with session.post(BOT_URL + 'sendMessage', data=params) as response:
            await response.json()


async def handle_updates(update):
    message = update['message']
    chat_id = message['chat']['id']
    try:
        await update_info(chat_id)
    except:
        # print(str(update))
        pass


async def get_updates():
    offset = None

    async with aiohttp.ClientSession() as session:
        while True:
            params = {'timeout': 10, 'offset': offset}
            async with session.post(BOT_URL + 'getUpdates', data=params) as response:
                updates = await response.json()
                if len(updates['result']) > 0:
                    offset = updates['result'][-1]['update_id'] + 1
                    for update in updates['result']:
                        await handle_updates(update)


async def main():
    await get_updates()


if __name__ == '__main__':
    asyncio.run(main())
