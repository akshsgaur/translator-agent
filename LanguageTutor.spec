# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Language Tutor Mac App
Run with: pyinstaller LanguageTutor.spec
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect data files from various packages
datas = [
    # Include the logo
    (os.path.join(spec_dir, 'logo.png'), '.'),
    # Include .env file for default configuration
    (os.path.join(spec_dir, '.env'), '.'),
    # Include the data directory
    (os.path.join(spec_dir, 'data'), 'data'),
    # Include src directory
    (os.path.join(spec_dir, 'src'), 'src'),
]

# Add customtkinter data files (themes, etc.)
datas += collect_data_files('customtkinter')

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'tiktoken_ext.openai_public',
    'tiktoken_ext',
    'customtkinter',
    'darkdetect',
    'PIL',
    'PIL._tkinter_finder',
    # LangChain core modules
    'langchain',
    'langchain.schema',
    'langchain.schema.runnable',
    'langchain.schema.messages',
    'langchain.schema.output_parser',
    'langchain.agents',
    'langchain.tools',
    'langchain.memory',
    'langchain.prompts',
    'langchain.chains',
    # LangChain core (newer versions)
    'langchain_core',
    'langchain_core.messages',
    'langchain_core.prompts',
    'langchain_core.output_parsers',
    'langchain_core.runnables',
    'langchain_core.language_models',
    # LangChain community
    'langchain_community',
    'langchain_community.llms',
    'langchain_community.llms.ollama',
    'langchain_community.chat_models',
    # Other dependencies
    'langsmith',
    'ollama',
    'pydantic',
    'pydantic_core',
    'dotenv',
    'pandas',
    'numpy',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    # Include all submodules that might be dynamically imported
    *collect_submodules('langchain'),
    *collect_submodules('langchain_core'),
    *collect_submodules('langchain_classic'),
    *collect_submodules('langchain_community'),
    *collect_submodules('langsmith'),
    *collect_submodules('pydantic'),
]

a = Analysis(
    [os.path.join(spec_dir, 'main_enhanced.py')],
    pathex=[spec_dir, os.path.join(spec_dir, 'src')],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LanguageTutor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=True,  # Enable argv emulation for macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LanguageTutor',
)

app = BUNDLE(
    coll,
    name='LanguageTutor.app',
    icon=os.path.join(spec_dir, 'LanguageTutor.icns'),
    bundle_identifier='com.languagetutor.app',
    info_plist={
        'CFBundleName': 'Language Tutor',
        'CFBundleDisplayName': 'Language Tutor',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleIdentifier': 'com.languagetutor.app',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'CFBundleDocumentTypes': [],
        'LSApplicationCategoryType': 'public.app-category.education',
    },
)
