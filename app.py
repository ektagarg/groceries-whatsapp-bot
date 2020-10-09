import re
import pandas as pd
import json
from config import TWILIO_DEFAULT_TO, TWILIO_FROM, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot(tea_flag=False, to=TWILIO_DEFAULT_TO,add_more_flag=False):
    # read in data
    with open('data.json') as f:
        items = json.load(f)

    # make string lowercase and remove whitespace
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    if request.args.get('tea_flag'):
        message = client.messages.create(
                            from_=TWILIO_FROM,
                            body="Hello! Looks like your tea is about to finish. I am Ordering one for you!\n"
                                    "Added 1 kg Grofers Happy Day Prime Tea in your cart!\n",
                            media_url="https://cdn.grofers.com/app/images/products/full_screen/pro_387202.jpg",
                            to=to
                          )

        return str(message)
            
    if request.args.get('add_more_flag') or incoming_msg.lower() == "continue":
        message = client.messages.create(
                            from_=TWILIO_FROM,
                            body="Is there anything else you want me to add to your cart?\n"
                                    "You can ask questions like:\n"
                                    "------------------------\n"
                                    "- Add Atta\n"
                                    "- Add Oil\n"
                                    "- Show my cart items\n"
                                    "- How many items are there in cart?\n"
                                    "- What is the total amount?\n"
                                    "- Cart checkout\n",
                            to=to
                          )

        return str(message)

    item = re.findall('|'.join(items["list"]), incoming_msg)
    total_sum = re.findall('|'.join(items["total_amount"]), incoming_msg)
    num_items = re.findall('|'.join(items["num_items"]), incoming_msg)
    show_items = re.findall('|'.join(items["show_items"]), incoming_msg)
    checkout = re.findall('|'.join(items["checkout"]), incoming_msg)

    if len(item)>0:
        selected_quantity = re.findall('|'.join(items[item[0]]["quantity_map"].keys()), incoming_msg)

        if len(incoming_msg) > 20:
            reply = ("Great! I have added the selected item in your cart\n")

        elif len(selected_quantity)>0:
            reply = ("We have these options available\n"
                "Select an option:\n")
            category = items[item[0]]["quantity_map"][selected_quantity[0]]
            q = items[item[0]][category]
            for i in range(len(q)):
                reply = reply + f"{i+1}. {q[i]}\n"

        else:
            if item[0] in incoming_msg:
                reply = ("Please select quantity:\n")
                q = items[item[0]]["quantity"]
                for i in range(len(q)):
                    reply = reply + f"{i+1}. {q[i]}\n"

    elif len(show_items)>0:
        reply = ("These are your cart items:\n"
                "------------------------\n"
                "Tata Premium Tea\n"
                "Grofers Mother's Choice Sharbati Atta\n"
                "Grofers Mother's Choice Kachi Ghani Mustard Oil")

    elif len(num_items)>0:
        reply = ("There are 3 items your cart\n")

    elif len(total_sum)>0:
        reply = ("Rs. 892\n")

    elif len(checkout)>0:
        reply = ("Cart Items:\n"
                "Tata Premium Tea\n"
                "Grofers Mother's Choice Sharbati Atta\n"
                "Grofers Mother's Choice Kachi Ghani Mustard Oil\n"
                "------------------------\n"
                "Total amount: 892\n"
                "Payment mode: COD\n"
                "------------------------\n"
                "Congrats, Your order has been placed successfully!!\n")

    else:
        reply = ("I'm sorry but I don't understand your question.  You can see some example questions by typing in 'hello'.")
    
    msg.body(reply)
    return str(resp)

def status():
    print(status)