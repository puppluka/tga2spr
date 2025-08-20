# tga2spr.py (v0.0.1-alpha)
# A Python program to create Quake sprite files from TGA/PNG/PPM images and a QC script.
# This version has been repaired to correctly match the Quake engine's binary format.
#
# Original Source Code: https://github.com/eukara/tga2spr
# The MIT License (MIT)
#
# Copyright (c) 2016-2019 Marco "eukara" Hladik <marco at icculus.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
import struct
import os
from PIL import Image
from math import sqrt

# -----------------------------------------------------------------------------
# Quake palette
# -----------------------------------------------------------------------------
QUAKE_PALETTE = bytes([
    0, 0, 0, 15, 15, 15, 31, 31, 31, 47, 47, 47, 63, 63, 63, 75, 75, 75,
    91, 91, 91, 107, 107, 107, 123, 123, 123, 139, 139, 139, 155, 155, 155,
    171, 171, 171, 187, 187, 187, 203, 203, 203, 219, 219, 219, 235, 235, 235,
    15, 11, 7, 23, 15, 11, 31, 23, 11, 39, 27, 15, 47, 35, 19, 55, 43, 23,
    63, 47, 23, 75, 55, 27, 83, 59, 27, 91, 67, 31, 99, 75, 31, 107, 83, 31,
    115, 87, 31, 123, 95, 35, 131, 103, 35, 143, 111, 35, 11, 11, 15, 19, 19,
    27, 27, 27, 39, 39, 39, 51, 47, 47, 63, 55, 55, 75, 63, 63, 87, 71, 71,
    99, 79, 79, 111, 91, 91, 127, 99, 99, 139, 107, 107, 151, 115, 115, 163,
    123, 123, 175, 7, 0, 0, 15, 0, 0, 23, 0, 0, 31, 0, 0, 39, 0, 0, 47, 0, 0,
    55, 0, 0, 63, 0, 0, 71, 0, 0, 79, 0, 0, 87, 0, 0, 95, 0, 0, 103, 0, 0,
    111, 0, 0, 119, 0, 0, 127, 0, 0, 19, 19, 0, 27, 27, 0, 35, 35, 0, 47, 43,
    0, 55, 47, 0, 67, 55, 0, 75, 59, 7, 87, 67, 7, 95, 71, 7, 107, 75, 11,
    119, 83, 15, 131, 87, 19, 139, 91, 19, 151, 95, 27, 163, 99, 31, 175, 103,
    35, 35, 19, 7, 47, 23, 11, 59, 31, 15, 75, 35, 19, 87, 43, 23, 99, 47,
    31, 115, 55, 35, 127, 59, 43, 143, 67, 51, 159, 79, 51, 175, 99, 47, 191,
    119, 47, 207, 143, 43, 223, 171, 39, 239, 243, 27, 11, 7, 0, 27, 19, 0, 43,
    35, 15, 55, 43, 19, 71, 51, 27, 83, 55, 35, 99, 63, 43, 111, 71, 51, 127,
    83, 63, 139, 95, 71, 155, 107, 83, 167, 123, 95, 183, 135, 107, 195, 147,
    123, 211, 163, 139, 171, 139, 163, 159, 127, 151, 147, 115, 135, 139, 103,
    123, 127, 91, 111, 119, 83, 99, 107, 75, 87, 95, 63, 75, 87, 55, 67, 75,
    47, 59, 67, 39, 47, 55, 31, 35, 43, 23, 19, 27, 15, 11, 15, 7, 7, 179, 59,
    159, 175, 107, 143, 163, 95, 131, 151, 87, 119, 139, 79, 107, 127, 75,
    95, 115, 67, 83, 107, 59, 75, 95, 51, 63, 83, 43, 55, 71, 35, 43, 59, 31,
    27, 47, 23, 19, 35, 11, 11, 15, 7, 7, 219, 195, 187, 203, 187, 167, 191,
    163, 155, 175, 151, 139, 163, 135, 123, 151, 123, 111, 135, 111, 95, 123,
    103, 83, 107, 91, 71, 95, 75, 59, 83, 63, 51, 67, 51, 39, 47, 39, 27, 27,
    23, 15, 111, 131, 123, 103, 123, 111, 95, 115, 103, 87, 107, 95, 79, 99,
    87, 71, 91, 79, 63, 83, 71, 55, 75, 63, 47, 67, 51, 39, 59, 43, 33, 47, 35,
    27, 39, 27, 19, 31, 19, 15, 23, 11, 7, 255, 243, 27, 239, 223, 23, 219, 203,
    19, 203, 187, 15, 186, 175, 15, 171, 155, 11, 155, 131, 7, 139, 115, 7,
    123, 99, 7, 107, 83, 0, 91, 71, 0, 75, 55, 0, 59, 43, 0, 43, 31, 0, 27, 15,
    0, 11, 7, 0, 0, 0, 255, 11, 11, 239, 19, 19, 223, 27, 27, 207, 35, 35, 191,
    43, 43, 175, 47, 47, 159, 47, 47, 143, 47, 47, 127, 47, 47, 111, 43, 43, 95,
    35, 35, 63, 27, 27, 47, 19, 19, 31, 11, 11, 15, 43, 0, 0, 59, 0, 0, 75, 7,
    0, 95, 7, 0, 111, 15, 0, 127, 23, 7, 147, 31, 7, 163, 39, 11, 179, 51, 15,
    195, 75, 27, 207, 99, 43, 219, 127, 59, 227, 151, 79, 231, 171, 95, 239,
    191, 119, 247, 211, 139, 167, 123, 59, 183, 155, 55, 199, 195, 55, 231, 227,
    87, 127, 191, 255, 171, 231, 255, 215, 255, 255, 103, 0, 0, 139, 0, 0, 179,
    0, 0, 215, 0, 0, 255, 0, 0, 255, 243, 147, 255, 247, 199, 255, 255, 255,
    159, 91, 83
])

# -----------------------------------------------------------------------------
# Quake sprite file format (little-endian)
# -----------------------------------------------------------------------------

# Main header for the entire sprite file.
# C Source:
# typedef struct {
#     int            ident;          // IDSP
#     int            version;        // SPRITE_VERSION
#     int            type;
#     float          boundingradius;
#     int            width;
#     int            height;
#     int            numframes;
#     float          beamlength;
#     synctype_t     synctype;
# } dsprite_t;
DSpriteHeader = struct.Struct('<4s i i f i i i f i')

# Header for a single frame within the sprite file.
# C Source:
# typedef struct {
#     int origin[2]; // In the C code, this is int, but used as float offsets.
#                    // The python script used float, which is likely correct for modern interpretation.
#                    // However, to match original tool, let's stick to the C struct.
#     int width;
#     int height;
# } dspriteframe_t;
# NOTE: The original C code uses 'int origin[2]', but then assigns float values to it
# during parsing. The python script's use of floats is more accurate to its usage.
DSpriteFrameHeader = struct.Struct('<i i i i')

# Header for a sprite group.
# C Source:
# typedef struct {
#    int            numframes;
# } dspritegroup_t;
DSpriteGroupHeader = struct.Struct('<i')

# Interval for frames within a group.
# C Source:
# typedef struct {
#   float interval;
# } dspriteinterval_t;
DSpriteInterval = struct.Struct('<f')

# Frame type identifier
# C Source:
# typedef enum { SPR_SINGLE=0, SPR_GROUP } spriteframetype_t;
SpriteFrameType = struct.Struct('<i')


def get_closest_color(pixel, palette):
    """Finds the index of the closest color in the palette using Euclidean distance."""
    min_dist = float('inf')
    closest_index = 0
    r1, g1, b1 = pixel

    for i in range(0, len(palette), 3):
        r2 = palette[i]
        g2 = palette[i+1]
        b2 = palette[i+2]
        
        dist = (r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2
        
        if dist < min_dist:
            min_dist = dist
            closest_index = i // 3
            if dist == 0: # Perfect match
                break
            
    return closest_index

def process_image_file(filename, palette):
    """
    Loads an image, converts it to an 8-bit palettized format, and returns
    the image dimensions and raw pixel data.
    """
    if not os.path.exists(filename):
        print(f"Error: Image file not found: {filename}")
        sys.exit(1)
        
    img = Image.open(filename)
    
    # Ensure image is in a format we can work with
    if img.mode not in ['RGB', 'RGBA']:
        img = img.convert('RGB')
    
    width, height = img.size
    pixels = list(img.getdata())
    
    palettized_data = bytearray(width * height)
    for i, pixel in enumerate(pixels):
        # Handle transparency if present
        if len(pixel) == 4 and pixel[3] == 0:
             # Quake uses index 255 for transparency
            palettized_data[i] = 255
        else:
            palettized_data[i] = get_closest_color(pixel[:3], palette)
            
    return width, height, bytes(palettized_data)

def parse_qc_file(qc_file):
    """Parses a QuakeC-style script file and returns a dictionary of sprite data."""
    sprite_data = {
        'output': 'sprite.spr',
        'width': 0,
        'height': 0,
        'type': 0,
        'beamlength': 0.0,
        # Default to ST_RAND (1), as per original tools
        'synctype': 1,
        'frames': []
    }
    
    if not os.path.exists(qc_file):
        print(f"Error: QC file not found: {qc_file}")
        sys.exit(1)
    
    with open(qc_file, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            continue
            
        parts = line.split()
        command = parts[0].lower()
        
        if command == 'output':
            sprite_data['output'] = parts[1]
        elif command == 'maxwidth':
            sprite_data['width'] = int(parts[1])
        elif command == 'maxheight':
            sprite_data['height'] = int(parts[1])
        elif command == 'type':
            sprite_data['type'] = int(parts[1])
        elif command == 'beamlength':
            sprite_data['beamlength'] = float(parts[1])
        elif command == 'synctype':
            # ST_SYNC = 0, ST_RAND = 1
            sprite_data['synctype'] = 0 if parts[1].lower() == 'sync' else 1
        elif command == 'frame':
            frame_info = {
                'filename': parts[1],
                'offset_x': int(parts[2]),
                'offset_y': int(parts[3])
            }
            sprite_data['frames'].append({'type': 'single', 'frame': frame_info})
        # Note: Group/anim logic would need to be expanded here if used.
        
    return sprite_data

def write_spr_file(sprite_data, palette):
    """Writes the sprite data to a Quake .spr file with the correct structure."""
    output_filename = sprite_data['output']
    
    try:
        # Step 1: Process all frames to gather their data and find max dimensions
        frame_payloads = []
        actual_max_w = 0
        actual_max_h = 0
        num_total_frames = 0

        for frame_group in sprite_data['frames']:
            if frame_group['type'] == 'single':
                num_total_frames += 1
                frame_info = frame_group['frame']
                
                width, height, pixel_data = process_image_file(frame_info['filename'], palette)
                
                if width > actual_max_w: actual_max_w = width
                if height > actual_max_h: actual_max_h = height
                
                frame_header = DSpriteFrameHeader.pack(
                    frame_info['offset_x'],
                    frame_info['offset_y'],
                    width,
                    height
                )
                
                frame_payloads.append({
                    'is_group': False,
                    'type_id': 0, # SPR_SINGLE
                    'header': frame_header,
                    'pixels': pixel_data
                })
            # Add logic for 'group' type frames here if needed
            
        # Step 2: Calculate the bounding radius from the *actual* max dimensions
        # This mimics the logic from the original SPRGEN.C
        bounding_radius = sqrt((actual_max_w / 2)**2 + (actual_max_h / 2)**2)

        with open(output_filename, 'wb') as spr_file:
            # Step 3: Write the main dsprite_t header
            main_header = DSpriteHeader.pack(
                b'IDSP',
                1,  # Version
                sprite_data['type'],
                bounding_radius,
                sprite_data['width'],  # Maxwidth from QC
                sprite_data['height'], # Maxheight from QC
                num_total_frames,
                sprite_data['beamlength'],
                sprite_data['synctype']
            )
            spr_file.write(main_header)
            
            # Step 4: Write the frame data in the correct order
            for payload in frame_payloads:
                if not payload['is_group']:
                    # Write frame type (e.g., SPR_SINGLE)
                    spr_file.write(SpriteFrameType.pack(payload['type_id']))
                    # Write frame header
                    spr_file.write(payload['header'])
                    # Write pixel data
                    spr_file.write(payload['pixels'])
                # Add logic for writing group data here
                
        print(f"Successfully created sprite file: {output_filename}")

    except Exception as e:
        print(f"Error writing sprite file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python tga2spr2.py [file.qc ...]")
        return
        
    palette_file = "palette.lmp"
    custom_palette = None
    if os.path.exists(palette_file):
        with open(palette_file, 'rb') as f:
            custom_palette = f.read(768)
        print(f"Using custom palette from {palette_file}")
    else:
        custom_palette = QUAKE_PALETTE
        print("Using built-in Quake palette")
        
    for qc_file in sys.argv[1:]:
        print(f"\nProcessing control file: {qc_file}")
        sprite_data = parse_qc_file(qc_file)
        write_spr_file(sprite_data, custom_palette)

if __name__ == "__main__":
    main()
