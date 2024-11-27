import streamlit as st
import subprocess
import os
from PIL import Image
import tempfile
import platform
import io

# Set global page configuration for better layout
st.set_page_config(
    page_title="Steggify Encoder/Decoder",
    layout="wide",
    initial_sidebar_state="auto",
)

import os
import subprocess
import streamlit as st

# Path to the binary and marker file
BINARY_PATH = "binaries/steggify"
MARKER_FILE = "binaries/setup_complete"

def setup_binary():
    """
    This function compiles the binary if it doesn't exist.
    It runs only once during deployment by checking the presence of a marker file.
    """
    # Check if setup has already been completed
    if os.path.exists(MARKER_FILE):
        st.info("Setup has already been completed.")
        return
    
    try:
        st.info("Setting up the binary. This may take a few minutes...")
        # Create binaries directory if it doesn't exist
        os.makedirs("binaries", exist_ok=True)

        # Clone the repository
        if not os.path.exists("encoding_audio_as_images"):
            subprocess.run(
                ["git", "clone", "--branch", "v3", "https://github.com/nethq/encoding_audio_as_images.git"],
                check=True,
                text=True
            )

        # Change directory and compile
        os.chdir("encoding_audio_as_images/cpp")
        subprocess.run(["make"], check=True, text=True)

        # Move the compiled binary to binaries directory
        #check if compilation has returned any file under bin, by getting all files under bin, and if its only one and its executable, send it to binaries/steggify
        files = os.listdir("bin")
        if len(files) != 1:
            raise RuntimeError("Compilation failed. No binary found.")
        if not os.access(f"bin/{files[0]}", os.X_OK):
            raise RuntimeError("Compiled binary is not executable.")
        subprocess.run(["mv", f"bin/{files[0]}", "../../binaries/steggify"], check=True)
        
        # Mark as executable
        os.chdir("../../")
        
        os.chmod(BINARY_PATH, 0o755)

        # Create marker file to indicate successful setup
        with open(MARKER_FILE, "w") as f:
            f.write("Setup completed successfully.")

        # Cleanup cloned repository to save space
        subprocess.run(["rm", "-rf", "encoding_audio_as_images"], check=True)

        st.success("Binary setup completed successfully!")

    except subprocess.CalledProcessError as e:
        st.error(f"Error during setup: {e}")
        raise RuntimeError("Setup failed. Please check the logs.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        raise RuntimeError("Unexpected error during setup.")

# Ensure the binary is set up before starting the app
if not os.path.exists(BINARY_PATH):
    setup_binary()
elif not os.access(BINARY_PATH, os.X_OK):
    st.error(f"The binary at {BINARY_PATH} is not executable. Please check the setup.")

st.title("Streamlit App with On-Demand Binary Setup")
st.write("If the binary is not present, it will be built automatically during the first deployment.")


# Determine the correct binary based on system architecture
try:
    STEGGIFY_PATH = os.path.join(os.getcwd(), "binaries/steggify")
except Exception as e:
    st.error(f"Error determining system architecture: {e}")
    st.stop()

# Check if the binary exists and is executable
if not os.path.isfile(STEGGIFY_PATH):
    st.error(f"'steggify' binary not found at {STEGGIFY_PATH}. It should be built during deployment.")
    st.stop()

if not os.access(STEGGIFY_PATH, os.X_OK):
    st.error(f"'steggify' binary at {STEGGIFY_PATH} is not executable. Please check the build process.")
    st.stop()

def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        st.error("The 'steggify' binary was not found. Please ensure it is correctly built.")
        return None
    except subprocess.CalledProcessError as e:
        st.error(f"Error during execution: {e.stderr}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

def validate_masks(masks):
    for mask in masks:
        if len(mask) != 8 or not all(c in '01' for c in mask):
            return False
    return True

def encode_image(input_image_path, input_data_path, masks, order, output_image_path):
    try:
        command = [
            STEGGIFY_PATH,
            "encode",
            "-i", input_image_path,
            "-d", input_data_path,
            "-m", masks[0], masks[1], masks[2], masks[3],
            "-o", output_image_path,
            "-r", order
        ]

        st.info("Encoding data into image...")
        output = run_command(command)
        if output:
            st.success("Encoding successful.")
            st.text(output)
            if os.path.isfile(output_image_path):
                try:
                    encoded_image = Image.open(output_image_path)
                    # Resize image to take up ~60% of horizontal space
                    st.image(encoded_image, caption="Encoded Image", use_column_width=False)
                except Exception as img_e:
                    st.error(f"Failed to load encoded image: {img_e}")
                with open(output_image_path, "rb") as file:
                    st.download_button(
                        label="Download Encoded Image",
                        data=file,
                        file_name=os.path.basename(output_image_path),
                        mime="image/png"
                    )
    except Exception as e:
        st.error(f"Failed to encode image: {e}")

def decode_image(input_image_path, masks, order, output_file_path):
    try:
        command = [
            STEGGIFY_PATH,
            "decode",
            "-i", input_image_path,
            "-m", masks[0], masks[1], masks[2], masks[3],
            "-o", output_file_path,
            "-r", order
        ]

        st.info("Decoding data from image...")
        output = run_command(command)
        if output:
            st.success("Decoding successful.")
            st.text(output)
            if os.path.isfile(output_file_path):
                if output_file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    try:
                        decoded_image = Image.open(output_file_path)
                        st.image(decoded_image, caption="Decoded Image", use_column_width=False)
                    except Exception as img_e:
                        st.error(f"Failed to load decoded image: {img_e}")
                else:
                    try:
                        with open(output_file_path, "rb") as file:
                            decoded_data = file.read()
                            try:
                                decoded_text = decoded_data.decode('utf-8')
                                st.text_area("Decoded Data", decoded_text, height=200)
                            except UnicodeDecodeError:
                                st.download_button(
                                    label="Download Decoded File",
                                    data=decoded_data,
                                    file_name=os.path.basename(output_file_path),
                                    mime="application/octet-stream"
                                )
                    except Exception as file_e:
                        st.error(f"Failed to read decoded file: {file_e}")
    except Exception as e:
        st.error(f"Failed to decode image: {e}")

def create_white_image():
    try:
        img = Image.new('RGBA', (600, 600), color=(255, 255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.name = "white_image.png"
        buf.seek(0)
        return buf
    except Exception as e:
        st.error(f"Error creating white image: {e}")
        return None

st.title("Steggify Encoder/Decoder")

tab1, tab2, tab3 = st.tabs(["Encode", "Decode", "Demo"])

with tab1:
    st.header("Encode Data into Image")
    with st.form("encode_form"):
        input_image = st.file_uploader("Upload Input Image", type=["png", "jpg", "jpeg", "bmp"])
        input_data = st.file_uploader("Upload Data File to Encode", type=["txt", "csv", "json", "bin", "mp3", "wav"])
        st.markdown("### Masks (8-bit binary)")
        col1, col2 = st.columns(2)
        with col1:
            mask_r = st.text_input("Mask for Red Channel", value="00001111")
            mask_g = st.text_input("Mask for Green Channel", value="00001111")
        with col2:
            mask_b = st.text_input("Mask for Blue Channel", value="00001111")
            mask_a = st.text_input("Mask for Alpha Channel", value="00001111")
        order = st.selectbox("Channel Order", options=["ARGB", "RGBA", "BGRA", "ABGR", "ARBG"])
        output_image = st.text_input("Output Image Filename", value="encoded_image.png")
        submit_encode = st.form_submit_button("Encode")

    if submit_encode:
        if input_image and input_data:
            masks = [mask_r, mask_g, mask_b, mask_a]
            if not validate_masks(masks):
                st.error("All masks must be 8-bit binary strings (e.g., '00001111').")
            else:
                try:
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(input_image.name)[1]) as tmp_img:
                        tmp_img.write(input_image.read())
                        tmp_img_path = tmp_img.name

                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(input_data.name)[1]) as tmp_data:
                        tmp_data.write(input_data.read())
                        tmp_data_path = tmp_data.name

                    output_path = os.path.join(tempfile.gettempdir(), output_image)

                    encode_image(tmp_img_path, tmp_data_path, masks, order, output_path)

                except Exception as e:
                    st.error(f"An unexpected error occurred during encoding: {e}")
        else:
            st.error("Please upload both an input image and a data file.")

with tab2:
    st.header("Decode Data from Image")
    with st.form("decode_form"):
        input_image = st.file_uploader("Upload Encoded Image", type=["png", "jpg", "jpeg", "bmp"])
        st.markdown("### Masks (8-bit binary)")
        col1, col2 = st.columns(2)
        with col1:
            mask_r = st.text_input("Mask for Red Channel", value="00001111")
            mask_g = st.text_input("Mask for Green Channel", value="00001111")
        with col2:
            mask_b = st.text_input("Mask for Blue Channel", value="00001111")
            mask_a = st.text_input("Mask for Alpha Channel", value="00001111")
        order = st.selectbox("Channel Order", options=["ARGB", "RGBA", "BGRA", "ABGR", "ARBG"])
        output_file = st.text_input("Output File Filename", value="decoded_data.bin")
        submit_decode = st.form_submit_button("Decode")

    if submit_decode:
        if input_image:
            masks = [mask_r, mask_g, mask_b, mask_a]
            if not validate_masks(masks):
                st.error("All masks must be 8-bit binary strings (e.g., '00001111').")
            else:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(input_image.name)[1]) as tmp_img:
                        tmp_img.write(input_image.read())
                        tmp_img_path = tmp_img.name

                    output_path = os.path.join(tempfile.gettempdir(), output_file)

                    decode_image(tmp_img_path, masks, order, output_path)

                except Exception as e:
                    st.error(f"An unexpected error occurred during decoding: {e}")
        else:
            st.error("Please upload an encoded image.")

with tab3:
    st.header("Demo")
    st.write("Provide text or upload a file to encode into a white image, then decode it back.")

    demo_input_type = st.radio("Choose Input Type", ("Text", "File"))

    if demo_input_type == "Text":
        demo_text = st.text_area("Enter text to encode", "Sample text for Steggify encoding.")
        st.markdown("### Customize Masks and Channel Order")
        customize_demo = st.checkbox("Customize Masks and Channel Order")
        if customize_demo:
            col1, col2 = st.columns(2)
            with col1:
                demo_mask_r = st.text_input("Mask for Red Channel", value="00001111")
                demo_mask_g = st.text_input("Mask for Green Channel", value="00001111")
            with col2:
                demo_mask_b = st.text_input("Mask for Blue Channel", value="00001111")
                demo_mask_a = st.text_input("Mask for Alpha Channel", value="00001111")
            demo_order = st.selectbox("Channel Order", options=["ARGB", "RGBA", "BGRA", "ABGR", "ARBG"], index=0)
            demo_masks = [demo_mask_r, demo_mask_g, demo_mask_b, demo_mask_a]
        else:
            demo_masks = ["00001111", "00001111", "00001111", "00001111"]
            demo_order = "ARGB"

        if st.button("Run Demo"):
            if demo_text.strip():
                if not validate_masks(demo_masks):
                    st.error("All masks must be 8-bit binary strings (e.g., '00001111').")
                else:
                    try:
                        masks = demo_masks
                        order = demo_order
                        output_image = "demo_encoded.png"
                        output_file = "demo_decoded.txt"

                        # Create white image
                        white_image = create_white_image()
                        if white_image is None:
                            st.error("Failed to create sample white image.")
                        else:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_white_img:
                                tmp_white_img.write(white_image.read())
                                tmp_white_img_path = tmp_white_img.name

                            # Save demo text to temporary file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_data:
                                tmp_data.write(demo_text.encode('utf-8'))
                                tmp_data_path = tmp_data.name

                            # Define output path
                            output_path = os.path.join(tempfile.gettempdir(), output_image)

                            # Encode
                            encode_image(tmp_img_path=tmp_white_img_path, 
                                         input_data_path=tmp_data_path, 
                                         masks=masks, 
                                         order=order, 
                                         output_image_path=output_path)

                            # Decode
                            decoded_output_path = os.path.join(tempfile.gettempdir(), output_file)
                            decode_image(input_image_path=output_path, 
                                         masks=masks, 
                                         order=order, 
                                         output_file_path=decoded_output_path)

                            # Read decoded text
                            if os.path.isfile(decoded_output_path):
                                try:
                                    with open(decoded_output_path, "r") as f:
                                        decoded_text = f.read()
                                        st.text_area("Decoded Text", decoded_text, height=200)
                                except Exception as read_e:
                                    st.error(f"Failed to read decoded text: {read_e}")
                            else:
                                st.error("Decoded file not found.")

                            # Display encoded image
                            if os.path.isfile(output_path):
                                try:
                                    encoded_image = Image.open(output_path)
                                    st.image(encoded_image, caption="Encoded Image", use_column_width=False)
                                except Exception as img_e:
                                    st.error(f"Failed to load encoded image: {img_e}")
                            else:
                                st.error("Encoded image not found.")

                            # Cleanup
                            try:
                                os.remove(tmp_white_img_path)
                                os.remove(tmp_data_path)
                                if os.path.exists(output_path):
                                    os.remove(output_path)
                                if os.path.exists(decoded_output_path):
                                    os.remove(decoded_output_path)
                            except Exception as cleanup_e:
                                st.warning(f"Failed to clean up temporary files: {cleanup_e}")
                    except Exception as e:
                        st.error(f"Demo failed: {e}")
            else:
                st.error("Please enter some text to encode.")

    else:
        demo_file = st.file_uploader("Upload a file to encode", type=["txt", "csv", "json", "bin", "mp3", "wav"])
        st.markdown("### Customize Masks and Channel Order")
        customize_demo_file = st.checkbox("Customize Masks and Channel Order")
        if customize_demo_file:
            col1, col2 = st.columns(2)
            with col1:
                demo_mask_r = st.text_input("Mask for Red Channel", value="00001111")
                demo_mask_g = st.text_input("Mask for Green Channel", value="00001111")
            with col2:
                demo_mask_b = st.text_input("Mask for Blue Channel", value="00001111")
                demo_mask_a = st.text_input("Mask for Alpha Channel", value="00001111")
            demo_order = st.selectbox("Channel Order", options=["ARGB", "RGBA", "BGRA", "ABGR", "ARBG"], index=0)
            demo_masks = [demo_mask_r, demo_mask_g, demo_mask_b, demo_mask_a]
        else:
            demo_masks = ["00001111", "00001111", "00001111", "00001111"]
            demo_order = "ARGB"

        if st.button("Run Demo"):
            if demo_file:
                if not validate_masks(demo_masks):
                    st.error("All masks must be 8-bit binary strings (e.g., '00001111').")
                else:
                    try:
                        masks = demo_masks
                        order = demo_order
                        output_image = "demo_encoded.png"
                        output_file = "demo_decoded" + os.path.splitext(demo_file.name)[1]

                        # Create white image
                        white_image = create_white_image()
                        if white_image is None:
                            st.error("Failed to create sample white image.")
                        else:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_white_img:
                                tmp_white_img.write(white_image.read())
                                tmp_white_img_path = tmp_white_img.name

                            # Save uploaded file to temporary file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(demo_file.name)[1]) as tmp_data:
                                tmp_data.write(demo_file.read())
                                tmp_data_path = tmp_data.name

                            # Define output path
                            output_path = os.path.join(tempfile.gettempdir(), output_image)

                            # Encode
                            encode_image(tmp_img_path=tmp_white_img_path, 
                                         input_data_path=tmp_data_path, 
                                         masks=masks, 
                                         order=order, 
                                         output_image_path=output_path)

                            # Decode
                            decoded_output_path = os.path.join(tempfile.gettempdir(), output_file)
                            decode_image(input_image_path=output_path, 
                                         masks=masks, 
                                         order=order, 
                                         output_file_path=decoded_output_path)

                            # Provide download button for decoded file
                            if os.path.isfile(decoded_output_path):
                                try:
                                    with open(decoded_output_path, "rb") as f:
                                        decoded_data = f.read()
                                        st.download_button(
                                            label="Download Decoded File",
                                            data=decoded_data,
                                            file_name=output_file,
                                            mime="application/octet-stream"
                                        )
                                except Exception as read_e:
                                    st.error(f"Failed to read decoded file: {read_e}")
                            else:
                                st.error("Decoded file not found.")

                            # Display encoded image
                            if os.path.isfile(output_path):
                                try:
                                    encoded_image = Image.open(output_path)
                                    st.image(encoded_image, caption="Encoded Image", use_column_width=False)
                                except Exception as img_e:
                                    st.error(f"Failed to load encoded image: {img_e}")
                            else:
                                st.error("Encoded image not found.")

                            # Cleanup
                            try:
                                os.remove(tmp_white_img_path)
                                os.remove(tmp_data_path)
                                if os.path.exists(output_path):
                                    os.remove(output_path)
                                if os.path.exists(decoded_output_path):
                                    os.remove(decoded_output_path)
                            except Exception as cleanup_e:
                                st.warning(f"Failed to clean up temporary files: {cleanup_e}")
                    except Exception as e:
                        st.error(f"Demo failed: {e}")
            else:
                st.error("Please upload a file to encode.")
