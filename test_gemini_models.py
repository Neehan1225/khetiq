import os
from google import genai

client = genai.Client(api_key="AIzaSyCAaAKwmiO_qEwejfphmzuYQjen4ow3i2w")
for model in client.models.list():
    if "gemini" in model.name:
        print(model.name)
        try:
            resp = client.models.generate_content(model=model.name, contents="Hello")
            print("SUCCESS:", model.name)
            break
        except Exception as e:
            print("FAILED:", model.name, str(e)[:100])
