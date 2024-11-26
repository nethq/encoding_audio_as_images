#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Clone the repository and checkout branch v3
git clone --branch v3 https://github.com/nethq/encoding_audio_as_images.git
cd encoding_audio_as_images/cpp/

# Build the binary using make
make

# Create binaries directory if it doesn't exist
mkdir -p ../../binaries/

# Copy the built binary to the binaries directory
cp bin/steggify ../../binaries/steggify

# Make sure the binary is executable
chmod +x ../../binaries/steggify

# Clean up by removing the cloned repository
cd ../..
rm -rf encoding_audio_as_images
