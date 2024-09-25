import json
import threading
import os

from flask import Flask, request, send_file

from telegram_functions import get_file_path, save_file_and_get_local_path, send_message_telegram, send_video_telegram, set_webhook_telegram
from utils import call_luma_api_image_to_video, call_luma_api_text_to_video

app = Flask(__name__)


@app.get("/")
def handle_home():
    return "OK", 200


@app.get("/get-image/<string:file_id>")
def handle_get_image(file_id: str):
    file_path_data = get_file_path(file_id=file_id)
    if file_path_data.get("status", False):
        local_file_path_data = save_file_and_get_local_path(
            file_path=file_path_data.get("file_path", ""))
        if local_file_path_data.get("status", False):
            try:
                return send_file(local_file_path_data.get("local_file_path", ""), mimetype='image/jpeg', download_name=f"""sample_image.{local_file_path_data["extension"]}""")
            finally:
                os.unlink(local_file_path_data.get("local_file_path", ""))
        else:
            return "BAD REQUEST", 403
    else:
        return "BAD REQUEST", 403


def call_luma_api_text_to_video_send_message_to_telegram(prompt: str, recipient_id: str) -> None:
    send_message_telegram(
        message="Generating video, it will take about 3 minutes...", recipient_id=recipient_id)
    video_url, status = call_luma_api_text_to_video(prompt=prompt)
    if status:
        send_video_telegram(video_url=video_url[0], recipient_id=recipient_id)
    else:
        send_message_telegram(
            message="Video generation failed, please try after some time.", recipient_id=recipient_id)


def call_luma_api_image_to_video_send_message_to_telegram(prompt: str, image_url: str, recipient_id: str) -> None:
    send_message_telegram(
        message="Generating video, it will take about 3 minutes...", recipient_id=recipient_id)
    video_url, status = call_luma_api_image_to_video(
        prompt=prompt, image_url=image_url)
    if status:
        send_video_telegram(video_url=video_url[0], recipient_id=recipient_id)
    else:
        send_message_telegram(
            message="Video generation failed, please try after some time.", recipient_id=recipient_id)


@app.post("/telegram")
def handle_telegram_post():
    try:
        body = request.get_json()
        print(json.dumps(body))
        message = dict(body["message"])
        keys = message.keys()
        print(keys)
        recipient_id = body["message"]["from"]["id"]
        if "text" in keys:
            query = str(body["message"]["text"])
            command = query.split(" ")[0]
            if command == "/start":
                send_message_telegram(
                    message="Welcome to VidifyAI! This bot can generate videos. Use /video to start generating.",
                    recipient_id=recipient_id
                )
            elif command == "/video":
                prompt_words = query.split(" ")[1:]
                prompt = " ".join(prompt_words)
                threading.Thread(
                    target=call_luma_api_text_to_video_send_message_to_telegram,
                    args=(prompt, recipient_id)
                ).start()
        base_url = request.base_url
        base_url = base_url.split("://")[1:]
        base_url = f"""https://{"".join(base_url)}"""
        base_url = base_url.rsplit("/", maxsplit=1)[:-1]
        base_url = "".join(base_url)
        if "document" in keys:
            document = dict(body["message"]["document"])
            print(json.dumps(document))
            if "image" in document["mime_type"]:
                if "caption" in keys:
                    threading.Thread(
                        target=call_luma_api_image_to_video_send_message_to_telegram,
                        args=(
                            message["caption"], f"""{base_url}/get-image/{document["file_id"]}""", recipient_id)
                    ).start()
                else:
                    send_message_telegram(
                        message="A caption is needed with an image to generate video.",
                        recipient_id=recipient_id
                    )
        elif "photo" in keys:
            photo = dict(body["message"]["photo"][0])
            print(json.dumps(photo))
            if "caption" in keys:
                threading.Thread(
                    target=call_luma_api_image_to_video_send_message_to_telegram,
                    args=(
                        message["caption"], f"""{base_url}/get-image/{photo["file_id"]}""", recipient_id)
                ).start()
            else:
                send_message_telegram(
                    message="A caption is needed with an image to generate video.",
                    recipient_id=recipient_id
                )
    except:
        pass
    return "OK", 200


@app.get("/telegram")
def handle_telegram_get():
    base_url = request.base_url
    parts = base_url.split("://")[1:]
    base_url = f"""https://{"".join(parts)}"""
    flag = set_webhook_telegram(url=base_url)
    if flag:
        return "OK", 200
    else:
        return "BAD_REQUEST", 403
