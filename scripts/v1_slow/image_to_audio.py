import sys
import numpy as np
from PIL import Image
import soundfile as sf

# Function to convert RGB triplets back to audio values
def rgb_to_audio(rgb_array, target_min, target_max):
    # Reverse the process of audio_to_rgb
    audio_data = []
    for r, g, b in rgb_array:
        # Heuristic to approximate the original value
        value = r * g * b
        audio_data.append(value)
    
    # Normalize the approximated values to the target range
    norm_audio_data = np.interp(audio_data, (min(audio_data), max(audio_data)), (target_min, target_max))
    return norm_audio_data

# Function to load an image and extract RGB triplets
def image_to_rgb_array(image_path):
    # Open the image
    image = Image.open(image_path)
    # Get the RGB values
    rgb_array = list(image.getdata())
    return rgb_array

def image_to_audio_file(image_path, sample_rate):
    # Load the RGB values from the image
    rgb_array = image_to_rgb_array(image_path)

    # Convert RGB array to audio data
    audio_data = rgb_to_audio(rgb_array, -1, 1)  # Normalize audio to -1 to 1 for wav file

    # Save the audio data to a WAV file
    audio_file_name = f"{image_path.rsplit('.', 1)[0]}.wav"
    sf.write(audio_file_name, audio_data, sample_rate)
    print(f"Audio created and saved as {audio_file_name}.")

# Get the image file path from the command line argument
if len(sys.argv) != 2:
    print("Usage: python script.py <path_to_image_file>")
    sys.exit(1)

image_file_path = sys.argv[1]

# Check if the provided file is an image file
if not image_file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
    print("Error: File is not a supported image file.")
    sys.exit(1)

# Set the sample rate
sample_rate = 16000

# Run the pipeline
image_to_audio_file(image_file_path, sample_rate)
