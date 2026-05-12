import os
from google import genai

client = genai.Client(api_key="AIzaSyCAaAKwmiO_qEwejfphmzuYQjen4ow3i2w")
try:
    resp = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello"
    )
    print("1.5-flash success:", resp.text)
except Exception as e:
    print("1.5-flash failed:", e)

try:
    resp = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents="Hello"
    )
    print("2.0-flash-lite success:", resp.text)
except Exception as e:
    print("2.0-flash-lite failed:", e)
