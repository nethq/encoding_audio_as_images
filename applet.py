import streamlit as st
from PIL import Image
#improt base64
import base64
from PIL import Image
import numpy as np
from functools import partial
from pydub import AudioSegment
import pydub
fill_empty_space_after_data_exhaustion = True

def encode_alpha(value):
    return value

def decode_alpha(value):
    return value

transformation_list = {3:(encode_alpha,decode_alpha)} # a list of tuples (<channel_index>,dynamic_encoding_function,dynamic_decoding_function)

def prepare_mask_operations(global_masking_operation):
    """
    Prepare mask operations to optimize computation in pixel manipulation functions.
    """
    shifts = {'R': 0, 'G': 1, 'B': 2, 'A': 3}
    mask_ops = {}
    for mask_value, shift_amount, channel in global_masking_operation:
        channel_index = shifts[channel]
        mask_ops[channel_index] = (mask_value, shift_amount)
    return mask_ops

def mask_and_embed(pixel, value, mask_ops,transformations = transformation_list):
    """
    Apply a mask to a pixel and embed a value into it using pre-calculated mask operations.
    """
    result_pixel = list(pixel)
    for channel_index, (mask_value, shift_amount) in mask_ops.items():
        # Extract appropriate bits from 'value'
        bits_to_embed = (value >> shift_amount) & mask_value
        # Mask out the bits in the original pixel and embed the new bits
        if channel_index in transformations:
            bits_to_embed = transformations[channel_index][0](bits_to_embed)
        else:
            result_pixel[channel_index] = (pixel[channel_index] & ~mask_value) | bits_to_embed
    return tuple(result_pixel)

def extract_from_mask(pixel, mask_ops,transformations=transformation_list):
    """
    Extract data from a pixel using pre-calculated mask operations.
    """
    extracted_value = 0
    for channel_index, (mask_value, shift_amount) in mask_ops.items():
        # Extract the bits from the pixel and position them correctly in the output value
        bits = (pixel[channel_index] & mask_value) << shift_amount
        if channel_index in transformations:
            bits = transformations[channel_index][1](bits)
        extracted_value |= bits
    return extracted_value

def unified_algorithm_v1(operation, image_filename, mask_scheme, endian='le', output_filename=None, yield_function=None, write_function=None,transformation_functions=transformation_list,fill_empty_space_after_data_exhaustion=True):
    """
    A universal function to handle both embedding (baking) and extracting (debaking) data in/from an image.
    """
    # Load image
    with Image.open(image_filename) as img:
        img_data = np.array(img)

    # Prepare mask operations
    mask_ops = prepare_mask_operations(mask_scheme)
    #for each channel, generate an empty transformation function

    if operation == 'bake':
        if yield_function is None:
            raise ValueError("yield_function must be provided for baking.")
        #if no alpha channel is present, add it
        if img_data.shape[2] == 3:
            img_data = np.dstack((img_data, np.full_like(img_data[:,:,0], 255)))
            print("Alpha channel added to the image data.")
        print("Shape of picture: ", img_data.shape)
        i, j = 0, 0
        for data in yield_function():
            if i >= img_data.shape[0]:
                break  # Stop if we run out of image space
            masked_value = mask_and_embed(img_data[i][j], data, mask_ops,transformation_functions)
            img_data[i][j] = masked_value
            j += 1
            if j >= img_data.shape[1]:
                i += 1
                j = 0
        
        if fill_empty_space_after_data_exhaustion:
            print("Data exhausted. Filling the rest of the image with zeros.")
            while i < img_data.shape[0]:
                img_data[i][j] = (0, 0, 0, 0)
                j += 1
                if j >= img_data.shape[1]:
                    i += 1
                    j = 0
        
        new_img = Image.fromarray(img_data)
        output_filename = output_filename if output_filename else "output_image.png"
        new_img.save(output_filename)
        print(f"Baked image saved as {output_filename}")

    elif operation == 'debake':
        extracted_data = (extract_from_mask(pixel, mask_ops,transformation_functions) for row in img_data for pixel in row)

        if write_function is None:
            raise ValueError("write_function must be provided for debaking.")

        # Use write_function to handle the output of extracted data
        write_function(extracted_data)
        print(f"Extracted data written using the provided write function.")
    else:
        raise ValueError("Unsupported operation specified")

v2_masking = [
    (0b11111111, 0, 'A'), 
    (0b00000011, 8, 'R'), 
    (0b00000111, 10, 'G'), 
    (0b00000111, 13, 'B')
]

# Function to handle baking operation
def bake(image_file, audio_file, masking_scheme):

    def audio_read_yield_function():
        #load the audio file using pydub
        audio_samples = pydub.AudioSegment.from_file(audio_file, format="wav", frame_rate=48000, sample_width=2, channels=1)
        samples = audio_samples.get_array_of_samples()
        for sample in samples:
            yield sample
            
    unified_algorithm_v1("bake",image_file, v2_masking,yield_function=audio_read_yield_function, output_filename="streamlit_temp_baked_image.png")
    # Display the baked image
    st.image("streamlit_temp_baked_image.png", caption="Baked Image", use_column_width=True)
    st.success("Audio baked successfully! Save the image, so that you can upload it for debaking.")
    # Provide a download link for the baked image
    st.markdown(get_image_download_link("streamlit_temp_baked_image.png"), unsafe_allow_html=True)

# Function to handle debaking operation
def debake(image_file, masking_scheme):

    audio_filename = "streamlit_extracted_audio.wav"
    
    def audio_write_function(data):
        audio = AudioSegment(
            data=np.array(list(data), dtype=np.int16).tobytes(),
            sample_width=2,
            frame_rate=48000,
            channels=1  # Mono
        )
        audio.export(audio_filename, format="wav")
        
    #visualise the image
    st.image(image_file, caption="Image to debake", use_column_width=True)
    unified_algorithm_v1("debake",image_file, v2_masking,write_function=audio_write_function)

    st.success("Audio extracted successfully!")
    st.audio(audio_filename, format="audio/wav")

# Function to generate a download link for files
def get_image_download_link(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('utf-8')
    href = f'<a href="data:image/png;base64,{b64}" download="{file_path}">Download baked image</a>'
    return href

# Main function to run the Streamlit app
def main():
    st.title("Unified Algorithm v1 Streamlit App")

    action = st.selectbox("Select action:", ["Bake", "Debake"])

    if action == "Bake":
        st.warning("Its not recommended to use this app to bake, as its under maintenance, but still you can check how it affects the image")
        st.write("Upload an image and an audio file to encode (\'BAKE\') the audio into the image.")
        image_file = st.file_uploader("Upload Image", type=["png"])
        audio_file = st.file_uploader("Upload Audio (WAV)", type=["wav"])

        if st.button("Bake"):
            if image_file and audio_file:
                bake(image_file, audio_file, v2_masking)  # Use v1_masking or v2_masking based on your choice
            else:
                st.warning("Please upload both image and audio files.")

    elif action == "Debake":
        st.write("Upload an image to decode ('DEBAKE\') the audio from the image.")
        image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

        if st.button("Debake"):
            if image_file:
                debake(image_file, v2_masking)  # Use v1_masking or v2_masking based on your choice
            else:
                st.warning("Please upload an image file.")

if __name__ == "__main__":
    main()
