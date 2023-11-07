import sys
import numpy as np
from PIL import Image
import soundfile as sf

def rgb_to_audio_sample(rgb):
    # Inverse of audio_sample_to_rgb
    #if the rgb value is x,y,z,255 remove 255 and use the x y z
    try:
        x, y, z = rgb
        # Recalculate the original value
        original_value = (x * y) + z
        # Adjust back to the range [-32768, 32767]
        return original_value - 32768
    except:
        print("Error encountered.")

def images_to_audio(images_paths, output_wav_file):
    audio_samples = []
    
    for image_path in images_paths:
        # Load image
        image = Image.open(image_path)
        rgb_data = list(image.getdata())
        
        # Convert RGB data back to audio samples
        for rgb in rgb_data:
            sample = rgb_to_audio_sample(rgb)
            audio_samples.append(sample)
    
    # Convert list to numpy array
    audio_array = np.array(audio_samples, dtype=np.int16)

    # Normalize the audio to the range [-1, 1]
    normalized_audio = audio_array / 32768.0

    # Write the result to a WAV file
    sf.write(output_wav_file, normalized_audio, 48000)  # Using a default sample rate of 44100Hz

    print(f"Audio was reconstructed to {output_wav_file}.")

# Command line argument processing
if len(sys.argv) < 3:
    print("Usage: python image_to_audio.py <output_wav_file> <image_path_1> <image_path_2> ...")
    sys.exit(1)

output_wav_file = sys.argv[1]
image_paths = sys.argv[2:]

# Run the conversion
images_to_audio(image_paths, output_wav_file)
