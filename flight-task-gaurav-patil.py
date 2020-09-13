from pymongo import MongoClient
from pprint import pprint


def flight():
    # Database connection string
    client = MongoClient("mongodb://localhost/")

    # Table
    db = client.flight

    # 1/50
    threshold_value = 0.02

    # First group the data by month
    # Sort the data by the month (1 - 12)
    # Calculate the probability by dividing no_of_canceled/total_flights
    # Based on the threshold value I assign either good or bad
    # Based on the good or bad I get the reliability for each month
    result = db.flightsview.aggregate([{"$group": {
        "_id": {
            "$substr": ["$flight_date", 5, 2]
        },
        "cancelled_count": {"$sum": "$cancelled"},
        "total_flights": {"$sum": 1}
        }},

        {"$sort": {"_id": 1}},

        {"$project": {
            "probability": {"$divide": ["$cancelled_count", "$total_flights"]}
        }},

        {"$project": {
            "flag": {"$cond": {"if": {"$gte": ["$probability", threshold_value]}, "then": "Bad", "else": "Good"}}
        }},

        {"$project": {
            "reliable": {"$cond": {"if": {"$eq": ["$flag", "Bad"]}, "then": False, "else": True}}
        }}
    ])

    # creating a map of month and reliability value
    month_reliability_map = {int(month["_id"]): {'reliable': month["reliable"]} for month in result}

    # Pretty print the map
    pprint(month_reliability_map)

    # Iterating over records to add the reliability attribute to all documents based on the month
    for f in db.flightsview.find():
        # Query
        my_query = {"_id": f["_id"]}
        # The attribute to insert
        new_values = {"$set": month_reliability_map[f["flight_date"].month]}
        # Adding the new attribute to the document
        db.flightsview.update_one(my_query, new_values)


if __name__ == "__main__":
    flight()
