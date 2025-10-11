import requests
r = requests.get("https://www.urp.cnr.it/documenti/dipartimentiistituti")
print(len(r.text))
print(r.text[:1000])
