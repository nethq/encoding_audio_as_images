import sys
import librosa
import numpy as np
from PIL import Image

# Function to convert audio amplitude to RGB values
def audio_to_rgb(audio_data, target_max):
    # Shift audio data to positive values
    shifted_audio_data = audio_data + 32767
    rgb_array = []

    # Generate RGB triplets
    for value in shifted_audio_data:
        # Ensure value is in the range of 0-65534
        value = max(min(value, target_max), 0)
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

def audio_file_to_images(file_path, image_size):
    # Load the audio file
    audio_data, _ = librosa.load(file_path, sr=None, mono=True)

    # Convert audio data to RGB array
    rgb_array = audio_to_rgb(audio_data.astype(np.float32), 65534)

    # Calculate the number of images required
    num_pixels_per_image = image_size * image_size
    num_full_images = len(rgb_array) // num_pixels_per_image

    # Create and save images
    for i in range(num_full_images):
        start_index = i * num_pixels_per_image
        end_index = start_index + num_pixels_per_image
        image = create_image(rgb_array[start_index:end_index], image_size, image_size)
        image_file_name = f"{file_path.rsplit('.', 1)[0]}_{i}.png"
        image.save(image_file_name)
        print(f"Image {i} created and saved as {image_file_name}.")

    # Handle any remaining data to create a smaller image
    remaining_data = len(rgb_array) % num_pixels_per_image
    if remaining_data > 0:
        last_image = create_image(rgb_array[-remaining_data:], remaining_data, 1)
        last_image_file_name = f"{file_path.rsplit('.', 1)[0]}_last.png"
        last_image.save(last_image_file_name)
        print(f"Last image created and saved as {last_image_file_name}.")

# Main script
if len(sys.argv) != 3:
    print("Usage: python script.py <path_to_wav_file> <image_size>")
    sys.exit(1)

audio_file_path = sys.argv[1]
image_size = int(sys.argv[2])

# Check if the provided file is a WAV file
if not audio_file_path.lower().endswith('.wav'):
    print("Error: File is not a WAV audio file.")
    sys.exit(1)

# Check if the image size is valid
if image_size <= 0:
    print("Error: Image size must be a positive integer.")
    sys.exit(1)

# Run the pipeline
audio_file_to_images(audio_file_path, image_size)