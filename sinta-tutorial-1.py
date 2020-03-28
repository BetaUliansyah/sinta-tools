import requests

s = requests.Session()
r = s.get('http://sinta.ristekbrin.go.id/journals')

if r.status_code==200:
    print(r.text)
