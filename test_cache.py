import urllib.request
import re

try:
    html = urllib.request.urlopen('http://13.49.74.167/').read().decode('utf-8')
    match = re.search(r'src="(/assets/index-.*?\.js)"', html)
    if not match:
        print("No JS file found in HTML")
    else:
        js_url = match.group(1)
        print("Found JS URL:", js_url)
        js = urllib.request.urlopen('http://13.49.74.167' + js_url).read().decode('utf-8')
        print("HAS LOCALHOST:", "localhost:8000" in js)
        print("HAS CLOUD IP:", "13.49.74.167:8000" in js)
except Exception as e:
    print("Error:", e)
