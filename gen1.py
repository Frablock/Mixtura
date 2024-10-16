# -*- coding: utf-8 -*-
"""
Traitement automatisé d'image via l'usage d'un modèle de diffusion latente'
"""

from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
import torch
from diffusers.utils import load_image
from PIL import Image
import glob


pipeline = StableDiffusionXLImg2ImgPipeline.from_single_file(
    "/home/user/Documents/Stable Diffusion/stable-diffusion-webui/models/Stable-diffusion/monstercoffeecelsiusMix_v10.safetensors",
    torch_dtype=torch.float16
).to("cuda")

pipeline.enable_model_cpu_offload()

def resize_image(image, max_size=1024):
    width, height = image.size
    if width > height:
        new_width = max_size
        new_height = int((new_width / width) * height)
    else:
        new_height = max_size
        new_width = int((new_height / height) * width)

    return image.resize((new_width, new_height), Image.LANCZOS)

def get_image_files(directory):
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp', '*.avif']
    return [file for ext in image_extensions for file in glob.glob(f"{directory}/{ext}")]

def transform(image_path, image_path_out):

    init_image = load_image(image_path).convert("RGB")

    init_image = resize_image(init_image)


    prompt = "Source_anime, anime style, score_9, score_8_up, score_7_up"

    image = pipeline(prompt, image=init_image, strength=0.4, negative_prompt="porn, nsfw, nude, suggestive, score_3, score_2, score_1, bad quality", sampler='euler-a').images[0] # guidance_scale = 5.0,

    image.save(image_path_out)

image_list = get_image_files("/home/user/Documents/Test_Cours/test_images")
print(image_list)
for img in image_list:
    print("transformation de "+img.split("/")[-1])
    transform(img, "./outputs/"+img.split("/")[-1])
