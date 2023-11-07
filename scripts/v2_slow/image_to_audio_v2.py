import sys
import numpy as np
from PIL import Image
import librosa

# Function to convert RGB values back to audio amplitude
def rgb_to_audio(rgb_array, target_max):
    # Initialize an empty list for the audio data
    audio_data = []

    # Convert RGB triplets back to audio values
    for rgb in rgb_array:
        a, b, c = rgb
        # Reverse the heuristic used for audio to RGB conversion
        value = ((a**3 + b**2 + c) % target_max) - 32767
        audio_data.append(value)

    return np.array(audio_data, dtype=np.float32)

# Function to extract RGB triplets from an image
def extract_rgb_from_image(image):
    # Get the pixel data from the image
    rgb_array = list(image.getdata())
    return rgb_array

def images_to_audio_file(image_files, audio_file_name):
    # Initialize an empty list to hold all the audio data
    full_audio_data = []

    # Process each image file
    for file_path in image_files:
        image = Image.open(file_path)
        rgb_array = extract_rgb_from_image(image)
        audio_data = rgb_to_audio(rgb_array, 65534)
        full_audio_data.extend(audio_data)

    # Convert the list of audio data into a numpy array
    full_audio_data = np.array(full_audio_data)

    # Write the numpy array as a .wav file
    librosa.output.write_wav(audio_file_name, full_audio_data, sr=16000)  # Use default sampling rate or a suitable one
    print(f"Audio created and saved as {audio_file_name}.")

# Main script
if len(sys.argv) < 3:
    print("Usage: python script.py <output_path_to_wav_file> <image_file_1> <image_file_2> ...")
    sys.exit(1)

audio_file_path = sys.argv[1]
image_files = sys.argv[2:]

# Run the pipeline
images_to_audio_file(image_files, audio_file_path)
