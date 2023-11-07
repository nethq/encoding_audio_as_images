import sys
import librosa
import numpy as np
from PIL import Image

# Function to convert audio amplitude to RGB values
def audio_to_rgb(audio_data, target_min, target_max):
    # Normalize and scale audio data to the target range
    norm_audio_data = np.interp(audio_data, (audio_data.min(), audio_data.max()), (target_min, target_max))
    rgb_array = []

    # Generate RGB triplets
    for value in norm_audio_data:
        # Ensure value is in the range of 0-255
        value = max(min(value, target_max), target_min)
        # Simple heuristic to convert a value into an RGB triplet
        a = int(np.cbrt(value)) % 256
        b = int(np.sqrt(value)) % 256
        c = int(value) % 256
        rgb_array.append((a, b, c))

    return rgb_array

# Function to create an image from RGB triplets
def create_image(rgb_array, width, height):
    # If the number of RGB triplets is not enough to fill the image, repeat the array
    num_pixels = width * height
    extended_rgb_array = rgb_array * (num_pixels // len(rgb_array)) + rgb_array[:num_pixels % len(rgb_array)]
    
    # Create image
    image = Image.new('RGB', (width, height))
    image.putdata(extended_rgb_array)
    return image

def audio_file_to_image(file_path):
    # Load the audio file
    audio_data, _ = librosa.load(file_path, sr=None, mono=True)

    # Convert audio data to RGB array
    rgb_array = audio_to_rgb(audio_data, 0, 255)

    # Define image dimensions
    # We'll make the width proportional to the square root of the number of RGB triplets,
    # and set the height to fit all data points.
    image_width = int(np.sqrt(len(rgb_array)))
    image_height = len(rgb_array) // image_width

    # Create the image from the RGB array
    image = create_image(rgb_array, image_width, image_height)

    # Save the image using the same base name as the audio file but with .png extension
    image_file_name = f"{file_path.rsplit('.', 1)[0]}.png"
    image.save(image_file_name)
    print(f"Image created and saved as {image_file_name}.")

# Get the audio file path from the command line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <path_to_wav_file>")
    sys.exit(1)

audio_file_path = sys.argv[1]

# Check if the provided file is a WAV file
if not audio_file_path.lower().endswith('.wav'):
    print("Error: File is not a WAV audio file.")
    sys.exit(1)

# Run the pipeline
audio_file_to_image(audio_file_path)
