import threading
import json

from flask import Flask, request
import requests

import config
from utils import call_luma_api

app = Flask(__name__)

BASE_URL = f'https://api.telegram.org/bot{config.TELEGRAM_BOT_API_KEY}'


def send_message_telegram(message: str, recipient_id: int) -> None:
    payload = {
        'chat_id': recipient_id,
        'text': message
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.request(
        'POST', f'{BASE_URL}/sendMessage', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.text)
    if status_code == 200 and response['ok']:
        print("TELEGRAM MESSAGE SENT SUCCESSFULLY.")
    else:
        print("TELEGRAM MESSAGE SENT FAILED.")


def send_video_telegram(video_url: str, recipient_id: int) -> None:
    payload = {
        'chat_id': recipient_id,
        'video': video_url
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.request(
        'POST', f'{BASE_URL}/sendVideo', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.text)
    if status_code == 200 and response['ok']:
        print("TELEGRAM VIDEO SENT SUCCESSFULLY.")
    else:
        print("TELEGRAM VIDEO SENT FAILED.")


def set_webhook_telegram(url: str, secret_token: str = '') -> bool:
    payload = {'url': url}
    if secret_token != '':
        payload['secret_token'] = secret_token
    headers = {'Content-Type': 'application/json'}
    response = requests.request(
        'POST', f'{BASE_URL}/setWebhook', json=payload, headers=headers)
    status_code = response.status_code
    response = json.loads(response.text)
    if status_code == 200 and response['ok']:
        return True
    else:
        return False


@app.route("/")
def handle_home():
    return "OK", 200


def call_luma_api_send_message_to_telegram(prompt: str, recipient_id: str) -> None:
    send_message_telegram(
        message="Generating video, it will take about 3 minutes...", recipient_id=recipient_id)
    video_url, status = call_luma_api(prompt=prompt)
    if status:
        send_video_telegram(video_url=video_url[0], recipient_id=recipient_id)
    else:
        send_message_telegram(
            message="Video generation failed, please try after some time.", recipient_id=recipient_id)


@app.route("/telegram", methods=["POST"])
def handle_telegram_post():
    try:
        body = request.get_json()
        query = str(body["message"]["text"])
        recipient_id = body["message"]["from"]["id"]
        command = query.split(" ")[0]
        if command == "/start":
            send_message_telegram(
                message="Welcome to VidifyAI! This bot can generate videos. Use /video to start generating.",
                recipient_id=recipient_id
            )
        else:
            prompt_words = query.split(" ")[1:]
            prompt = " ".join(prompt_words)
            threading.Thread(
                target=call_luma_api_send_message_to_telegram,
                args=(prompt, recipient_id)
            ).start()
    except:
        pass
    return "OK", 200


@app.route("/telegram", methods=["GET"])
def handle_telegram_get():
    base_url = f"https://2a72-2405-201-2027-501a-54b9-8cfb-cbe5-3081.ngrok-free.app/telegram"
    flag = set_webhook_telegram(url=base_url)
    if flag:
        return "OK", 200
    else:
        return "BAD_REQUEST", 403
