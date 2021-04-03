"""
proxy.py - A script that will help me to change my IP when I'll be ban from the server

@ Bastien Lasorne - 2021

v1.0
"""

import requests

URL = "https://www.sofascore.com/"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}

def test_connection():
    r = requests.get(URL, headers=headers)
    print(r.status_code)

test_connection()