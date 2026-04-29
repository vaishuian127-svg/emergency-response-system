import requests
query = '''[out:json][timeout:30];
(
  node["amenity"="hospital"](around:5000,13.328,77.120);
  way["amenity"="hospital"](around:5000,13.328,77.120);
);
out body;'''
print(requests.post('https://overpass-api.de/api/interpreter', data=query).text)
