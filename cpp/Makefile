# =====================================================
# Makefile for Steggify Project with Cross-Compilation
# =====================================================

# =======================
# Configuration Variables
# =======================

# Source file
TARGET_SRC = steggify.cpp

# Base name for the compiled binary
BASE_BINARY = steggify

# Compiler for native compilation
COMPILER = g++

# Compiler flags for native compilation
CFLAGS = -std=c++17 -O3 -I./include -I./headers

# Output directories
BIN_DIR = bin
RESULTS_DIR = results

# Paths and parameters
image_path = "examples/image.png"
pixel_format = "ARBG"

r_mask = "00001111"
g_mask = "00001111"
b_mask = "00001111"
a_mask = "00001111"

encoded_image_path = "results/hidden.png"
audio_path = "examples/bg3_mt.mp3"
decoded_image_path = "results/decoded.$(shell echo $(audio_path) | awk -F . '{print $$NF}')"

# =======================
# Cross-Compilation Variables
# =======================

# List of all cross-compilation targets
CROSS_ARCHS = windows32 windows64 linux32 linux64

# Cross-compiler definitions
# Windows 32-bit
WINDOWS32_CC = i686-w64-mingw32-g++
WINDOWS32_EXT = .exe

# Windows 64-bit
WINDOWS64_CC = x86_64-w64-mingw32-g++
WINDOWS64_EXT = .exe

# Linux 32-bit
LINUX32_CC = g++
LINUX32_FLAGS = -m32

# Linux 64-bit
LINUX64_CC = g++
LINUX64_FLAGS = -m64

# =======================
# Default Target
# =======================

.PHONY: all
all: compile

# =======================
# Native Compilation Target
# =======================

.PHONY: compile
compile:
	@echo "Compiling for native architecture..."
	@echo "image_path: $(image_path)"
	@echo "audio_path: $(audio_path)"
	@echo "r_mask: $(r_mask)"
	@echo "g_mask: $(g_mask)"
	@echo "b_mask: $(b_mask)"
	@echo "a_mask: $(a_mask)"
	@echo "encoded_image_path: $(encoded_image_path)"
	@echo "decoded_image_path: $(decoded_image_path)"
	@echo "target: $(TARGET_SRC)"
	@echo "compiled_binary: $(BASE_BINARY)"
	@echo "compiler: $(COMPILER)"
	@mkdir -p $(BIN_DIR)
	$(COMPILER) $(CFLAGS) $(TARGET_SRC) -o $(BIN_DIR)/$(BASE_BINARY)
	$(info Built $(BIN_DIR)/$(BASE_BINARY))

# =======================
# Cross-Compilation Targets
# =======================

.PHONY: crosscompile_all $(CROSS_ARCHS)
crosscompile_all: $(CROSS_ARCHS)

# Windows 32-bit
windows32:
	@echo "Cross-compiling for Windows 32-bit..."
	@mkdir -p $(BIN_DIR)
	$(WINDOWS32_CC) $(CFLAGS) $(TARGET_SRC) -o $(BIN_DIR)/$(BASE_BINARY)_windows32$(WINDOWS32_EXT)
	@echo "Built $(BIN_DIR)/$(BASE_BINARY)_windows32$(WINDOWS32_EXT)"

# Windows 64-bit
windows64:
	@echo "Cross-compiling for Windows 64-bit..."
	@mkdir -p $(BIN_DIR)
	$(WINDOWS64_CC) $(CFLAGS) $(TARGET_SRC) -o $(BIN_DIR)/$(BASE_BINARY)_windows64$(WINDOWS64_EXT)
	@echo "Built $(BIN_DIR)/$(BASE_BINARY)_windows64$(WINDOWS64_EXT)"

# Linux 32-bit
linux32:
	@echo "Cross-compiling for Linux 32-bit..."
	@mkdir -p $(BIN_DIR)
	$(LINUX32_CC) $(CFLAGS) $(LINUX32_FLAGS) $(TARGET_SRC) -o $(BIN_DIR)/$(BASE_BINARY)_linux32
	@echo "Built $(BIN_DIR)/$(BASE_BINARY)_linux32"

# Linux 64-bit
linux64:
	@echo "Cross-compiling for Linux 64-bit..."
	@mkdir -p $(BIN_DIR)
	$(LINUX64_CC) $(CFLAGS) $(LINUX64_FLAGS) $(TARGET_SRC) -o $(BIN_DIR)/$(BASE_BINARY)_linux64
	@echo "Built $(BIN_DIR)/$(BASE_BINARY)_linux64"

# =======================
# Encode Target
# =======================

.PHONY: encode
encode:
	@read -p "Enter image path (default: $(image_path)): " img_path; \
	read -p "Enter audio path (default: $(audio_path)): " aud_path; \
	read -p "Enter encoded image path (default: $(encoded_image_path)): " enc_img_path; \
	read -p "Enter pixel format (default: $(pixel_format)): " pix_format; \
	read -p "Enter r_mask (default: $(r_mask)): " r_msk; \
	read -p "Enter g_mask (default: $(g_mask)): " g_msk; \
	read -p "Enter b_mask (default: $(b_mask)): " b_msk; \
	read -p "Enter a_mask (default: $(a_mask)): " a_msk; \
	./$(BIN_DIR)/$(BASE_BINARY) encode -i $${img_path:-$(image_path)} \
		-d $${aud_path:-$(audio_path)} \
		-m $${r_msk:-$(r_mask)} $${g_msk:-$(g_mask)} $${b_msk:-$(b_mask)} $${a_msk:-$(a_mask)} \
		-o $${enc_img_path:-$(encoded_image_path)} \
		-r $${pix_format:-$(pixel_format)}

# =======================
# Decode Target
# =======================

.PHONY: decode
decode:
	@read -p "Enter encoded image path (default: $(encoded_image_path)): " enc_img_path; \
	read -p "Enter decoded image path (default: $(decoded_image_path)): " dec_img_path; \
	read -p "Enter pixel format (default: $(pixel_format)): " pix_format; \
	read -p "Enter r_mask (default: $(r_mask)): " r_msk; \
	read -p "Enter g_mask (default: $(g_mask)): " g_msk; \
	read -p "Enter b_mask (default: $(b_mask)): " b_msk; \
	read -p "Enter a_mask (default: $(a_mask)): " a_msk; \
	./$(BIN_DIR)/$(BASE_BINARY) decode -i $${enc_img_path:-$(encoded_image_path)} \
		-m $${r_msk:-$(r_mask)} $${g_msk:-$(g_mask)} $${b_msk:-$(b_mask)} $${a_msk:-$(a_mask)} \
		-o $${dec_img_path:-$(decoded_image_path)} \
		-r $${pix_format:-$(pixel_format)}

# =======================
# Play Audio Target
# =======================

.PHONY: play_audio
play_audio:
	vlc $(decoded_image_path)

# =======================
# Compare Hashes Target
# =======================

.PHONY: compare_hashes
compare_hashes:
	@read -p "Enter first file path: " file1; \
	read -p "Enter second file path: " file2; \
	if [ "$(OS)" = "Windows_NT" ]; then \
		echo "Comparing hashes on Windows"; \
		hash1=$$(CertUtil -hashfile $$file1 MD5 | findstr /V "hash" | findstr /V "CertUtil"); \
		hash2=$$(CertUtil -hashfile $$file2 MD5 | findstr /V "hash" | findstr /V "CertUtil"); \
	else \
		echo "Comparing hashes on Linux"; \
		hash1=$$(md5sum $$file1 | awk '{ print $$1 }'); \
		hash2=$$(md5sum $$file2 | awk '{ print $$1 }'); \
	fi; \
	if [ "$$hash1" = "$$hash2" ]; then \
		echo "Files are identical"; \
	else \
		echo "Files are different"; \
	fi

# =======================
# Clean Target
# =======================

.PHONY: clean
clean:
	@echo "Cleaning up generated binaries and results..."
	rm -rf $(BIN_DIR)/*
	rm -rf $(RESULTS_DIR)/*
	@echo "Cleaned."

# =======================
# Help Target
# =======================

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  compile           - Compile for native architecture"
	@echo "  crosscompile_all  - Cross-compile for all target architectures"
	@echo "  windows32         - Cross-compile for Windows 32-bit"
	@echo "  windows64         - Cross-compile for Windows 64-bit"
	@echo "  linux32           - Cross-compile for Linux 32-bit"
	@echo "  linux64           - Cross-compile for Linux 64-bit"
	@echo "  encode            - Encode audio into image"
	@echo "  decode            - Decode audio from image"
	@echo "  play_audio        - Play the decoded audio"
	@echo "  compare_hashes    - Compare hashes of two files"
	@echo "  clean             - Clean up generated files"
	@echo "  help              - Display this help message"


