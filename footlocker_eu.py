import asyncio
from aiohttp import ClientRequest, ClientSession, client_exceptions
import logging
import warnings
import csv
from webhook import monitor_webhook
from proxies import proxy
from functions import time_stmap
from datetime import datetime
import pause
from time import strptime
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

class CustomRequestClass(ClientRequest):
    DEFAULT_HEADERS = {}
    pass

RETRY_DELAY = 5 #In seconds
DELAY = 10 #In seconds
USE_PROXIES = True

tasks = []
proxies = []

class footlocker:
      def __init__(self, sku, region, webhook_link) -> None:
            self.region = region
            self.sku = sku
            self.endpoint = f"https://www.footlocker{self.region}/api/products/pdp/{self.sku}?timestamp={time_stmap()}"
            self.product_link = f"https://www.footlocker{self.region}/product/Dario/{self.sku}"
            self.webhook_link = webhook_link
            
            self.headers = {
                  "cache-control": "max-age=0",
                  "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                  "sec-ch-ua-mobile": "?0",
                  "sec-ch-ua-platform": '"Windows"',
                  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                  "accept": "application/json, */*",
                  "sec-fetch-site": "none",
                  "sec-fetch-mode": "navigate",
                  "sec-fetch-user": "?1",
                  "sec-fetch-dest": "document",
                  "accept-encoding": "gzip, deflate, br",
                  "accept-language": "en-GB,en-US;q=0.9,en;q=0.8"
            }

      
      async def monitor_sku(self):
            async with ClientSession(headers=self.headers, request_class=CustomRequestClass, trust_env=True) as s:
                  while True:
                        try:
                              if USE_PROXIES == False:
                                    product_response = await s.get(url=self.endpoint)
                              elif USE_PROXIES == True:
                                    proxies.append(proxy())
                                    product_response = await s.get(url=self.endpoint, proxy=proxies[0]) 
                                    proxies.clear()
                              if "Sold Out" in await product_response.text():
                                    print(f"[STATUS] {product_response.status} | {self.sku} Out Of Stock")
                                    await asyncio.sleep(RETRY_DELAY)
                              elif product_response.status == 400:
                                    print(f"[STATUS] {product_response.status} | {self.sku} Not Loaded")
                                    await asyncio.sleep(RETRY_DELAY)
                              else:
                                    product_json = await product_response.json()     
                                    if product_json["variantAttributes"][0]["displayCountDownTimer"] == True:
                                          time = str(product_json["variantAttributes"][0]["skuLaunchDate"])
                                          print(f"[STATUS] {product_response.status} | {self.sku} On Timer {time}")
                                          print(f"[INFO] Pauing Intill {time[:-9]}")   
                                          time = time.split(" ")
                                          if "0" in time[1]:
                                                time[1] = time[1].replace("0", "")
                                          hour = int(time[3].replace(":", "").replace("0", ""))      
                                       
                                          pause.until(datetime(int(time[2]), int(strptime(time[0],'%b').tm_mon), int(time[1]), hour))
                                    else:      
                                          product_title = product_json["name"]
                                          print(f"[STATUS] {product_response.status} | Found {product_title}, Fetching Stock")
                                          varients = product_json["sellableUnits"]
                                          in_stock_varients = [x for x in varients if x["stockLevelStatus"] == "inStock"]
                                          if len(in_stock_varients) > 0:
                                                sizes = str([x["attributes"][0]["value"] for x in in_stock_varients]).replace("[", "").replace("]", "").replace("'", "")
                                                print(f"[INFO] Found Sizes {sizes}")
                                                product_price = str(in_stock_varients[0]["price"]["formattedOriginalPrice"]).replace(" ", "")
                                                monitor_webhook(self.product_link, product_title, self.region, product_price, self.sku, sizes, self.webhook_link)
                                                await asyncio.sleep(DELAY)
                                          else:
                                                print("[INFO] No Sizes Found")
                                                await asyncio.sleep(RETRY_DELAY)
                        except client_exceptions.ClientConnectorError:
                              print("[ERROR] Invalid Region")  
                              break   
                        except client_exceptions.ServerDisconnectedError:
                              print("[ERROR] Proxy Error")
                              proxies.clear() 
                                       
with warnings.catch_warnings():
      warnings.filterwarnings("ignore", category=DeprecationWarning)
      with open('settings.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                  tasks.append(asyncio.ensure_future(*[footlocker(row["product_sku"], row["region"], row["webhook_link"]).monitor_sku()]))

async def run():
      await asyncio.gather(*tasks)

with warnings.catch_warnings():
      warnings.filterwarnings("ignore", category=DeprecationWarning)
      if __name__ == "__main__":
            asyncio.get_event_loop().run_until_complete(run())
