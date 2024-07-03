# encoding_audio_as_images - V3 - DPLMA - Referential Bitmap

## Overview

This is an optimised version (V3) of the `encoding_audio_as_images` tool. The initial version of the tool is laid out in its bare intent in version 1. This version has been improved based on the learnings and discoveries noted down during the development process.

If you are interested in the experimentation process, the progress that has been made, and the discoveries that have been made, you can check out the provided Python notebooks. Please note that these notebooks are not clearly labeled and the time and space complexity is sub-par.

## Current Iteration

The current iteration of the script is written in C++. If you wish to enable some experimental functionality, look through the macros, define the ones you wish to enable, and re-compile the script.

## Functionality

This solution allows you to Encode/Decode any type of file into and out of a given PNG image. The solution has gone through many iterations and is still a work in progress. However, for 1080 images, it currently runs in less than 0.5 seconds, depending on the hardware.

The recommended application is for embedding audio in images, but there is support for embedding other types of files. Please ensure you test the decoding of the data from the image yourself before passing it on to its journey as a steganogram.

If you wish to COMPRESS/ENCRYPT the data you are embedding, you can use any tool you desire, as long as it can output to one or more files. The solution works with any type of file.

## Known Issues

When working with some particular extensions, there seems to be a problem with the ending 0s in the file data, as they seem to be trimmed short. If you encounter such a problem, you should change the `PAD_VALUE` macro to some arbitrary value that does not coincide with the ending values of your file. The same must be done with the decoding script.

## Applicabiltiy

The algorithm with which this steganographic process is applied allows the user an unrestricted freedom in manipulating the way that the data is encoded into the image,
thus you should creafully look at the command output of the script and check if firstly the file you are trying to encode is cut, because it will be on "silent" mode.