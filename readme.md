# jSonar Python Task - Gaurav Patil



### Dependencies:

```bash
brew install python
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# make sure this python version is no osx inbuilt and the one installed by brew
python get-pip.py
pip install -r requirements.txt

# To run the flask server 
python main.py

# To run the client
python client.py

# Database Name
DVD_RENTALS
# Collection Names
films
customers
```



### API End points:

```python
# GET
# Returns all the customers present in the database
/customers

# Returns a customer with the specific customer id
/customers/<int:customer_id>
  
# Returns all the films present in the database
/films

# Returns a film with a specific film id
/films/<int:film_id>
  
# POST
# This is an extra end point that I wrote that can be used by 
# a client. It returns all the movies along with the information 
# about customers who rented the movies. Uses regex internally
# to find the title's pattern in the collection of films

# Additionally I could have also used fuzzy matching to get 
# most relevant movies given a movie title
/films Post data: {'title', 'Spiderman'}

```