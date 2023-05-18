TG_TOKEN = "6153881889:AAEWPcHZJtrVEDpN2YwfFFOFvH9JteRkI00"
WB_API = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6Ijk1N2U5NGZhLTZlZmItNDVkZi1iNjhmLTQzMTJmYWUwNDYzZSJ9.JTJCaPE5MoJXDd_QySv_mwA1nsa41B4C5wgNk7eC8KY"

from datetime import datetime
import pytz
import requests

url_stock = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
tz = pytz.timezone("Europe/Moscow")
current_time = str(datetime.now(tz).date())

params = {'dateFrom': current_time}
header = {'Authorization': WB_API}
data = requests.get(url_stock, headers=header, params=params)
print(data)
