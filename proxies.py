import random

def proxy():
      try:
           with open("proxies.txt", "r") as f:
                  proxy_list = f.readlines()

                  if len(proxy_list) == 0:
                        print("[ERROR] No Proxies Found")
                        exit()
                  else:
                        proxy = random.choice(proxy_list).split(":")
                        proxy = "http://" + proxy[2]+":"+proxy[3]+"@"+proxy[0]+":"+proxy[1]
                        return proxy      
      except FileNotFoundError:
            print("[ERROR] Proxy File Not Found")
            exit()
      except IndexError:
            print("[ERROR] Proxy Format Incorrect [hostname:port:username:password]")
            exit()               
proxy()
