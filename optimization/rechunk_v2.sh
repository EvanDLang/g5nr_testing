#!/usr/bin/env bash

# Check if the correct number of arguments is provided
if [ "$#" -lt 4 ]; then
    echo "Usage: $0 <file_path> <chunk_size_elevation> <chunk_size_lat> <chunk_size_lon>"
    exit 1
fi

# Assign arguments to variables
FILE_PATH="$1"
CHUNK_SIZE_ELEVATION="$2"
CHUNK_SIZE_LAT="$3"
CHUNK_SIZE_LON="$4"

# Check if the file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "File does not exist: $FILE_PATH"
    exit 1
fi

# Output directory
OUTDIR="experiments/"

# Variables
VARIABLES="T"

# Create output directory if it doesn't exist
mkdir -p "$OUTDIR"

# Construct the chunk size string
CHUNK_SIZE="1x${CHUNK_SIZE_ELEVATION}x${CHUNK_SIZE_LAT}x${CHUNK_SIZE_LON}"

# Perform the chunking with h5repack
OUTPUT_FILE="$OUTDIR/chunked-${CHUNK_SIZE}.nc"
h5repack -S PAGE -G $((8 * 1024 * 1024)) -l $VARIABLES:CHUNK=$CHUNK_SIZE "$FILE_PATH" "$OUTPUT_FILE"

# Check if the operation was successful
if [ $? -eq 0 ]; then
    # Return the file size after chunking
    FILE_SIZE=$(du -sH "$OUTPUT_FILE" | cut -f1)
    echo "File size for $OUTPUT_FILE: $FILE_SIZE KB"
else
    echo "Failed to process chunk size: $CHUNK_SIZE"
    exit 1
fi
