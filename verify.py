path = r'c:\Users\Lenovo\Desktop\KhetIQ\frontend\src\App.jsx'
content = open(path,'r',encoding='utf-8').read()
checks = [
    'function FDeals(',
    'function BDeals(',
    'onRespond={respondToDeal}',
    'onAcceptCounter={acceptCounter}',
    'respondToDeal',
    'acceptCounter',
    'Incoming Offers from Buyers',
    'Counter-offer:',
    'Accept Counter',
    'initiated_by',
    '/status',
]
for c in checks:
    found = c in content
    status = 'OK' if found else 'MISSING'
    print(status + ': ' + c)
print('Total lines: ' + str(len(content.splitlines())))
