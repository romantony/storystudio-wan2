#!/usr/bin/env python3
"""
Simple client to test Wan2.2 S2V Modal API

Usage:
    python test_client.py --url https://your-app.modal.run --api-key your-key --image test.jpg --audio test.wav
"""

import requests
import argparse
import base64
import json
import time
from pathlib import Path


def test_generate_video(base_url: str, api_key: str, image_path: str, audio_path: str, 
                       prompt: str = "", resolution: str = "720p", output: str = "output.mp4"):
    """Test video generation endpoint"""
    
    print("=" * 70)
    print("🎬 Wan2.2 S2V Video Generation Test")
    print("=" * 70)
    print(f"API URL: {base_url}")
    print(f"Image: {image_path}")
    print(f"Audio: {audio_path}")
    print(f"Prompt: {prompt}")
    print(f"Resolution: {resolution}")
    print(f"Output: {output}")
    print("=" * 70)
    
    # Prepare request
    url = f"{base_url}/generate-video"
    headers = {"X-API-Key": api_key} if api_key else {}
    
    files = {
        "image": (Path(image_path).name, open(image_path, "rb"), "image/jpeg"),
        "audio": (Path(audio_path).name, open(audio_path, "rb"), "audio/wav"),
    }
    
    data = {
        "prompt": prompt,
        "resolution": resolution,
    }
    
    print("\n🚀 Sending request to API...")
    print("⏱️  This may take 15-20 minutes for 720p video generation...")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=2000)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Request completed in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        
        if response.status_code == 200:
            result = response.json()
            
            if "video" in result:
                # Decode base64 video
                video_data = base64.b64decode(result["video"])
                
                # Save video
                with open(output, "wb") as f:
                    f.write(video_data)
                
                print(f"\n🎉 Success! Video saved to: {output}")
                print(f"📊 Video size: {len(video_data) / (1024*1024):.2f} MB")
                print(f"📺 Format: {result.get('format', 'mp4')}")
                print(f"📐 Resolution: {result.get('resolution', resolution)}")
            else:
                print(f"\n⚠️  Response doesn't contain video data")
                print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️  Request timed out after {time.time() - start_time:.1f} seconds")
        print("This is normal for video generation. The server is still processing.")
        print("Consider implementing a job queue system for production.")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
        print("Make sure the Modal app is deployed and the URL is correct.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_health(base_url: str):
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_info(base_url: str):
    """Test info endpoint"""
    print("\nℹ️  Testing info endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ API Info:")
            print(json.dumps(info, indent=2))
            return True
        else:
            print(f"❌ Info check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Info check error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test Wan2.2 S2V Modal API")
    parser.add_argument("--url", required=True, help="Base URL of Modal app")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--image", help="Path to reference image")
    parser.add_argument("--audio", help="Path to audio file")
    parser.add_argument("--prompt", default="", help="Text prompt")
    parser.add_argument("--resolution", default="720p", choices=["480p", "720p"], help="Output resolution")
    parser.add_argument("--output", default="output.mp4", help="Output video path")
    parser.add_argument("--health-only", action="store_true", help="Only test health endpoint")
    
    args = parser.parse_args()
    
    # Normalize URL
    base_url = args.url.rstrip('/')
    
    # Test health
    if not test_health(base_url):
        print("\n⚠️  Health check failed. App may not be ready.")
    
    # Test info
    test_info(base_url)
    
    # Exit if health-only
    if args.health_only:
        return
    
    # Validate inputs for video generation
    if not args.image or not args.audio:
        print("\n⚠️  To generate video, provide --image and --audio parameters")
        return
    
    if not Path(args.image).exists():
        print(f"\n❌ Image file not found: {args.image}")
        return
    
    if not Path(args.audio).exists():
        print(f"\n❌ Audio file not found: {args.audio}")
        return
    
    # Generate video
    test_generate_video(
        base_url=base_url,
        api_key=args.api_key,
        image_path=args.image,
        audio_path=args.audio,
        prompt=args.prompt,
        resolution=args.resolution,
        output=args.output
    )


if __name__ == "__main__":
    main()
