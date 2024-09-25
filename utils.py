import time

import requests

import config


def get_luma_job_id(prompt: str, image_url: str = "") -> str:
    try:
        if image_url == "":
            payload = {
                "prompt": prompt
            }
        else:
            payload = {
                "prompt": prompt,
                "keyframes": {
                    "frame0": {
                        "type": "image",
                        "url": image_url
                    }
                }
            }
        print(payload)
        headers = {
            "Authorization": f"Bearer {config.LUMA_API_KEY}"
        }
        response = requests.post(
            "https://api.lumalabs.ai/dream-machine/v1/generations",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        response = response.json()
        return response["id"]
    except:
        return ""


def retriev_luma_job_by_id(task_id: str) -> tuple[list[str], bool]:
    headers = {
        "Authorization": f"Bearer {config.LUMA_API_KEY}"
    }
    flag = True
    status = False
    video_url = []
    while flag:
        response = requests.get(
            f"https://api.lumalabs.ai/dream-machine/v1/generations/{task_id}",
            headers=headers,
        )
        print(response.json())
        response.raise_for_status()
        if response.status_code == 200:
            response = response.json()
            if response["state"] == "completed" and response["failure_reason"] == None:
                video_url.append(response["assets"]["video"])
                flag = False
                status = True
            if response["failure_reason"] != None:
                flag = False
                status = False
        time.sleep(1)
    return video_url, status


def call_luma_api_text_to_video(prompt: str) -> tuple[list[str], bool]:
    task_id = get_luma_job_id(prompt=prompt)
    if task_id == "":
        return [], False
    else:
        video_url, status = retriev_luma_job_by_id(
            task_id=task_id)
        return video_url, status


def call_luma_api_image_to_video(prompt: str, image_url: str) -> tuple[list[str], bool]:
    task_id = get_luma_job_id(prompt=prompt, image_url=image_url)
    print(task_id)
    if task_id == "":
        return [], False
    else:
        video_url, status = retriev_luma_job_by_id(
            task_id=task_id)
        return video_url, status
