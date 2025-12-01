#!/usr/bin/env python3
"""
API Key Generator for Wan2.2 S2V Modal Deployment

Usage:
    python generate_api_keys.py           # Generate 1 key
    python generate_api_keys.py 5         # Generate 5 keys
"""

import secrets
import sys
import json
from datetime import datetime


def generate_key():
    """Generate a single secure API key"""
    return secrets.token_urlsafe(32)


def main():
    # Determine how many keys to generate
    count = 1
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            if count < 1 or count > 100:
                print("Error: Please specify between 1 and 100 keys")
                sys.exit(1)
        except ValueError:
            print("Error: Please provide a valid number")
            sys.exit(1)
    
    # Generate keys
    keys = [generate_key() for _ in range(count)]
    
    # Display results
    print("=" * 70)
    print(f"  Wan2.2 S2V API Key Generator")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    if count == 1:
        print(f"Generated API Key:")
        print(f"  {keys[0]}")
    else:
        print(f"Generated {count} API Keys:")
        for i, key in enumerate(keys, 1):
            print(f"  {i}. {key}")
    
    print()
    print("-" * 70)
    print("Modal Secret Configuration:")
    print("-" * 70)
    print()
    print("1. Go to https://modal.com/ -> Your Workspace -> Secrets")
    print("2. Create/Edit Secret: 'wan2-api-keys'")
    print("3. Add environment variable:")
    print()
    print("   Key:   WAN2_API_KEYS")
    print(f"   Value: {','.join(keys)}")
    print()
    print("-" * 70)
    print()
    
    # Save to file
    output_file = f"api_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "keys": keys,
            "modal_secret_name": "wan2-api-keys",
            "environment_variable": "WAN2_API_KEYS",
            "value": ','.join(keys)
        }, f, indent=2)
    
    print(f"[OK] Keys saved to: {output_file}")
    print()
    print("[!] SECURITY WARNING:")
    print("   - Keep these keys secure and private")
    print("   - Do NOT commit this file to version control")
    print("   - Add *.json to your .gitignore")
    print("   - Delete this file after configuring Modal Secret")
    print()


if __name__ == "__main__":
    main()
