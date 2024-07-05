# Variables
$image_path = "examples/image.png"
$pixel_format = "ARBG"

$r_mask = "00001111"
$g_mask = "00001111"
$b_mask = "00001111"
$a_mask = "00001111"

$encoded_image_path = "results/hidden.png"
$audio_path = "examples/bg3_mt.mp3"
$decoded_image_path = "results/decoded.$($audio_path.Split('.')[-1])"
$target = "steggify.cpp"
$compiled_binary = "steggify.exe"
$compiler = "g++"

# Compilation target
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
    Measure-Command {
        & $compiler -std=c++17 -O3 -I./include -I./headers $target -o $compiled_binary
    }
}

# Encode target
function Encode {
    .\$compiled_binary encode -i $image_path -d $audio_path -m $r_mask $g_mask $b_mask $a_mask -o $encoded_image_path -r $pixel_format
}

# Decode target
function Decode {
    .\$compiled_binary decode -i $encoded_image_path -m $r_mask $g_mask $b_mask $a_mask -o $decoded_image_path -r $pixel_format
}

# Play audio target
function PlayAudio {
    Start-Process vlc $decoded_image_path
}

# Compare hashes target
function CompareHashes {
    $file1 = $image_path
    $file2 = $decoded_image_path
    if ($env:OS -eq "Windows_NT") {
        Write-Host "Comparing hashes on Windows"
        $hash1 = CertUtil -hashfile $file1 MD5 | Select-String -Pattern "^[a-fA-F0-9]{32}$"
        $hash2 = CertUtil -hashfile $file2 MD5 | Select-String -Pattern "^[a-fA-F0-9]{32}$"
    } else {
        Write-Host "Comparing hashes on Linux"
        $hash1 = (Get-FileHash $file1 -Algorithm MD5).Hash
        $hash2 = (Get-FileHash $file2 -Algorithm MD5).Hash
    }
    if ($hash1 -eq $hash2) {
        Write-Host "Files are identical"
    } else {
        Write-Host "Files are different"
    }
}

# Run All target
function RunAll {
    Compile
    Encode
    Decode
    CompareHashes
    PlayAudio
}

# Main Menu
function Main {
    while ($true) {
        Write-Host "Select an option:"
        Write-Host "1. Compile"
        Write-Host "2. Encode"
        Write-Host "3. Decode"
        Write-Host "4. Play Audio"
        Write-Host "5. Compare Hashes"
        Write-Host "6. Run All"
        Write-Host "7. Exit"
        $choice = Read-Host "Enter choice"
        switch ($choice) {
            1 { Compile }
            2 { Encode }
            3 { Decode }
            4 { PlayAudio }
            5 { CompareHashes }
            6 { RunAll }
            7 { break }
            default { Write-Host "Invalid option, please try again." }
        }
    }
}

Main
