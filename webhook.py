from discord_webhook import DiscordWebhook, DiscordEmbed
from functions import webhook_time_stmap


def monitor_webhook(product_link, product_title, product_region, product_price, product_sku, product_sizes, webhook_link):
      webhook = DiscordWebhook(url=webhook_link, rate_limit_retry=True)
      embed = DiscordEmbed(title="Product Found", url=product_link, color='212121')
      embed.set_thumbnail(url=f"https://images.footlocker.com/is/image/FLEU/{product_sku}")
      embed.add_embed_field(name="**Product Title:**", value=product_title, inline=False)
      embed.add_embed_field(name="**Product Price:**", value=product_price, inline=False)
      embed.add_embed_field(name="**Product Region:**", value=product_region, inline=False)
      embed.add_embed_field(name="**Sizes Found:**", value=product_sizes, inline=False)
      
      embed.set_footer(text=f"Dario#9999 | {webhook_time_stmap()}")
      webhook.add_embed(embed)
      response = webhook.execute()
      if "<Response [405]>" in str(response):
            print("[ERROR] Webhook Incorrect")
      else:
            print("[INFO] Webhook Sent")      
