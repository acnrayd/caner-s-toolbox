# Bot to retrieve list of cars on sale in Mercedes Benz Turkey website. 
# It also sends notification to my Telegram bot when a new car is available.
# I am running this code in a Docker container 7&24.

import requests
import time

TOKEN = "TELEGRAM_BOT_TOKEN"
chat_id = "TELEGRAM_BOT_CHATID"

# message = "hello from your telegram bot"
# url2 = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
# print(requests.get(ur2l).json()) # this sends the message

def send_message(message):
	url2 = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
	print(requests.get(url2).json())

url = "https://shop.mercedes-benz.com/smsc-backend-os/dcp-api/v2/market-tr/products/search?lang=tr&query=%3Aprice-asc%3AallCategories%3Amarket-tr-new-passenger-cars&currentPage=0&pageSize=12&fields=FULL"

prev_products = []

while True:
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])

        for product in products:
            description = product.get("description", "")
            commission_number = product.get("commissionNumber", "")
            
            if (description, commission_number) not in prev_products:
                print(f"New product added: Description = {description}, Commission Number = {commission_number}")
                message = f"New product added:\nDescription: {description}\nCommission Number: {commission_number}"
                send_message(message)
                prev_products.append((description, commission_number))
    else:
        print("Error")
    
    time.sleep(300)
