from flask import Flask, make_response, request
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from datetime import datetime


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost/DVD_RENTALS"
api = Api(app)
mongo = PyMongo(app)


class Customer(Resource):

    def get(self, customer_id=None):
        if not customer_id:
            # Returns all customers when a customer_id is not specified
            customers = mongo.db.customers.find({}, {"_id": 1,
                                                     "First Name": 1,
                                                     "Last Name": 1,
                                                     "Phone": 1,
                                                     "Address": 1,
                                                     "City": 1,
                                                     "District": 1,
                                                     "Country": 1
                                                     })
            customers = list(customers)
            return customers if len(customers) > 0 else make_response("No customers in the database", 404)

        else:
            # Returns a specific customer when a customer_id is specified in the URL
            customer = mongo.db.customers.find_one({"_id": customer_id}, {
                                                    "_id": 1,
                                                    "First Name": 1,
                                                    "Last Name": 1,
                                                    "Phone": 1,
                                                    "Address": 1,
                                                    "City": 1,
                                                    "District": 1,
                                                    "Country": 1,
                                                    "Rentals": 1
                                                })

            if customer and customer["Rentals"]:

                # Assumption: rentals is a list of dictionaries instead of just a dictionary with the movie name
                # as a key because, a single customer might rent the same movie twice. It is still possible to have
                # a dictionary with movie names as key mapping to list of each instance of data where the customer
                # rented the movie. I went with the list of dicts for simplicity.
                rentals = []

                for rental in customer["Rentals"]:
                    rental_date = datetime.strptime(rental["Rental Date"].split(" ")[0], '%Y-%m-%d').date()
                    return_date = datetime.strptime(rental["Return Date"].split(" ")[0], '%Y-%m-%d').date()
                    length_of_rental = (return_date - rental_date).days

                    rentals.append({
                        "Film Title": rental["Film Title"],
                        "Rental Date": rental["Rental Date"],
                        "Rental Duration": length_of_rental,
                        "Amount": rental["Payments"][0]["Amount"]
                    })
                customer["Rentals"] = rentals

            return customer if customer else make_response("Customer with id " + str(customer_id) + " does not exist",
                                                           404)


class Films(Resource):

    def get(self, film_id=None):
        if not film_id:
            films = mongo.db.films.find(
                {},
                {
                    "Title": 1,
                    "Category": 1,
                    "Description": 1,
                    "Rating": 1,
                    "Rental Duration": 1,
                }
            )

            films = list(films)
            return films if len(films) > 0 else make_response("No films in the database", 404)

        else:
            films = mongo.db.films.aggregate([
                {"$match": {"_id": film_id}},
                {
                    "$lookup": {
                        "from": "customers",
                        "localField": "_id",
                        "foreignField": "Rentals.filmId",
                        "as": "customer"
                    }
                },
                {
                    "$unwind": "$customer"
                },
            ])

            films = list(films)

            # Sanitizing the results before sending them to the client
            # I believe this step can also be performed in the query in the new version of MongoDB
            # We group and then append all the customers into an array of objects
            if len(films) > 0:
                film = {
                    "Category": films[0]["Category"],
                    "Description": films[0]["Description"],
                    "Length": films[0]["Length"],
                    "Rating": films[0]["Rating"],
                    "Rental Duration": films[0]["Rental Duration"],
                    "Replacement Cost": films[0]["Replacement Cost"],
                    "Special Features": films[0]["Special Features"],
                    "Title": films[0]["Title"],
                    "Actors":  films[0]["Actors"],
                    "_id": films[0]["_id"],
                    "Customers": [{
                        'Address': f["customer"]['Address'],
                        'City': f["customer"]['City'],
                        'Country': f["customer"]['Country'],
                        'District': f["customer"]['District'],
                        'First Name': f["customer"]['First Name'],
                        'Last Name': f["customer"]['Last Name'],
                        'Phone': f["customer"]['Phone'],
                    } for f in films if f["customer"]]
                }
                return film
            else:
                return make_response("Film with id " + str(film_id) + " does not exist", 404)

    def post(self):

        json_data = request.get_json(force=True)

        if "title" in json_data:
            film_title = json_data["title"]
        else:
            return make_response("Please provide a movie title to search", 404)

        films = mongo.db.films.aggregate([
            {"$match": {"Title": {"$regex": '^.*'+film_title+'.*$'}}},
            {
                "$lookup": {
                    "from": "customers",
                    "localField": "_id",
                    "foreignField": "Rentals.filmId",
                    "as": "customer"
                }
            },
            {
                "$unwind": "$customer"
            },
        ])

        films = list(films)

        if len(films) > 0:
            # Creating a dict of list in case there is more than one movie that matches the pattern
            film_dict = {}
            for film in films:
                if film["_id"] in film_dict:
                    film_dict[film["_id"]].append(film)
                else:
                    film_dict[film["_id"]] = [film]

            fs = []
            for key, films in film_dict.items():
                fs.append({
                    "Category": films[0]["Category"],
                    "Description": films[0]["Description"],
                    "Length": films[0]["Length"],
                    "Rating": films[0]["Rating"],
                    "Rental Duration": films[0]["Rental Duration"],
                    "Replacement Cost": films[0]["Replacement Cost"],
                    "Special Features": films[0]["Special Features"],
                    "Title": films[0]["Title"],
                    "Actors": films[0]["Actors"],
                    "_id": films[0]["_id"],
                    "Customers": [{
                        'Address': f["customer"]['Address'],
                        'City': f["customer"]['City'],
                        'Country': f["customer"]['Country'],
                        'District': f["customer"]['District'],
                        'First Name': f["customer"]['First Name'],
                        'Last Name': f["customer"]['Last Name'],
                        'Phone': f["customer"]['Phone'],
                    } for f in films if f["customer"]]
                })
                return fs
        else:
            return make_response("Film with title matching " + str(film_title) + " does not exist", 404)


api.add_resource(Customer, '/customers', '/customers/<int:customer_id>')
api.add_resource(Films, '/films', '/films/<int:film_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
