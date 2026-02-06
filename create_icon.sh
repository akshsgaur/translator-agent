#!/bin/bash
#
# Convert logo.png to macOS .icns format
# Usage: ./create_icon.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PNG_FILE="$SCRIPT_DIR/logo.png"
ICONSET_DIR="$SCRIPT_DIR/LanguageTutor.iconset"
ICNS_FILE="$SCRIPT_DIR/LanguageTutor.icns"

if [ ! -f "$PNG_FILE" ]; then
    echo "ERROR: logo.png not found"
    exit 1
fi

echo "Creating macOS icon from logo.png..."

# Create iconset directory
mkdir -p "$ICONSET_DIR"

# Generate all required icon sizes
sips -z 16 16     "$PNG_FILE" --out "$ICONSET_DIR/icon_16x16.png"      2>/dev/null
sips -z 32 32     "$PNG_FILE" --out "$ICONSET_DIR/icon_16x16@2x.png"   2>/dev/null
sips -z 32 32     "$PNG_FILE" --out "$ICONSET_DIR/icon_32x32.png"      2>/dev/null
sips -z 64 64     "$PNG_FILE" --out "$ICONSET_DIR/icon_32x32@2x.png"   2>/dev/null
sips -z 128 128   "$PNG_FILE" --out "$ICONSET_DIR/icon_128x128.png"    2>/dev/null
sips -z 256 256   "$PNG_FILE" --out "$ICONSET_DIR/icon_128x128@2x.png" 2>/dev/null
sips -z 256 256   "$PNG_FILE" --out "$ICONSET_DIR/icon_256x256.png"    2>/dev/null
sips -z 512 512   "$PNG_FILE" --out "$ICONSET_DIR/icon_256x256@2x.png" 2>/dev/null
sips -z 512 512   "$PNG_FILE" --out "$ICONSET_DIR/icon_512x512.png"    2>/dev/null
sips -z 1024 1024 "$PNG_FILE" --out "$ICONSET_DIR/icon_512x512@2x.png" 2>/dev/null

# Convert iconset to icns
iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"

# Clean up iconset directory
rm -rf "$ICONSET_DIR"

echo "Icon created: $ICNS_FILE"
