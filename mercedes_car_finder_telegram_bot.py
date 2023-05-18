### Bot to retrieve list of cars on sale in Mercedes Benz Turkey website. 
# It also sends notification to my Telegram bot when a new car is available.
# I am running this code in a Docker container 7&24.

import requests
import time

TOKEN = "TELEGRAM_TOKEN"
chat_id = "CHAT_ID

url2 = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"

def send_message(message):
    url2 = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url2).json()) 

url = "URL_OF_MERCEDES_STORE" ## Your secret mission is to find this URL. 

prev_products = []

while True:
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])

        for product in products:
            description = product.get("description", "")
            commission_number = product.get("commissionNumber", "")
            price = product.get("price", {})
            price = price.get("formattedValue", "")
            estimated_arrival = product.get("stock", {})
            estimated_arrival = estimated_arrival.get("estimatedArrivalDate", "")
            stock = product.get("stock", {})
            stock = stock.get("stockType", "")

            if (description, commission_number) not in prev_products:
                print(f"Yeni Arac eklendi: Model = {description}, Fiyat: {price}, Commission Nr = {commission_number}")
                message = f"Yeni Arac Eklendi:\nModel: {description}\nFiyat: {price}\nStok: {stock}\nTeslim: {estimated_arrival}\nCommission Nr: {commission_number}"
                send_message(message)
                prev_products.append((description, commission_number))
    else:
        print("Error: Failed to retrieve data from the URL.")

    time.sleep(30)
