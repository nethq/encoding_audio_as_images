# Variables
$image_path = "examples/image.png"
$pixel_format = "ARBG"

$r_mask = "00001111"
$g_mask = "00001111"
$b_mask = "00001111"
$a_mask = "00001111"

$encoded_image_path = "results/hidden.png"
$audio_path = "examples/bg3_mt.mp3"
$decoded_image_path = "results/decoded"
$target = "steggify.cpp"
$compiled_binary = "steggify.exe"
$compiler = "g++"

# Function to compile
function Compile {
    Write-Host "Compiling with the following parameters:"
    Write-Host "image_path: $image_path"
    Write-Host "audio_path: $audio_path"
    Write-Host "r_mask: $r_mask"
    Write-Host "g_mask: $g_mask"
    Write-Host "b_mask: $b_mask"
    Write-Host "a_mask: $a_mask"
    Write-Host "encoded_image_path: $encoded_image_path"
    Write-Host "decoded_image_path: $decoded_image_path"
    Write-Host "target: $target"
    Write-Host "compiled_binary: $compiled_binary"
    Write-Host "compiler: $compiler"
	$time = Measure-Command {
        & $compiler -std=c++17 -O3 -I./include -I./headers $target -o $compiled_binary
    }
    Write-Host "Compilation time: $($time.TotalSeconds) seconds"
}

# Function to encode
function Encode {
    $img_path = Read-Host "Enter image path (default: $image_path)"
    $aud_path = Read-Host "Enter audio path (default: $audio_path)"
    $enc_img_path = Read-Host "Enter encoded image path (default: $encoded_image_path)"
    $pix_format = Read-Host "Enter pixel format (default: $pixel_format)"
    $r_msk = Read-Host "Enter r_mask (default: $r_mask)"
    $g_msk = Read-Host "Enter g_mask (default: $g_mask)"
    $b_msk = Read-Host "Enter b_mask (default: $b_mask)"
    $a_msk = Read-Host "Enter a_mask (default: $a_mask)"
    
    $img_path = if ($img_path) { $img_path } else { $image_path }
    $aud_path = if ($aud_path) { $aud_path } else { $audio_path }
    $enc_img_path = if ($enc_img_path) { $enc_img_path } else { $encoded_image_path }
    $pix_format = if ($pix_format) { $pix_format } else { $pixel_format }
    $r_msk = if ($r_msk) { $r_msk } else { $r_mask }
    $g_msk = if ($g_msk) { $g_msk } else { $g_mask }
    $b_msk = if ($b_msk) { $b_msk } else { $b_mask }
    $a_msk = if ($a_msk) { $a_msk } else { $a_mask }
    & Start-Process $img_path    
& .\$compiled_binary encode -i $img_path -d $aud_path -m $r_msk $g_msk $b_msk $a_msk -o $enc_img_path -r $pix_format
    & Start-Process $enc_img_path
}

# Function to decode
function Decode {
    $enc_img_path = Read-Host "Enter encoded image path (default: $encoded_image_path)"
    $dec_img_path = Read-Host "Enter decoded image path (default: $decoded_image_path)"
    $pix_format = Read-Host "Enter pixel format (default: $pixel_format)"
    $r_msk = Read-Host "Enter r_mask (default: $r_mask)"
    $g_msk = Read-Host "Enter g_mask (default: $g_mask)"
    $b_msk = Read-Host "Enter b_mask (default: $b_mask)"
    $a_msk = Read-Host "Enter a_mask (default: $a_mask)"

    $enc_img_path = if ($enc_img_path) { $enc_img_path } else { $encoded_image_path }
    $dec_img_path = if ($dec_img_path) { $dec_img_path } else { $decoded_image_path }
    $pix_format = if ($pix_format) { $pix_format } else { $pixel_format }
    $r_msk = if ($r_msk) { $r_msk } else { $r_mask }
    $g_msk = if ($g_msk) { $g_msk } else { $g_mask }
    $b_msk = if ($b_msk) { $b_msk } else { $b_mask }
    $a_msk = if ($a_msk) { $a_msk } else { $a_mask }

    & .\$compiled_binary decode -i $enc_img_path -m $r_msk $g_msk $b_msk $a_msk -o $dec_img_path -r $pix_format
    & Start-Process $dec_img_path
}

# Function to play audio
function PlayAudio {
    & Start-Process $decoded_image_path
}

# Function to compare hashes
function CompareHashes {
    $file1 = Read-Host "Enter first file path"
    $file2 = Read-Host "Enter second file path"

    if ($IsWindows) {
        Write-Host "Comparing hashes on Windows"
        $hash1 = CertUtil -hashfile $file1 MD5 | Select-String -Pattern "^[0-9a-f]{32}$" | ForEach-Object { $_.Line }
        $hash2 = CertUtil -hashfile $file2 MD5 | Select-String -Pattern "^[0-9a-f]{32}$" | ForEach-Object { $_.Line }
    } else {
        Write-Host "Comparing hashes on Linux"
        $hash1 = $(md5sum $file1 | ForEach-Object { $_.Split(" ")[0] })
        $hash2 = $(md5sum $file2 | ForEach-Object { $_.Split(" ")[0] })
    }

    if ($hash1 -eq $hash2) {
        Write-Host "Files are identical"
    } else {
        Write-Host "Files are different"
    }
}

# Function to run everything once
function RunEverythingOnce {
    Compile
    Encode
    Decode

    Write-Host "Select an option to open the decoded file:"
    Write-Host "1. Play Audio"
    Write-Host "2. Exit"

    $choice = Read-Host "Enter your choice"

    switch ($choice) {
        1 { PlayAudio }
        2 { Write-Host "Exiting..." }
        default { Write-Host "Invalid option, exiting." }
    }
}

# Main menu
function MainMenu {
    while ($true) {
        Write-Host "Select an option:"
        Write-Host "1. Compile"
        Write-Host "2. Encode"
        Write-Host "3. Decode"
        Write-Host "4. Play Audio"
        Write-Host "5. Compare Hashes"
        Write-Host "6. Run Everything Once"
        Write-Host "7. Exit"
        
        $choice = Read-Host "Enter your choice"
        
        switch ($choice) {
            1 { Compile }
            2 { Encode }
            3 { Decode }
            4 { PlayAudio }
            5 { CompareHashes }
            6 { RunEverythingOnce; break }
            7 { break }
            default { Write-Host "Invalid option, please try again." }
        }
    }
}

MainMenu
