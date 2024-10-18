# -*- coding: utf-8 -*-
"""
Traitement automatisé d'image via l'usage d'un modèle de diffusion latente
"""

import torch
from diffusers import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLInpaintPipeline
from diffusers.utils import load_image
from PIL import Image
import glob
import json
import os

from translation import translate
import model_finder as mf

current_model_data ={}
currentPipeLine = StableDiffusionXLImg2ImgPipeline
currentPipeLineStr = "img2img"

with open("config.json", "r") as f:
    config = json.load(f)

def change_pipeline(data):
    print(os.path.abspath(mf.MODELS_PATHS+data["file"]))
    global pipeline, device, current_model_data
    pipeline = currentPipeLine.from_single_file(
        data["model_url"],#os.path.abspath(mf.MODELS_PATHS+data["file"]),
        torch_dtype=torch.float16
    )

    # Set the device (GPU if available, else CPU)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipeline = pipeline.to(device)
    current_model_data = data

#pipeline.load_lora_weights("/home/user/Téléchargements/Flat_Vector_Art_PDXL-000007.safetensors", weight_name="Flat_Vector_Art_PDXL-000007.safetensors", adapter_name="vector") # https://civitai.com/api/download/models/488807?type=Model&format=SafeTensor

change_pipeline(tuple(mf.models.values())[0])

if device == "cuda":
    pipeline.enable_model_cpu_offload()

def resize_image(image, max_size=1024):
    """Resize image while maintaining aspect ratio."""
    width, height = image.size
    if width > height:
        new_width = max_size
        new_height = int((new_width / width) * height)
    else:
        new_height = max_size
        new_width = int((new_height / height) * width)
    new_width = (new_width // 8) * 8
    new_height = (new_height // 8) * 8

    return image.resize((new_width, new_height), Image.LANCZOS), (new_height, new_width)

def get_image_files(directory):
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp', '*.avif']
    return [file for ext in image_extensions for file in glob.glob(f"{directory}/{ext}")]

def transform(image_path, image_path_out, prompt, neg_prompt, strength, model):
    global currentPipeLineStr, currentPipeLine
    if currentPipeLineStr != "img2img":
        currentPipeLineStr = "img2img"
        currentPipeLine = StableDiffusionXLImg2ImgPipeline
        change_pipeline(mf.models[mf.getAllModelsNameAndTag()[model]])
    try:
        init_image = load_image(image_path).convert("RGB")

        init_image = resize_image(init_image, max_size=config["max_size"])[0]

        prompt = "(("+translate(current_model_data.get("hidden_prompt","")+")), "+prompt)
        neg_prompt = "(("+translate(current_model_data.get("hidden_neg_prompt", "")+")), "+neg_prompt)

        image = pipeline(
            prompt,
            image=init_image,
            strength=strength,
            negative_prompt=neg_prompt,
            guidance_scale=6.4,#7.5
            num_inference_steps=30
        ).images[0]

        os.makedirs(os.path.dirname(image_path_out), exist_ok=True)
        image.save(image_path_out)
        print(f"Image saved at {image_path_out}")
        return True

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def inpaint(image_path, image_path_out, mask, prompt, neg_prompt, strength, model):
    global currentPipeLineStr, currentPipeLine

    if currentPipeLineStr != "inpaint":
        currentPipeLineStr = "inpaint"
        currentPipeLine = StableDiffusionXLInpaintPipeline
        change_pipeline(mf.models[mf.getAllModelsNameAndTag()[model]])
    print(currentPipeLineStr)
    try:
        init_image = load_image(image_path).convert("RGB")
        init_image = resize_image(init_image, max_size=config["max_size"])[0]  # Resize image

        init_mask = mask.convert("RGB").resize(init_image.size, Image.LANCZOS)  # Convert mask to RGB if needed

        prompt = "(("+translate(current_model_data.get("hidden_prompt", "") + ")), " + prompt)
        neg_prompt = "(("+translate(current_model_data.get("hidden_neg_prompt", "") + ")), " + neg_prompt)

        image = pipeline(
            prompt=prompt,
            negative_prompt=neg_prompt,
            image=init_image,
            mask_image=init_mask,
            guidance_scale=7,
            strength=strength,
            num_inference_steps=50,
            height=init_image.height,
            width=init_image.width
        ).images[0]

        os.makedirs(os.path.dirname(image_path_out), exist_ok=True)
        image.save(image_path_out)
        print(f"Image saved at {image_path_out}")
        return True

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False
