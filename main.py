# Imports
import io
import os
import numpy as np
import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from PIL import Image
from torchvision import transforms
from skimage.color import rgb2lab, lab2rgb
from model import Unet
import tensorflow as tf
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# Load PyTorch model for colorization
generator_colorize = Unet(input_c=1, output_c=2, n_down=8, num_filters=64)
generator_colorize.load_state_dict(torch.load('models/galaxy_colorization.pth', map_location='cpu'))
generator_colorize.eval()
device = torch.device("cpu")

# Constants for image processing
SIZE = 256  # Desired image size for the colorization process
L_CHANNEL_DIR = 'Database/L_channel_Images'  # Directory to store L channel images
RGB_DIR = 'Database/RGB_Generated_Images'     # Directory to store colorized RGB images
GALAXY_DIR = 'Database/Generated_Galaxy_Images'  # Directory to store generated galaxy images
NUM_IMAGES = 1  # Number of images to generate
NOISE_DIM = 100  # Dimension of the noise input for the GAN

# Create directories if they don't exist
os.makedirs(L_CHANNEL_DIR, exist_ok=True)
os.makedirs(RGB_DIR, exist_ok=True)
os.makedirs(GALAXY_DIR, exist_ok=True)

def lab_to_rgb(L, ab):
    """
    Convert L and ab channels from Lab color space to RGB color space.
    
    Args:
        L (Tensor): L channel tensor.
        ab (Tensor): ab channel tensor.
    
    Returns:
        np.ndarray: RGB images in numpy array format.
    """
    # Scale L and ab channels to proper ranges
    L = (L + 1) * 50
    ab = (ab + 1) * 255 / 2 - 128
    Lab = torch.cat([L, ab], dim=1).permute(0, 2, 3, 1).cpu().numpy()
    rgb_imgs = []
    for img in Lab:
        img_rgb = lab2rgb(img)  # Convert to RGB using skimage
        rgb_imgs.append(img_rgb)
    return np.stack(rgb_imgs, axis=0)

def colorize_image(image: Image.Image):
    """
    Colorizes the input image using a pre-trained model and saves the L channel and RGB outputs.
    
    Args:
        image (Image.Image): The input image to be colorized.
    
    Returns:
        Tuple[np.ndarray, np.ndarray]: L channel and RGB colorized image as numpy arrays.
    """
    # Convert image to RGB and center crop to SIZE
    img = image.convert("RGB")
    img = transforms.Compose([transforms.CenterCrop(SIZE)])(img)
    img = np.array(img)

    # Convert RGB image to Lab color space
    img_lab = rgb2lab(img).astype("float32")
    img_lab = transforms.ToTensor()(img_lab)

    # Normalize L channel
    L = img_lab[[0], ...] / 50. - 1.
    L = L.unsqueeze(0)  # Add batch dimension

    # Predict ab channels using the generator model
    ab = generator_colorize(L.to(device))
    
    # Convert L and ab channels to RGB
    rgb_out = lab_to_rgb(L.to(device), ab.detach().to(device))

    # Squeeze and scale RGB output to uint8
    rgb_out = rgb_out.squeeze(0)
    rgb_out = (rgb_out * 255).astype(np.uint8)

    # Create a timestamp for the filename
    current_time = datetime.now().strftime("%d%m%Y_%H%M")  # Format: DDMMYYYY_HHMM

    # Save L channel and RGB output with timestamps
    l_channel_image = (L.squeeze().cpu().numpy() + 1) * 127.5  # Scale L channel to 0-255
    l_channel_image = np.clip(l_channel_image, 0, 255).astype(np.uint8)  # Ensure values are within valid range

    # Save images to respective directories
    Image.fromarray(l_channel_image).save(os.path.join(L_CHANNEL_DIR, f'L_channel_{current_time}.png'))
    Image.fromarray(rgb_out).save(os.path.join(RGB_DIR, f'RGB_generated_{current_time}.png'))

    return L.squeeze().cpu().numpy(), rgb_out

@app.post("/colorize/")
async def colorize(file: UploadFile = File(...)):
    """
    Endpoint to colorize an uploaded image file.
    
    Args:
        file (UploadFile): The image file to colorize.
    
    Returns:
        StreamingResponse: Colorized image in PNG format.
    """
    # Read the uploaded image file
    image = Image.open(io.BytesIO(await file.read()))
    L_channel, colorized_image = colorize_image(image)  # Perform colorization

    # Prepare the colorized image for response
    img_byte_arr = io.BytesIO()
    Image.fromarray(colorized_image).save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")

# Load your GAN model for galaxy generation
generate_galaxy = tf.keras.models.load_model('models/generate_galaxy.h5')

@app.post("/generate/")
async def generate():
    """
    Endpoint to generate a galaxy image using a GAN model.
    
    Returns:
        FileResponse: The latest generated galaxy image in PNG format.
    """
    # Generate random noise for the GAN
    test_noise = tf.random.normal([NUM_IMAGES, NOISE_DIM])
    
    # Generate an image using the generator model
    prediction = generate_galaxy.predict(test_noise)

    # Get the generated image and resize it to (256, 256, 1)
    generated_image = prediction[0]  # Shape should be (128, 128, 1)
    generated_image_resized = tf.image.resize(generated_image, (256, 256)).numpy()  # Resize to (256, 256, 1)

    # Create a timestamp for the filename
    current_time = datetime.now().strftime("%d%m%Y_%H%M")  # Format: DDMMYYYY_HHMM

    # Generate unique filename for the new galaxy image
    galaxy_image_name = f'generated_galaxy_image_{current_time}.png'
    galaxy_image_path = os.path.join(GALAXY_DIR, galaxy_image_name)

    # Save the generated galaxy image as a PNG file
    plt.imsave(galaxy_image_path, generated_image_resized.squeeze(-1), cmap='gray', format='png')

    # Prepare the response by returning the latest image from the directory
    last_galaxy_image_path = sorted(os.listdir(GALAXY_DIR))[-1]  # Get the most recent file
    return FileResponse(os.path.join(GALAXY_DIR, last_galaxy_image_path))
