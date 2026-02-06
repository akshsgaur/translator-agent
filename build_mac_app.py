#!/usr/bin/env python3
"""
Build script for Language Tutor Mac App

Usage:
    python build_mac_app.py          # Build the app
    python build_mac_app.py --clean  # Clean and rebuild
    python build_mac_app.py --dmg    # Build app and create DMG
"""

import os
import sys
import shutil
import subprocess
import argparse


def get_project_dir():
    """Get the project directory."""
    return os.path.dirname(os.path.abspath(__file__))


def clean_build():
    """Remove previous build artifacts."""
    project_dir = get_project_dir()
    dirs_to_remove = ['build', 'dist']

    for dir_name in dirs_to_remove:
        dir_path = os.path.join(project_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"Removing {dir_path}...")
            shutil.rmtree(dir_path)

    print("Clean complete.")


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    # Check for PyInstaller
    try:
        import PyInstaller
        print(f"  PyInstaller {PyInstaller.__version__} - OK")
    except ImportError:
        print("  PyInstaller - NOT FOUND")
        print("\nPlease install PyInstaller: pip install pyinstaller")
        sys.exit(1)

    # Check for customtkinter
    try:
        import customtkinter
        print(f"  customtkinter - OK")
    except ImportError:
        print("  customtkinter - NOT FOUND")
        print("\nPlease install customtkinter: pip install customtkinter")
        sys.exit(1)

    print("All dependencies OK.\n")


def build_app():
    """Build the Mac application using PyInstaller."""
    project_dir = get_project_dir()
    spec_file = os.path.join(project_dir, 'LanguageTutor.spec')

    if not os.path.exists(spec_file):
        print(f"ERROR: Spec file not found: {spec_file}")
        sys.exit(1)

    print("Building Language Tutor.app...")
    print("This may take a few minutes...\n")

    # Run PyInstaller
    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', spec_file, '--noconfirm'],
        cwd=project_dir
    )

    if result.returncode != 0:
        print("\nBuild failed!")
        sys.exit(1)

    app_path = os.path.join(project_dir, 'dist', 'LanguageTutor.app')
    if os.path.exists(app_path):
        print(f"\nBuild successful!")
        print(f"App location: {app_path}")
        print(f"\nTo install, drag LanguageTutor.app to your Applications folder.")
        return app_path
    else:
        print("\nBuild completed but app not found!")
        sys.exit(1)


def create_dmg():
    """Create a DMG installer for distribution."""
    project_dir = get_project_dir()
    app_path = os.path.join(project_dir, 'dist', 'LanguageTutor.app')
    dmg_path = os.path.join(project_dir, 'dist', 'LanguageTutor.dmg')

    if not os.path.exists(app_path):
        print("ERROR: App not found. Please build the app first.")
        sys.exit(1)

    print("\nCreating DMG installer...")

    # Remove existing DMG
    if os.path.exists(dmg_path):
        os.remove(dmg_path)

    # Create DMG using hdiutil
    result = subprocess.run([
        'hdiutil', 'create',
        '-volname', 'Language Tutor',
        '-srcfolder', app_path,
        '-ov',
        '-format', 'UDZO',
        dmg_path
    ])

    if result.returncode != 0:
        print("Failed to create DMG!")
        sys.exit(1)

    print(f"\nDMG created: {dmg_path}")
    print("\nDistribution files ready:")
    print(f"  - App: {app_path}")
    print(f"  - DMG: {dmg_path}")


def main():
    parser = argparse.ArgumentParser(description='Build Language Tutor Mac App')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts before building')
    parser.add_argument('--dmg', action='store_true', help='Create DMG installer after building')
    parser.add_argument('--clean-only', action='store_true', help='Only clean, do not build')
    args = parser.parse_args()

    print("=" * 50)
    print("Language Tutor - Mac App Builder")
    print("=" * 50 + "\n")

    if args.clean_only:
        clean_build()
        return

    if args.clean:
        clean_build()
        print()

    check_dependencies()
    build_app()

    if args.dmg:
        create_dmg()

    print("\n" + "=" * 50)
    print("Build complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
