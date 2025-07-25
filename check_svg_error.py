#!/usr/bin/env python3
"""Check for SVG GANTT errors in the browser console."""

import time
import requests

BASE_URL = "http://localhost:9094"

print("Testing SVG GANTT implementation...")
print("\nPlease check the browser console for errors:")
print(f"1. Open {BASE_URL}/idea/3 in your browser")
print("2. Open Developer Tools (F12)")
print("3. Check the Console tab for any errors")
print("4. Look for:")
print("   - 'SVGGanttChart is not defined' errors")
print("   - 404 errors for svg-gantt.js")
print("   - Any JavaScript syntax errors")
print("\nAlso check the Network tab to see if svg-gantt.js loads successfully")

# Test if the file is accessible
response = requests.get(f"{BASE_URL}/static/js/svg-gantt.js")
print(f"\nDirect access to svg-gantt.js: {response.status_code}")
if response.status_code == 200:
    print(f"File size: {len(response.content)} bytes")
    print("First 100 chars:", response.text[:100])