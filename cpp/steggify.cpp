#include <vector>
#include <string>
#include <iostream>
#include <map>
#include <tuple>
#include <algorithm>
#include <fstream>
#include <chrono>
#include <sstream>
#include <filesystem>
#include <bitset>
#include <stdint.h>

//based on version 9

// #define COMPARE_BITMAP_WITH_FILE //compares the bitmap with the file after encoding and decoding
// #define INVERTED_ALPHA //inverts the alpha channel
// #define REMOVE_STARTING_0s //removes the starting 0s from the file //EXPERIMENTAL!
// #define TEST_FUNCTIONS //runs the test functions

#define PAD_0_AFTER_DATA_PUSH_WHOLE_BITMAP_TO_FILE
#define VV

#define PAD_VALUE 128
#define ATOMIC_TYPE uint8_t
#define BITS_IN_ATOMIC_TYPE 8
#define STB

#define STANDARD_ORDER "RGBA" //The expected image channel order

using namespace std;

string standard_order = STANDARD_ORDER;

#ifdef STB

    #define STB_IMAGE_IMPLEMENTATION
    #define STB_IMAGE_WRITE_IMPLEMENTATION

    #include "headers/stb_image.h"
    #include "headers/stb_image_write.h"

    vector<unsigned char> loadImage(const string& filename, int& width, int& height) {
        int n;
        unsigned char* data = stbi_load(filename.c_str(), &width, &height, &n, 4);
        if (!data) {
            cerr << "Error loading image: " << filename << endl;
            return {};
        }
        vector<unsigned char> rgbaData(data, data + (width * height * 4));
        stbi_image_free(data);
        return rgbaData;
    }
    bool saveImage(const string& filename, const vector<unsigned char>& data, int width, int height) {
        string ext = filename.substr(filename.find_last_of(".") + 1);
        switch (ext[0]) {
            case 'p': return stbi_write_png(filename.c_str(), width, height, 4, data.data(), width * 4);
            case 'j': return stbi_write_jpg(filename.c_str(), width, height, 4, data.data(), 100);
            case 'b': return stbi_write_bmp(filename.c_str(), width, height, 4, data.data());
            case 't': return stbi_write_tga(filename.c_str(), width, height, 4, data.data());
            default: return stbi_write_png(filename.c_str(), width, height, 4, data.data(), width * 4);
        }
    }
#endif

string invert_string(const string& str) {
    string inverted = str;
    reverse(inverted.begin(), inverted.end());
    return inverted;
}

typedef struct int_tuple { int first, second; } int_tuple;

string* masks;
int mask_count;
map<char, int_tuple> channel_image_data_order;

class ReferentialBitmap {
    int width, height, channels;
    string* masks;
    int mask_count;

    void map_order(const string order) {
        for (char channel : order) {
            switch (channel) {
                case 'R': channel_image_data_order[channel] = int_tuple{(int)standard_order.find("R"), int(order.find(channel))}; break;
                case 'G': channel_image_data_order[channel] = int_tuple{(int)standard_order.find("G"), int(order.find(channel))}; break;
                case 'B': channel_image_data_order[channel] = int_tuple{(int)standard_order.find("B"), int(order.find(channel))}; break;
                case 'A': channel_image_data_order[channel] = int_tuple{(int)standard_order.find("A"), int(order.find(channel))}; break;
            }
        }
    }
 


map<int, vector<tuple<int, int, int>>> map_masks(const vector<string>& masks, const string& order,bool inverted_strings = true ,bool fillFromMSB = true) {
    //fixed equal lenght masks problem found at v8
    int numMasks = masks.size();
    int bitsPerMask = masks[0].size();
    map<int, vector<tuple<int, int, int>>> global_vectorized_storage_map;

    int bits_in_all_masks = sum_total_1_bits_in_all_masks();

    // Check if the total number of bits is less than BITS_IN_ATOMIC_TYPE
    if (bits_in_all_masks % BITS_IN_ATOMIC_TYPE != 0) {
        cout << "Not enough bits to fill a storage object." << endl;
        cout << "Currently, the total number of bits is: " << bits_in_all_masks << endl;
        cout << "The total number of bits should be a multiple of " << BITS_IN_ATOMIC_TYPE << endl;
        return global_vectorized_storage_map;
    }
    
    vector<string> local_masks(numMasks); // Inverting the masks if necessary
    if (inverted_strings) {
        for (int i = 0; i < numMasks; i++) {
            local_masks[i] = invert_string(masks[i]);
        }
    } else {
        for (int i = 0; i < numMasks; i++) {
            local_masks[i] = masks[i];
        }
    }

    int storageIndex = 0;
    int storageBit = fillFromMSB ? BITS_IN_ATOMIC_TYPE - 1 : 0;
    int increment = fillFromMSB ? -1 : 1;

    for (char o : order) {
        int channel_position_in_default_data_order = channel_image_data_order[o].first;
        // int position_in_given_order = channel_image_data_order[o].second;

        if (fillFromMSB) {
            for (int bit = bitsPerMask - 1; bit >= 0; --bit) {
                if (local_masks[channel_position_in_default_data_order][bit] == '1') {
                    global_vectorized_storage_map[storageIndex].emplace_back(make_tuple(channel_position_in_default_data_order, bit, storageBit));
                    storageBit += increment;
                    if (storageBit < 0) {
                        ++storageIndex;
                        storageBit = BITS_IN_ATOMIC_TYPE - 1;
                    }
                }
            }
        } else {
            for (int bit = 0; bit < bitsPerMask; ++bit) {
                if (local_masks[channel_position_in_default_data_order][bit] == '1') {
                    global_vectorized_storage_map[storageIndex].emplace_back(make_tuple(channel_position_in_default_data_order, bit, storageBit));
                    storageBit += increment;
                    if (storageBit >= BITS_IN_ATOMIC_TYPE) {
                        ++storageIndex;
                        storageBit = 0;
                    }
                }
            }
        }
    }

    // Check if all storage objects are filled to the brim
    for (const auto& entry : global_vectorized_storage_map) {
        auto it = find_if(global_vectorized_storage_map.begin(), global_vectorized_storage_map.end(), [](const auto& entry) {
            return entry.second.size() != BITS_IN_ATOMIC_TYPE;
        });

        if (it != global_vectorized_storage_map.end()) {
            cout << "Error: Storage object " << it->first << " is not completely filled." << endl;
            return {};
        }
    }

    return global_vectorized_storage_map;
}


public:
    map<int, vector<tuple<int, int, int>>> global_vectorized_storage_map;
    vector<ATOMIC_TYPE> referential_bitmap;
    ReferentialBitmap(int width, int height, int channels, string* masks, int mask_count,const string order)
        : width(width), height(height), channels(channels), masks(masks), mask_count(mask_count) {
        map_order(order);
        //convert masks to vector, but keep the original alignment
        vector<string> masks_vector;
        for (int i = 0; i < mask_count; i++)
        {
            masks_vector.emplace_back(masks[i]);
        }
        global_vectorized_storage_map = map_masks(masks_vector, order);
        
        #ifdef VV
        cout << "Mapping for channels is as follows: " << endl;

        for (const auto& entry : global_vectorized_storage_map) {
            cout << "Storage index: " << entry.first << endl;
            for (const auto& tuple : entry.second) {
                auto [channel_pos, mask_bit_index, storage_bit_index] = tuple;
                cout << "Channel: " << channel_pos << ", Mask bit index: " << mask_bit_index << ", Storage bit index: " << storage_bit_index << endl;
            }
        }
        #endif

    }
    
    void build_referential_bitmap() {
        size_t total_pixels = width * height;
        size_t total_available_bits = total_pixels * sum_total_1_bits_in_all_masks();
        size_t storage_size = (total_available_bits + BITS_IN_ATOMIC_TYPE - 1) / BITS_IN_ATOMIC_TYPE;
        referential_bitmap.resize(storage_size);
        printf("Current allocatable storage in image:\n%lu bytes\n%lu KB\n%lu MB\n", referential_bitmap.size(), referential_bitmap.size() / 1024, referential_bitmap.size() / 1024 / 1024);
    }
    
    bool populate_bitmap_with_file(const string& filename, size_t max_bytes) { 
    ifstream file(filename, ios::binary);
    if (!file) {
        cerr << "Failed to open file: " << filename << endl;
        return false;
    }
    
    vector<char> fileData((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    
    #ifdef REMOVE_STARTING_0s
    // Skip leading zeros if more than 1000 are present
    size_t zero_count = 0;
    size_t start_index = 0;
    while (start_index < fileData.size() && zero_count < 1000) {
        if (fileData[start_index] == 0) {
            zero_count++;
        } else {
            zero_count = 0;
        }
        start_index++;
    }
    // If we have counted 1000 zeros, skip past them
    if (zero_count >= 1000) {
        fileData.erase(fileData.begin(), fileData.begin() + start_index);
    }
    #endif

    size_t bytes_to_copy = (max_bytes == 0) ? fileData.size() : min(max_bytes, fileData.size());

    for (size_t i = 0; i < bytes_to_copy && i < referential_bitmap.size(); ++i) {
        referential_bitmap[i] = static_cast<ATOMIC_TYPE>(fileData[i]);
    }

    #ifdef PAD_0_AFTER_DATA_PUSH_WHOLE_BITMAP_TO_FILE
        for (size_t i = bytes_to_copy; i < referential_bitmap.size(); ++i) {
            referential_bitmap[i] = PAD_VALUE;
        }
    #endif
    
    return true;
}

    ATOMIC_TYPE* atomic_pull_operation(int storage_index,const void* array_to_pull_from) {
        if (storage_index >= referential_bitmap.size()) {
            cerr << "Storage index out of range" << endl;
            return NULL;
        }
        ATOMIC_TYPE* storage = &referential_bitmap[storage_index];
        ATOMIC_TYPE* referenced_values = (ATOMIC_TYPE*)array_to_pull_from;
        int vectorized_map_index = storage_index % global_vectorized_storage_map.size();
        auto mappings = global_vectorized_storage_map[vectorized_map_index];

        ATOMIC_TYPE temp_buffer = 0;
        int bit_index = sizeof(ATOMIC_TYPE) * 8 - 1;
        while (bit_index >= 0 && mappings.size()) {
            auto [channel_pos, mask_bit_index, storage_bit_index] = mappings.back();
            ATOMIC_TYPE bit_value = (referenced_values[channel_image_data_order[standard_order[channel_pos]].first] >> mask_bit_index) & 1;
            #ifdef INVERTED_ALPHA
                if (channel_pos == 3) bit_value = !bit_value;
            #endif
            temp_buffer |= (bit_value << storage_bit_index);
            bit_index--;
            mappings.pop_back();
        }
        *storage = temp_buffer;
        return storage;
    }

    void export_bitmap_to_file(const string& filename) {
        ofstream file(filename, ios::binary);
        if (!file) {
            cerr << "Failed to open file for writing: " << filename << endl;
            return;
        }
        size_t end_index = referential_bitmap.size();
        #ifdef PAD_0_AFTER_DATA_PUSH_WHOLE_BITMAP_TO_FILE
            while (end_index > 0 && referential_bitmap[end_index - 1] == PAD_VALUE) --end_index;
        #endif
        for (size_t i = 0; i < end_index; ++i) {
            file.put(static_cast<unsigned char>(referential_bitmap[i]));
        }
    }
    
    int atomic_push_operation(int storage_index, void* array_to_push_to) {
        if (storage_index >= referential_bitmap.size()) {
            cerr << "Storage index out of range" << endl;
            return -1;
        }
        ATOMIC_TYPE* storage = &referential_bitmap[storage_index];
        ATOMIC_TYPE* values_to_write_to = (ATOMIC_TYPE*)array_to_push_to;
        int vectorized_map_index = storage_index % global_vectorized_storage_map.size();
        auto mappings = global_vectorized_storage_map[vectorized_map_index];
        ATOMIC_TYPE temp_buffer = *storage;
        int bit_index = sizeof(ATOMIC_TYPE) * 8 - 1;

        while (bit_index >= 0 && mappings.size()) {
            auto [channel_pos, mask_bit_index, storage_bit_index] = mappings.back();
            ATOMIC_TYPE bit_value = (temp_buffer >> storage_bit_index) & 1;
            #ifdef INVERTED_ALPHA
                if (channel_pos == 3) bit_value = !bit_value;
            #endif
            int indx_to_write_to = channel_image_data_order[standard_order[channel_pos]].first;
            values_to_write_to[indx_to_write_to] &= ~(1 << mask_bit_index);
            values_to_write_to[indx_to_write_to] |= (bit_value << mask_bit_index);
            bit_index--;
            mappings.pop_back();
        }
        return 0;
    }
    ~ReferentialBitmap() {
        referential_bitmap.clear();
        global_vectorized_storage_map.clear();
    }
    int sum_total_1_bits_in_all_masks() {
        int sum = 0;
        for (int i = 0; i < mask_count; i++) {
            sum += count(masks[i].begin(), masks[i].end(), '1');
        }
        return sum;
    }
    void compare_bitmap_with_file(const string& filename) {
        ifstream file(filename, ios::binary);
        if (!file) {
            cerr << "Failed to open file for reading: " << filename << endl;
            return;
        }
        vector<unsigned char> fileData((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
        size_t file_size = fileData.size();
        size_t bitmap_size = referential_bitmap.size();
        size_t min_size = min(bitmap_size, file_size);
        size_t first_mismatch_index = min_size;
        size_t next_align_index = min_size;
        size_t i = 0;
        for (i = 0; i < min_size; ++i) {
            if (referential_bitmap[i] != fileData[i]) {
                first_mismatch_index = i;
                break;
            }
        }
        for (i = first_mismatch_index + 1; i < min_size; ++i) {
            if (referential_bitmap[i] == fileData[i]) {
                next_align_index = i;
                break;
            }
        }
        if (first_mismatch_index < min_size) {
            cout << "First mismatch at index: " << first_mismatch_index << endl;
        } else {
            cout << "No mismatches found" << endl;
        }
        if (next_align_index < min_size) {
            cout << "Next align index: " << next_align_index << endl;
        } else {
            cout << "No next align index found" << endl;
        }
    }
};

bool encode_atomic_push(string image_filename, string order, vector<string> masks, string inputDataFile, string outputFilename) {
    auto start_total = chrono::high_resolution_clock::now();
    int width, height;

    // Load the image
    auto start_load = chrono::high_resolution_clock::now();
    vector<unsigned char> imageData = loadImage(image_filename, width, height);
    auto end_load = chrono::high_resolution_clock::now();
    if (imageData.empty()) {
        cerr << "Failed to load image" << endl;
        return false;
    }
    chrono::duration<double> load_duration = end_load - start_load;
    cout << "Image loading time: " << load_duration.count() << " s\n";

    // Initialize bitmap
    ReferentialBitmap bitmap(width, height, 4, masks.data(), masks.size(), order);
    bitmap.build_referential_bitmap();

    // Read the input file data
    ifstream file(inputDataFile, ios::binary | ios::ate);
    if (!file) {
        cerr << "Failed to open input file: " << inputDataFile << endl;
        return false;
    }
    size_t file_size = file.tellg();
    file.seekg(0, ios::beg);
    vector<char> fileData(file_size);
    file.read(fileData.data(), file_size);
    file.close();

    bitmap.populate_bitmap_with_file(inputDataFile, file_size);

    //print if the file will fit in the bitmap or will it be truncated.
    if (file_size > bitmap.referential_bitmap.size()) {
        cout << "\n FILE SIZE IS BIGGER THAN THE CURRENTLY AVAILABLE BITMAP. TRUNCATING THE FILE! \n" << endl;
    }

    // Push data to the image
    size_t storage_index = 0;
    int storage_objects_per_pixel = bitmap.global_vectorized_storage_map.size();
    for (int pixel_counter = 0; pixel_counter < width * height; ++pixel_counter) {
        for (int gvsl = 0; gvsl < storage_objects_per_pixel; ++gvsl) {
            ATOMIC_TYPE* temp_data = &imageData.at(pixel_counter * 4);
            bitmap.atomic_push_operation(storage_index++, temp_data);
        }
    }

    // Save the modified image
    auto start_save = chrono::high_resolution_clock::now();
    if (!saveImage(outputFilename, imageData, width, height)) {
        cerr << "Failed to save image" << endl;
        return false;
    }
    auto end_save = chrono::high_resolution_clock::now();
    chrono::duration<double> save_duration = end_save - start_save;
    cout << "Image saving time: " << save_duration.count() << " s\n";

    auto end_total = chrono::high_resolution_clock::now();
    chrono::duration<double> total_duration = end_total - start_total;
    cout << "Total encode time: " << total_duration.count() << " s\n";

    return true;
}

ATOMIC_TYPE* decode_atomic_pull(string image_filename, string order, vector<string> masks, string outputFilename) {
    auto start_total = chrono::high_resolution_clock::now();
    int width, height;

    // Load the image
    auto start_load = chrono::high_resolution_clock::now();
    vector<unsigned char> imageData = loadImage(image_filename, width, height);
    auto end_load = chrono::high_resolution_clock::now();
    if (imageData.empty()) {
        cerr << "Failed to load image" << endl;
        return nullptr;
    }
    chrono::duration<double> load_duration = end_load - start_load;
    cout << "Image loading time: " << load_duration.count() << " s\n";

    // Initialize bitmap
    ReferentialBitmap bitmap(width, height, 4, masks.data(), masks.size(), order);
    bitmap.build_referential_bitmap();

    // Pull data from the image
    size_t storage_index = 0;
    int storage_objects_per_pixel = bitmap.global_vectorized_storage_map.size();
    for (int pixel_counter = 0; pixel_counter < width * height; ++pixel_counter) {
        for (int gvsl = 0; gvsl < storage_objects_per_pixel; ++gvsl) {
            ATOMIC_TYPE* temp_data = &imageData.at(pixel_counter * 4);
            bitmap.atomic_pull_operation(storage_index++, temp_data);
        }
    }

    // Export bitmap to file
    auto start_export = chrono::high_resolution_clock::now();
    bitmap.export_bitmap_to_file(outputFilename);
    auto end_export = chrono::high_resolution_clock::now();
    chrono::duration<double> export_duration = end_export - start_export;
    cout << "Data export time: " << export_duration.count() << " s\n";

    auto end_total = chrono::high_resolution_clock::now();
    chrono::duration<double> total_duration = end_total - start_total;
    cout << "Total decode time: " << total_duration.count() << " s\n";

    return bitmap.referential_bitmap.data();
}


// ----- Testing Functions -----
#ifdef TEST_FUNCTIONS
#include <cassert>

vector<unsigned char> generate_test_image(int width, int height) {
    return vector<unsigned char>(width * height * 4, 128);
}
#define testmasks {"00001111","00001111", "00001111","00001111"}
#define testorder "ARBG"

void test_build_referential_bitmap() {
    string order = testorder;
    string masks[] = testmasks;
    ReferentialBitmap bitmap(8, 4, 4, masks, 4, order);
    bitmap.build_referential_bitmap();
    assert(bitmap.referential_bitmap.size() == 64);
    cout << "test_build_referential_bitmap passed." << endl;
}

void test_populate_bitmap_with_value() {
    string order = testorder;
    string masks[] = testmasks;
    ReferentialBitmap bitmap(8, 4, 4, masks, 4, order);
    bitmap.build_referential_bitmap();
    uint32_t test_value = 42069;
    bitmap.referential_bitmap[0] = 0b10100100;
    bitmap.referential_bitmap[1] = 0b01010101;
    uint32_t retrieved_value = 0;
    retrieved_value |= bitmap.referential_bitmap[0] << 8;
    retrieved_value |= bitmap.referential_bitmap[1];
    assert(retrieved_value == test_value);
    cout << "test_populate_bitmap_with_value passed." << endl;
}

void test_atomic_push_operation() {
    string order = testorder;
    string masks[] = testmasks;    
    ReferentialBitmap bitmap(8, 4, 4, masks, 4, order);
    bitmap.build_referential_bitmap();
    uint8_t image_data[32 * 4] = {128};
    for (int i = 0; i < 32 * 4; i++) {
        image_data[i] = 0b10000000;
    }
    bitmap.referential_bitmap[0] = 0b10100100;
    bitmap.referential_bitmap[1] = 0b01010101;

    assert(bitmap.referential_bitmap[0] == 0b10100100);
    assert(bitmap.referential_bitmap[1] == 0b01010101);

    bitmap.atomic_push_operation(0, image_data);
    bitmap.atomic_push_operation(1, image_data);
    
    assert(image_data[0] == 0b10000001);
    assert(image_data[1] == 0b10000101);
    assert(image_data[2] == 0b10000010);
    assert(image_data[3] == 0b11010010);
    cout << "test_atomic_push_operation passed." << endl;
}

void test_atomic_pull_operation() {
    string order = testorder;
    string masks[] = testmasks;
    ReferentialBitmap bitmap(8, 4, 4, masks, 4, order);
    bitmap.build_referential_bitmap();
    uint8_t image_data[32 * 4] = {0b10000001, 0b10000101, 0b10000010, 0b11010010};
    bitmap.atomic_pull_operation(0, image_data);
    bitmap.atomic_pull_operation(1, image_data);
    uint16_t retrieved_value = 0;
    retrieved_value |= bitmap.referential_bitmap[0] << 8;
    retrieved_value |= bitmap.referential_bitmap[1];
    assert(retrieved_value == 42069);
    cout << "test_atomic_pull_operation passed." << endl;
}

void test_encode_atomic_push() {
    string order = testorder;
    vector<string> masks = testmasks;
    int width = 8, height = 4;
    vector<unsigned char> imageData = generate_test_image(width, height);
    ReferentialBitmap bitmap(width, height, 4, masks.data(), masks.size(), order);
    bitmap.build_referential_bitmap();
    // bitmap.referential_bitmap[0] = 0b10100100;
    // bitmap.referential_bitmap[1] = 0b01010101;
    
    for (int i = 0; i < 64; i++) {
        if (i % 2 == 0) {
            bitmap.referential_bitmap[i] = 0b10100100;
        } else {
            bitmap.referential_bitmap[i] = 0b01010101;
        }
    }

    int storage_obj_per_pixel = bitmap.global_vectorized_storage_map.size();
    size_t storage_index = 0;
    for (int pixel_counter = 0; pixel_counter < width * height; ++pixel_counter) {
        for(int gvsl = 0 ; gvsl < bitmap.global_vectorized_storage_map.size(); gvsl++){ 
            ATOMIC_TYPE *temp_data = &imageData.at(pixel_counter * 4);
            bitmap.atomic_push_operation(pixel_counter/storage_obj_per_pixel + gvsl, temp_data );
            storage_index++;
        }
    }

    for (int i = 0; i < 32 * 4; i++) {
        if (i % 4 == 0) {
            assert(imageData[i] == 0b10000001);
        } else if (i % 4 == 1) {
            assert(imageData[i] == 0b10000101);
        } else if (i % 4 == 2) {
            assert(imageData[i] == 0b10000010);
        } else {
            assert(imageData[i] == 0b11010010);
        }
    }

    cout << "test_encode_atomic_push passed." << endl;
}

void test_decode_atomic_pull() {
    string order = testorder;
    vector<string> masks = testmasks;
    int width = 8, height = 4;
    vector<unsigned char> imageData = generate_test_image(width, height);
    ReferentialBitmap bitmap(width, height, 4, masks.data(), masks.size(), order);
    bitmap.build_referential_bitmap();
    // imageData[0] = 0b10000001;
    // imageData[1] = 0b10000101;
    // imageData[2] = 0b10000010;
    // imageData[3] = 0b11010010;
    for (int i =0 ; i<32*4; i++) {
        if (i % 4 == 0) {
            imageData[i] = 0b10000001;
        } else if (i % 4 == 1) {
            imageData[i] = 0b10000101;
        } else if (i % 4 == 2) {
            imageData[i] = 0b10000010;
        } else {
            imageData[i] = 0b11010010;
        }
    }

    int storage_objects_per_pixel = bitmap.global_vectorized_storage_map.size();
    int pixel_iterator = 0;
    int storage_iterator = 0;

    for (int pixel_counter = 0; pixel_counter < width * height; ++pixel_counter) {
        for(int gvsl = 0 ; gvsl < bitmap.global_vectorized_storage_map.size(); gvsl++){ 
            ATOMIC_TYPE *temp_data = &imageData.at(pixel_counter * 4);
            bitmap.atomic_pull_operation(storage_iterator, temp_data );
            storage_iterator++;
        }
    }

    uint32_t retrieved_value = 0;
    for ( int i = 0 ; i < bitmap.referential_bitmap.size(); i++) {
        if(i % 2 == 0) {
            assert(bitmap.referential_bitmap[i] == 0b10100100);
        } else {
            assert(bitmap.referential_bitmap[i] == 0b01010101);
        }
    }
    cout << "test_decode_atomic_pull passed." << endl;
}

void run_tests() {
    test_build_referential_bitmap();
    test_populate_bitmap_with_value();
    test_atomic_push_operation();
    test_atomic_pull_operation();
    test_encode_atomic_push();
    test_decode_atomic_pull();
    cout << "All tests passed." << endl;
}

// ----- Testing Functions -----
#endif 

void print_help() {
    cout << "Usage:\n"
         << "  tests \n"
         << "  encode -i <inputImage> -d <inputDataFile> -m <maskR> <maskG> <maskB> <maskA> -o <outputImage> -r <order> [options]\n"
         << "  decode -i <inputImage> -m <maskR> <maskG> <maskB> <maskA> -o <outputFile> -r <order> [options]\n"
         << "Options:\n"
         << "  -h, --help                 Show this help message\n"
         << "  -i, --input <inputFile>    Specify the input image file\n"
         << "  -o, --output <outputFile>  Specify the output file\n"
         << "  -d, --data <inputDataFile> Specify the input data file for encoding\n"
         << "  -m, --masks <masks>        Specify the masks\n"
         << "  -r, --order <order>        Specify the channel order (e.g., ARBG)\n";
}

int main(int argc, char** argv) {
    if (argc < 2) {
        print_help();
        return 1;
    }

    string mode;
    string inputFilename;
    string outputFilename;
    string inputDataFile;
    vector<string> masks;
    string order;
    bool pad = false, compare = false, verbose = false, remove_zeros = false, invert_alpha = false;

    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--help" || arg == "-h") {
            print_help();
            return 0;
        }else if (arg == "tests") {
           
            #ifdef TEST_FUNCTIONS
                run_tests();
            #else
                cout << "Tests are disabled in this build." << endl;
            #endif

            return 0;
        }else if (arg == "encode" || arg == "decode") {
            mode = arg;
        } else if ((arg == "--input" || arg == "-i") && i + 1 < argc) {
            inputFilename = argv[++i];
        } else if ((arg == "--output" || arg == "-o") && i + 1 < argc) {
            outputFilename = argv[++i];
        } else if ((arg == "--data" || arg == "-d") && i + 1 < argc) {
            inputDataFile = argv[++i];
        } else if ((arg == "--masks" || arg == "-m") && i + 1 < argc) {
            while (i + 1 < argc && argv[i + 1][0] != '-') {
                masks.push_back(argv[++i]);
                #ifdef VV
                //cout<< "mask: " << masks.back() << endl;
                #endif
            }
        } else if ((arg == "--order" || arg == "-r") && i + 1 < argc) {
            order = argv[++i];
        } else {
            cerr << "Unknown option: " << arg << endl;
            print_help();
            return 1;
        }
    }

    if (mode.empty() || inputFilename.empty() || order.empty() || masks.empty() || (mode == "encode" && inputDataFile.empty())) {
        print_help();
        return 1;
    }

    if (mode == "decode") {
        if (outputFilename.empty()) {
            outputFilename = inputFilename + "_decoded";
        }
        decode_atomic_pull(inputFilename, order, masks, outputFilename);
    } else if (mode == "encode") {
        if (outputFilename.empty()) {
            outputFilename = inputFilename + "_encoded";
        }
        bool encodedCompletely = encode_atomic_push(inputFilename, order, masks, inputDataFile, outputFilename);

        if (encodedCompletely) {
            cout << "\n\nSUCCESS!\n\n" << endl;
        } else {
            cout << "\n\nWARNING! - Error in the encoding process.\n\n" << endl;
        }
    } else {
        print_help();
        return 1;
    }
    return 0;
}
