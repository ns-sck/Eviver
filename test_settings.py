#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from utils.properties import (
        SETTINGS_FILE, EDITOR_TEXT_COLOR, EDITOR_BACKGROUND_COLOR, 
        EDITOR_FONT, EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE,
        SYNTAX_KEYWORD, load_settings_from_json
    )
    
    print("Successfully imported properties module")
    
    print(f"\nCurrent Settings:")
    print(f"SETTINGS_FILE: {SETTINGS_FILE}")
    print(f"EDITOR_TEXT_COLOR: {EDITOR_TEXT_COLOR.name()}")
    print(f"EDITOR_BACKGROUND_COLOR: {EDITOR_BACKGROUND_COLOR.name()}")
    print(f"EDITOR_FONT: {EDITOR_FONT.family()}, {EDITOR_FONT.pointSize()}")
    print(f"SYNTAX_KEYWORD: {SYNTAX_KEYWORD.name()}")
    
    if os.path.exists(SETTINGS_FILE):
        print(f"\nSettings file exists at: {SETTINGS_FILE}")
        
        import json
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            
        print("\nVerifying settings:")
        for key, value in settings.items():
            if key in dir():
                if key.endswith('_COLOR') or key.startswith('SYNTAX_'):
                    local_value = locals()[key].name()
                    print(f"{key}: {value} -> {local_value}")
                else:
                    local_value = locals()[key]
                    print(f"{key}: {value} -> {local_value}")
            else:
                print(f"{key}: Not imported in this script")
    else:
        print(f"\nSettings file does not exist: {SETTINGS_FILE}")
        
except ImportError as e:
    print(f"Error importing properties module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("\nTest completed successfully!") 