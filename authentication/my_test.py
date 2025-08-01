import requests

url = 'http://localhost:8000/auth/facebook/'
data = {'access_token': 'EAAFFAiZChFYoBAEj8BMXl3k0ZBNbJDVhxWYcXCYkEQIihoVBbZBuI1nOVeuhHdaofZCbYk0HsjKzvLPHZASjADItxoxZAty4gDJlMMa4ZCuP2D27MVT5I7guFmLfasZBEpRGQNLE8uOhXfCkwYc6TLVGWwA9TAAs9zeDIv7GUyzs9ZAZCfzmUdV1WLJ2LroUkcuAvLdlQ35QZAB3jgURM7BUZBMWciNNHzHZB9zDCi3VMbAUEqAZDZD'}
response = requests.post(url, data=data)
print(response.json())
