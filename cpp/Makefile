# Variables
image_path="examples/image.png"
pixel_format="ARBG"

r_mask="00000011"
g_mask="00000011"
b_mask="00000011"
a_mask="00000011"

encoded_image_path="results/hidden.png"
audio_path="examples/test_data.txt"
decoded_image_path="results/decoded.$(shell echo $(audio_path) | awk -F . '{print $$NF}')"
target="steggify.cpp"
compiled_binary="steggify"
compiler=g++

# Compilation target
.PHONY: compile
compile:
	@echo "Compiling with the following parameters:"
	@echo "image_path: $(image_path)"
	@echo "audio_path: $(audio_path)"
	@echo "r_mask: $(r_mask)"
	@echo "g_mask: $(g_mask)"
	@echo "b_mask: $(b_mask)"
	@echo "a_mask: $(a_mask)"
	@echo "encoded_image_path: $(encoded_image_path)"
	@echo "decoded_image_path: $(decoded_image_path)"
	@echo "target: $(target)"
	@echo "compiled_binary: $(compiled_binary)"
	@echo "compiler: $(compiler)"
	time $(compiler) -std=c++17 -O3 -I./include -I./headers $(target) -o $(compiled_binary)

# Encode target
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
	./$(compiled_binary) encode -i $${img_path:-$(image_path)} -d $${aud_path:-$(audio_path)} -m $${r_msk:-$(r_mask)} $${g_msk:-$(g_mask)} $${b_msk:-$(b_mask)} $${a_msk:-$(a_mask)} -o $${enc_img_path:-$(encoded_image_path)} -r $${pix_format:-$(pixel_format)}

# Decode target
.PHONY: decode
decode:
	@read -p "Enter encoded image path (default: $(encoded_image_path)): " enc_img_path; \
	read -p "Enter decoded image path (default: $(decoded_image_path)): " dec_img_path; \
	read -p "Enter pixel format (default: $(pixel_format)): " pix_format; \
	read -p "Enter r_mask (default: $(r_mask)): " r_msk; \
	read -p "Enter g_mask (default: $(g_mask)): " g_msk; \
	read -p "Enter b_mask (default: $(b_mask)): " b_msk; \
	read -p "Enter a_mask (default: $(a_mask)): " a_msk; \
	./$(compiled_binary) decode -i $${enc_img_path:-$(encoded_image_path)} -m $${r_msk:-$(r_mask)} $${g_msk:-$(g_mask)} $${b_msk:-$(b_mask)} $${a_msk:-$(a_mask)} -o $${dec_img_path:-$(decoded_image_path)} -r $${pix_format:-$(pixel_format)}

# Play audio target
.PHONY: play_audio
play_audio:
	vlc $(decoded_image_path)

# Compare hashes target
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
