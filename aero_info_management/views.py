from django.shortcuts import render
# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI2MTQ1NzUwLCJqdGkiOiI2MWQxZjViMjNmNzU0YjM5OGU2ODA1YTYyOGUzODEwMiIsInVzZXJfaWQiOjIyfQ.i9-HmCkmX58a4Q27Fes2L3yUXeO65k3vTe_GqBuayFY
from django.urls import reverse
from datetime import date, datetime, time
from django.core.files.uploadedfile import SimpleUploadedFile

import requests

file = open("C:/Users/Utilisateur/Desktop/notesabba.txt", 'rb')
uploaded_file = SimpleUploadedFile('notesabba.txt', file.read())

url = "http://127.0.0.1:8000/aeroinfos/demande-notam/create"
data_notam = {
    'start_val_period': str(date(2021, 8, 22)),
    'end_val_period': str(date(2021, 10, 22)),
    'daily_freq_start': str(time(8, 30)),
    'daily_freq_end': str(time(17, 30)),
}
files = {
    'attachments': [
        {'file': ('notes.txt', file)}
    ]
}

bearer_token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI2MTQ1ODc5LCJqdGkiOiIwM2E4M2QyOWVkNmQ0ZTFlODU5MjBjZDUwZmFjZDA5OCIsInVzZXJfaWQiOjIyfQ.qHS8hGms9Sbr8LlFSAzOxY5Ha5MGNz15DQSIQEOESGA"
r = requests.post(url, data=data_notam, files=files, headers={"Authorization": bearer_token})
print(r.headers, r.content)