# import requests
# import time

# def retry(fun):
#     def retry_wrapper(*args,**kargs):
#         attemp = 0
#         retry = 3
#         while attemp < retry:
#             try:
#                 return fun(*args,**kargs)
#             except requests.exceptions.RequestException as e:
#                 print(e)
#                 time.sleep(2)
#                 attemp += 1
#     return retry_wrapper

# @retry
# def get_data(url):
#     r = requests.get(url)
#     return r.text


# data= get_data("https://www.google.com/")
# print(data)

from collections import defaultdict
l = ["eat", "tea", "tan", "ate", "nat", "bat"]

result = defaultdict(int)
for word in l:
    sorted_word = ''.join(sorted(word))
    result[sorted_word] += 1

print(dict(result))  # {'aet': 3, 'ant': 2, 'abt': 1}