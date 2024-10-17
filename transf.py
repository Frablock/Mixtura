# -*- coding: utf-8 -*-
"""
Traitement automatisé d'image via l'usage d'un modèle de diffusion latente
"""

import torch
from diffusers import StableDiffusionXLImg2ImgPipeline
from diffusers.utils import load_image
from PIL import Image
import glob
import json
import os

# Load config file
with open("config.json", "r") as f:
    config = json.load(f)

# Load the model
pipeline = StableDiffusionXLImg2ImgPipeline.from_single_file(
    config['base_model'],
    torch_dtype=torch.float16
)

# Set the device (GPU if available, else CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipeline = pipeline.to(device)

pipeline.load_lora_weights("/home/user/Téléchargements/Flat_Vector_Art_PDXL-000007.safetensors", weight_name="Flat_Vector_Art_PDXL-000007.safetensors", adapter_name="vector") # https://civitai.com/api/download/models/488807?type=Model&format=SafeTensor

# Enable model offload if CUDA is available
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

    return image.resize((new_width, new_height), Image.LANCZOS)

def get_image_files(directory):
    """Return all image files from the specified directory."""
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp', '*.avif']
    return [file for ext in image_extensions for file in glob.glob(f"{directory}/{ext}")]

def transform(image_path, image_path_out):
    """Transform an image using the Stable Diffusion pipeline."""
    try:
        init_image = load_image(image_path).convert("RGB")

        init_image = resize_image(init_image, max_size=config["max_size"])

        # Prompt and negative prompt from config
        prompt = config["base_prompt"]
        prompt = "(a flat style vector illustration, vztdzsxx,flat color, vector art, illustration, vector illustration, cel shading, simple coloring,)"
        neg_prompt = config["neg_prompt"]

        # Perform the transformation
        image = pipeline(
            prompt,
            image=init_image,
            strength=config["strength"],
            negative_prompt=neg_prompt,
            guidance_scale=7.5,  # Optional for better control
            num_inference_steps=30
        ).images[0]

        # Save the transformed image
        os.makedirs(os.path.dirname(image_path_out), exist_ok=True)
        image.save(image_path_out)
        print(f"Image saved at {image_path_out}")
        return True

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

# Uncomment to process multiple images from a directory
"""
image_list = get_image_files("/home/user/Documents/Test_Cours/test_images")
print(image_list)
for img in image_list:
    print(f"Transformation de {img.split('/')[-1]}")
    transform(img, f"./outputs/{os.path.basename(img)}")
"""
