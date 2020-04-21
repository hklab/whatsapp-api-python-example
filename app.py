from flask import Flask, request, jsonify
from pyngrok import ngrok
import requests
import sys

app = Flask(__name__)

# Replace the values here.
INSTANCE_URL = "https://api.maytapi.com/api"
PRODUCT_ID = ""
PHONE_ID = ""
API_TOKEN = ""


@app.route("/")
def hello():
    return app.send_static_file("index.html")


def send_response(body):
    print("Request Body", body, file=sys.stdout, flush=True)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/" + PHONE_ID + "/sendMessage"
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    response = requests.post(url, json=body, headers=headers)
    print("Response", response.json(), file=sys.stdout, flush=True)
    return


@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json()
    message = json_data["message"]
    conversation = json_data["conversation"]
    _type = message["type"]
    if message["fromMe"]:
        return
    if _type == "text":
        # Handle Messages
        text = message["text"]
        text = text.lower()
        print("Type:", _type, "Text:", text, file=sys.stdout, flush=True)
        if text == "image":
            body = {
                "type": "media",
                "text": "Image Response",
                "message": "http://placehold.it/180",
            }
        elif text == "location":
            body = {
                "type": "location",
                "text": "Location Response",
                "latitude": "41.093292",
                "longitude": "29.061737",
            }
        else:
            body = {"type": "text", "message": "Echo - " + text}
        body.update({"to_number": conversation})
        send_response(body)
    else:
        print("Ignored Message Type:", type,  file=sys.stdout, flush=True)
    return jsonify({"success": True}), 200


def setup_webhook():
    if PRODUCT_ID == "" or PHONE_ID == "" or API_TOKEN == "":
        print(
            "You need to change PRODUCT_ID, PHONE_ID and API_TOKEN values in app.py file.", file=sys.stdout, flush=True
        )
        return
    public_url = ngrok.connect(9000)
    public_url = public_url.replace("http", "https", 1)
    print("Public Url " + public_url, file=sys.stdout, flush=True)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/setWebhook"
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    body = {"webhook": public_url + "/webhook"}
    response = requests.post(url, json=body, headers=headers)
    print(response.json(), file=sys.stdout, flush=True)


# Do not use this method in your production environment
setup_webhook()
