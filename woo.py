import os
from dotenv import load_dotenv
from woocommerce import API

load_dotenv('keys.env')

wcapi = API(
    url = os.getenv("WC_URL"),
    consumer_key = os.getenv("WC_KEY"),
    consumer_secret = os.getenv("WC_SECRET"),
    version = "wc/v3",
    verify_ssl = False
)