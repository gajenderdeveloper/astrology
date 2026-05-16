import time
import requests
from tenacity import retry,stop_after_attempt


# # count = 0
# @retry(stop=stop_after_attempt(7))
# def stop_after_7_attempts():
#     print("Stopping after 7 attempts")
#     raise Exception

