import asyncio
from random import randint
from PIL import Image, UnidentifiedImageError
import requests
from dotenv import dotenv_values
import os
from time import sleep
import io
import json

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")

    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening Image: {image_path}")
            img.show()
            sleep(1)

        except IOError:
            print(f"Unable to open {image_path}")

# 🔑 Load API Key
env = dotenv_values(".env")
HF_API_KEY = env.get("HuggingFaceAPIKey")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# ✅ Helper: check if bytes are image
def is_image(content: bytes) -> bool:
    try:
        Image.open(io.BytesIO(content)).verify()
        return True
    except UnidentifiedImageError:
        return False

async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

async def genrate_images(prompt: str):
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality-4K, sharpness-maximum, ultra high details, high resolution, seed={randint(0,1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_byte_list = await asyncio.gather(*tasks)

    for i, image_byte in enumerate(image_byte_list):
        file_name = fr"Data\{prompt.replace(' ', '_')}{i+1}.jpg"
        if is_image(image_byte):
            with open(file_name, "wb") as f:
                f.write(image_byte)
            print(f"✅ Saved {file_name}")
        else:
            # Save error logs instead of broken jpgs
            error_log = fr"Data\{prompt.replace(' ', '_')}{i+1}_error.json"
            with open(error_log, "wb") as f:
                f.write(image_byte)
            print(f"⚠️ API returned error, saved at {error_log}")

def GenrateImages(prompt: str):
    asyncio.run(genrate_images(prompt))
    sleep(1)
    open_images(prompt)

while True:
    try:
        with open(r"Frontend\Files\ImageGenration.data", "r") as f:
            Data: str = f.read()

        Prompt, Status = Data.split(",")

        if Status == "True":
            print("Generating Image...")
            GenrateImages(prompt=Prompt)

            with open(r"Frontend\Files\ImageGenration.data", "w") as f:
                f.write("False,False")
            break

        else:
            sleep(1)

    except Exception as e:
        print(f"Loop Error: {e}")
        sleep(1)
