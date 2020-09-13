import requests
from pprint import pprint

BASE = "http://0.0.0.0:5000"


# Displays a list of customers
response = requests.get(BASE + "/customers")
if response.status_code == 200:
    pprint(response.json())
else:
    print(response.status_code)
    print(response.content)

# Displays a customer with id '1'
response = requests.get(BASE + "/customers/1")
if response.status_code == 200:
    pprint(response.json())
else:
    print(response.status_code)
    print(response.content)

# Displays information of all the films in the db
response = requests.get(BASE + "/films")
if response.status_code == 200:
    pprint(response.json())
else:
    print(response.status_code)
    print(response.content)

# Displays a film with id '2' the result also contains a list of customer who rented the movie
response = requests.get(BASE + "/films/2")
if response.status_code == 200:
    pprint(response.json())
else:
    print(response.status_code)
    print(response.content)

# Retrieves a movie with a specific name or id
response = requests.post(BASE + "/films", json={"title": "ACE GOLDFINGER"})
if response.status_code == 200:
    pprint(response.json())
else:
    print(response.status_code)
    print(response.content)
