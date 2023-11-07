import sys
import librosa
import numpy as np
from PIL import Image

# Function to convert audio sample to RGB values
def audio_sample_to_rgb(value, max_value):
    # Adjust the value range from [-32768, 32767] to [0, 65535]
    adjusted_value = value + 32768
    
    # Find factors of adjusted_value considering the constraints
    x = int(np.sqrt(adjusted_value))  # x will be the square root, floored
    y = x
    z = adjusted_value - (x * y)  # z will be the remainder

    # Ensure z is positive
    assert z >= 0, "Calculated z-value was negative, which violates the constraints"

    return (x, y, z)

# Function to create images from the WAV file samples
def audio_to_images(audio_samples, file_base_name, image_size):
    num_samples = len(audio_samples)
    num_pixels_per_image = image_size * image_size
    num_full_images = num_samples // num_pixels_per_image
    images = []

    # Process full images
    for i in range(num_full_images):
        start_index = i * num_pixels_per_image
        end_index = start_index + num_pixels_per_image
        rgb_array = [audio_sample_to_rgb(sample, 65535) for sample in audio_samples[start_index:end_index]]
        image = Image.new('RGB', (image_size, image_size))
        image.putdata(rgb_array)
        image_file_name = f"{file_base_name}_{i}.png"
        image.save(image_file_name)
        print(f"Image {i} created and saved as {image_file_name}.")
        images.append(image)

    # Process remaining samples for the last image, if any
    remaining_samples = num_samples % num_pixels_per_image
    if remaining_samples > 0:
        rgb_array = [audio_sample_to_rgb(sample, 65535) for sample in audio_samples[-remaining_samples:]]
        # Fill the rest of the image with black pixels
        rgb_array += [(0, 0, 0)] * (num_pixels_per_image - remaining_samples)
        image = Image.new('RGB', (image_size, image_size))
        image.putdata(rgb_array)
        last_image_file_name = f"{file_base_name}_last.png"
        image.save(last_image_file_name)
        print(f"Last image created and saved as {last_image_file_name}.")
        images.append(image)

    return images

# Main function to load the audio file and convert it to images
def convert_wav_to_images(file_path, image_size):
    # Load the audio file
    audio_data, _ = librosa.load(file_path, sr=None, mono=True)

    # Convert to 16-bit integer values
    int_audio_data = np.int16(audio_data * 32767)

    # Base name for the output images
    file_base_name = file_path.rsplit('.', 1)[0]

    # Create the images
    audio_to_images(int_audio_data, file_base_name, image_size)

# Command line argument processing
if len(sys.argv) != 3:
    print("Usage: python script.py <path_to_wav_file> <image_size>")
    sys.exit(1)

audio_file_path = sys.argv[1]
image_size = int(sys.argv[2])

# Run the conversion
convert_wav_to_images(audio_file_path, image_size)
