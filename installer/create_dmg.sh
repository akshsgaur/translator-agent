#!/bin/bash
#
# Create a DMG installer for Language Tutor
# Usage: ./create_dmg.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_PATH="$PROJECT_DIR/dist/LanguageTutor.app"
DMG_PATH="$PROJECT_DIR/dist/LanguageTutor.dmg"
DMG_TEMP="$PROJECT_DIR/dist/LanguageTutor_temp.dmg"
VOLUME_NAME="Language Tutor"

echo "Creating DMG installer for Language Tutor..."

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "ERROR: App not found at $APP_PATH"
    echo "Please run 'python build_mac_app.py' first."
    exit 1
fi

# Remove existing DMG files
rm -f "$DMG_PATH" "$DMG_TEMP"

# Get app size and add buffer
APP_SIZE=$(du -sm "$APP_PATH" | cut -f1)
DMG_SIZE=$((APP_SIZE + 50))

echo "App size: ${APP_SIZE}MB, DMG size: ${DMG_SIZE}MB"

# Create temporary DMG
hdiutil create -srcfolder "$APP_PATH" \
    -volname "$VOLUME_NAME" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size ${DMG_SIZE}m \
    "$DMG_TEMP"

# Mount the temporary DMG
MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP" | grep "/Volumes/" | sed 's/.*\/Volumes/\/Volumes/')

echo "Mounted at: $MOUNT_DIR"

# Create Applications symlink for drag-to-install
ln -sf /Applications "$MOUNT_DIR/Applications"

# Optional: Set custom background and icon positions using AppleScript
# This creates a nicer installer experience
osascript <<EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 900, 400}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 80
        set position of item "LanguageTutor.app" of container window to {125, 150}
        set position of item "Applications" of container window to {375, 150}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF

# Sync and unmount
sync
hdiutil detach "$MOUNT_DIR"

# Convert to compressed final DMG
hdiutil convert "$DMG_TEMP" -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH"

# Clean up
rm -f "$DMG_TEMP"

echo ""
echo "DMG created successfully: $DMG_PATH"
echo ""
echo "File size: $(du -h "$DMG_PATH" | cut -f1)"
