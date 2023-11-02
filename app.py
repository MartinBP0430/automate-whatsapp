from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://MartinBP:mbp@cluster0.pby7eh3.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route('/bot', methods=['GET', 'POST'])
def bot():
    text = request.form.get('Body')
    number = request.form.get('From')
    number = number.replace('whatsapp:', "")
    resp = MessagingResponse()
    user = users.find_one({"number": number})
    if not bool(user):
        resp.message("Hi, thanks for contacting *The Red Velvet*. \nYou can choose from one of the options below: "
                     "\n\n*Type*\n\n 1.- To *contact* us \n 2.- To *order* snacks  \n 3.- To know our *working hours* "
                     "\n 4.-"
                     "To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            resp.message("Please enter a valid response")
            return str(resp)
        if option == 1:
            resp.message("You can contact us through phone or e-mail.\n\n*Phone*: 6861900026 \n*E-mail*: "
                         "martin.becparra@gmail.com")
        elif option == 2:
            resp.message("You have entered *ordering mode*.")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            resp.message("You can select one of the following cakes to order: \n\n 1.- Red Velvet \n 2.- Dark Forest "
                         "\n 3.- Ice Cream Cake \n 4.- Plum Cake \n 5.- Sponge Cake \n 6.- Genoise Cake \n 7.- Carrot "
                         "Cake \n 8.- Butterscotch \n 0.- Go Back")
        elif option == 3:
            resp.message("We work everyday from *9 AM to 9 PM*")
        elif option == 4:
            resp.message("We have many centres across the city. Our main center is at *4/54, Mexicali*")
        else:
            resp.message("Please enter a valid response")
            return str(resp)
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            resp.message("Please enter a valid response")
            return str(resp)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            resp.message("Hi, thanks for contacting *The Red Velvet*. \nYou can choose from one of the options below: "
                         "\n\n*Type*\n\n 1.- To *contact* us \n 2.- To *order* snacks  \n 3.- To know our *working "
                         "hours*"
                         "\n 4.-"
                         "To get our *address*")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "Dark Forest Cake",
                     "3.- Ice Cream Cake", "4.- Plum Cake", "5.- Sponge Cake", "6.- Genoise Cake", "7.- Carrot Cake",
                     "Butterscotch Cake"]
            selected = cakes[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            resp.message("Excellent Choice")
            resp.message("Please enter your address to confirm the order")
        else:
            resp.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        resp.message("Thanks for shopping with us!")
        resp.message(f"Your order for {selected} has been received and will be delivered within an hour")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        resp.message("Hi, thanks for contacting *The Red Velvet*. \nYou can choose from one of the options below: "
                     "\n\n*Type*\n\n 1.- To *contact* us \n 2.- To *order* snacks  \n 3.- To know our *working hours* "
                     "\n 4.-"
                     "To get our *address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(resp)


if __name__ == '__main__':
    app.run()
