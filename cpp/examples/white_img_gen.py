import numpy as np
import cv2

# Create a black image with 8K dimensions (7680x4320)
#width, height = 7680, 4320
#width, height = 3840, 2160
width, height = 1920, 1080

image = np.zeros((height, width, 4), dtype=np.uint8)  # 4 channels (RGBA)

# Set alpha channel (A) to 255 (fully opaque)
image[:, :, 3] = 255

image[:, :, 0] = 255 #R
image[:, :, 1] = 255 #G
image[:, :, 2] = 255 #B

# Save the image to a file
output_filename = "image.png"
cv2.imwrite(output_filename, image)

print(f"Image saved as {output_filename}")
