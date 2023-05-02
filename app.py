from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://imrajesh:imrajesh@cluster0.qrcepdq.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Marcom"]
client = db["client"]
services = db["services"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():

    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = client.find_one({"number": number})
    if bool(user) == False:
        msg = res.message(
            "Hi, thanks for contacting *Marcom Web Agency*.\nYou can choose from one of the options below: "
            "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *avail* services \n 3️⃣ To know our *working hours* \n 4️⃣ "
            "To get our *contact details*")
        msg.media("https://marcomwebagency.in/wp-content/uploads/2023/03/cropped-Asset_2_2x-removebg-preview.png")
        client.insert_one({"number": number, "status": "main", "messages": []})


    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message(
                "You can contact us through phone or e-mail.\n\n*Phone*: 7827067667 \n*E-mail* : "
                "admin@marcomwebagency.com")
        elif option == 2:
            res.message("You have entered *ordering mode*.")
            client.update_one(
                {"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following services to order: \n\n1️⃣ Local SEO  \n2️⃣ Website designing "
                "\n3️⃣ SEO"
                "\n4️⃣ Social Media Marketing \n5️⃣ Google Ads \n6️⃣ FB/Insta Ads \n7️⃣ WhatsApp Marketing \n8️⃣ "
                "WhatsApp Advertising \n9️⃣ Logos/Brochure Designing  \n0️⃣ Go Back")
        elif option == 3:
            res.message("We work from *9 a.m. to 7 p.m*.")

        elif option == 4:
            res.message(
                "We have our offices in Delhi & Greater Noida. Our main center is at *B 9/2,West Vinod nagar, Delhi*")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            client.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *avail* services \n 3️⃣ To know our *working "
                        "hours* \n 4️⃣"
                        "To get our *address*")
        elif 1 <= option <= 9:
            services = ["Local SEO", "Website designing", "SEO",
                        "Social Media Marketing", "Google Ads", "FB/Insta Ads", "WhatsApp Marketing",
                        "WhatsApp Advertising", "Logos/Brochure Designing"]
            selected = services[option - 1]
            client.update_one({"number": number}, {"$set": {"status": "address"}})
            client.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Excellent choice 😉")
            res.message("Please enter your address to confirm the order")
        else:
            res.message("Please enter a valid response")

    elif user["status"] == "address":
        selected = user["item"]
        db = cluster["Marcom"]
        services = db["services"]
        res.message("Thanks for showing interest with us 😊")
        res.message(f"Your query for *{selected}* has been received and will be resolved in 2 hrs")
        services.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        client.update_one({"number": number}, {"$set": {"status": "ordered"}})

    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *avail* services \n 3️⃣ To know our *working hours* "
                    "\n 4️⃣"
                    "To get our *address*")
        client.update_one({"number": number}, {"$set": {"status": "main"}})
    client.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()
