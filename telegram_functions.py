import json
import uuid
import os
import tempfile

import requests

import config


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


def get_file_path(file_id: str) -> dict[str, any]:
    url = f'https://api.telegram.org/bot{config.TELEGRAM_BOT_API_KEY}/getFile'
    querystring = {'file_id': file_id}
    response = requests.request('GET', url, params=querystring)
    if response.status_code == 200:
        data = json.loads(response.text)
        file_path = data['result']['file_path']
        return {
            'status': True,
            'file_path': file_path
        }
    else:
        return {
            'status': False,
            'file_path': ''
        }


def save_file_and_get_local_path(file_path: str) -> dict[str, any]:
    url = f'https://api.telegram.org/file/bot{config.TELEGRAM_BOT_API_KEY}/{file_path}'
    response = requests.request('GET', url)
    extention = file_path.split('.')[-1]
    file_id = uuid.uuid1()
    file_name = f'{file_id}.{extention}'
    local_file_path = os.path.join(
        tempfile.gettempdir(),
        file_name
    )
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
        return {
            'status': True,
            'local_file_path': local_file_path,
            'file_name': file_name,
            'file_id': file_id,
            'extension': extention
        }
    else:
        return {
            'status': False,
            'local_file_path': '',
            'file_name': '',
            'file_id': '',
            'extension': ''
        }
