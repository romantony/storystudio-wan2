#!/usr/bin/env python3
"""
Quick deployment script for Wan2.2 S2V to Modal

This script automates the deployment process.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'=' * 70}")
    print(f"📋 {description}")
    print(f"{'=' * 70}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print(f"Please install it first: pip install {cmd[0]}")
        return False


def check_modal_installed():
    """Check if Modal is installed"""
    try:
        subprocess.run(["modal", "--version"], check=True, capture_output=True)
        return True
    except:
        return False


def check_modal_authenticated():
    """Check if Modal is authenticated"""
    try:
        result = subprocess.run(["modal", "profile", "current"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def main():
    print("=" * 70)
    print("🚀 Wan2.2 S2V Modal Deployment Script")
    print("=" * 70)
    
    # Step 1: Check Modal installation
    print("\n[1/5] Checking Modal installation...")
    if not check_modal_installed():
        print("❌ Modal is not installed")
        print("\nInstalling Modal...")
        if not run_command([sys.executable, "-m", "pip", "install", "modal"], "Install Modal"):
            print("\n⚠️  Failed to install Modal. Please run: pip install modal")
            return False
    else:
        print("✅ Modal is installed")
    
    # Step 2: Check Modal authentication
    print("\n[2/5] Checking Modal authentication...")
    if not check_modal_authenticated():
        print("❌ Modal is not authenticated")
        print("\nPlease run: modal setup")
        print("Then run this script again.")
        return False
    else:
        print("✅ Modal is authenticated")
    
    # Step 3: Generate API key (optional)
    print("\n[3/5] API Key Setup (optional)")
    response = input("Do you want to generate an API key? (y/n): ").lower()
    
    if response == 'y':
        if Path("generate_api_keys.py").exists():
            run_command([sys.executable, "generate_api_keys.py"], "Generate API Key")
            print("\n⚠️  Remember to configure Modal Secret:")
            print("   1. Go to https://modal.com/ → Secrets")
            print("   2. Create secret: 'wan2-api-keys'")
            print("   3. Add environment variable: WAN2_API_KEYS=your-key")
            input("\nPress Enter when you've configured the secret (or skip by pressing Enter)...")
        else:
            print("⚠️  generate_api_keys.py not found. Skipping...")
    else:
        print("⚠️  Skipping API key generation. API will run without authentication.")
    
    # Step 4: Deploy to Modal
    print("\n[4/5] Deploying to Modal...")
    print("This will build the Docker image and deploy the app.")
    print("It may take 5-10 minutes on first deployment.")
    
    if not run_command(["modal", "deploy", "wan2_modal.py"], "Deploy to Modal"):
        print("\n❌ Deployment failed. Check the errors above.")
        return False
    
    # Step 5: Test deployment
    print("\n[5/5] Testing deployment...")
    print("\n✅ Deployment successful!")
    print("\n" + "=" * 70)
    print("🎉 Your Wan2.2 S2V API is now live!")
    print("=" * 70)
    
    print("\n📋 Next Steps:")
    print("1. Get your app URL from the deployment output above")
    print("   It looks like: https://your-username--wan2-s2v-fastapi-app.modal.run")
    print("\n2. Test the health endpoint:")
    print("   curl https://your-app-url.modal.run/health")
    print("\n3. Generate a test video:")
    print("   python test_client.py \\")
    print("     --url https://your-app-url.modal.run \\")
    print("     --api-key your-api-key \\")
    print("     --image your-image.jpg \\")
    print("     --audio your-audio.wav")
    print("\n4. Read DEPLOYMENT.md for detailed instructions")
    print("\n" + "=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
