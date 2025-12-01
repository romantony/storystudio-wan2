# API Key Setup Guide for Wan2.2 S2V Modal Deployment

This guide explains how to set up and use API key authentication for the Wan2.2-S2V-14B Modal deployment.

---

## 🔐 Setting Up API Keys in Modal

### Step 1: Create a Modal Secret

1. **Go to Modal Dashboard:**
   - Visit https://modal.com/
   - Navigate to your workspace
   - Go to "Secrets" section

2. **Create New Secret:**
   - Click "New Secret"
   - Name it: `wan2-api-keys`
   - Add environment variable:
     - **Key:** `WAN2_API_KEYS`
     - **Value:** Your API key(s)

### Step 2: Generate Secure API Keys

You can generate secure API keys using any of these methods:

#### Method 1: Python (Recommended)
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"Your API Key: {api_key}")
```

#### Method 2: OpenSSL
```bash
openssl rand -base64 32
```

#### Method 3: Online Generator
Use a trusted password generator like:
- https://1password.com/password-generator/
- https://bitwarden.com/password-generator/

### Step 3: Configure Multiple API Keys (Optional)

To support multiple API keys (e.g., for different users/services), use comma-separated values:

```
WAN2_API_KEYS=key1_abc123xyz789,key2_def456uvw012,key3_ghi789rst345
```

---

## 📡 Using the API

### Authentication

All API requests must include the API key in the `X-API-Key` header:

```http
X-API-Key: your-api-key-here
```

### Endpoints

#### 1. Health Check (No Auth Required)
```bash
curl https://your-app.modal.run/health
```

Response:
```json
{
  "status": "healthy",
  "model": "Wan2.2-S2V-14B"
}
```

#### 2. API Information
```bash
curl https://your-app.modal.run/
```

Response:
```json
{
  "status": "online",
  "model": "Wan2.2-S2V-14B",
  "version": "0.1.0",
  "endpoints": {
    "POST /generate-video": "Generate video from audio and image",
    "GET /health": "Health check"
  },
  "authentication": {
    "required": true,
    "method": "API Key in X-API-Key header",
    "status": "enabled"
  },
  "supported_formats": {
    "image": ["JPG", "PNG"],
    "audio": ["WAV", "MP3"],
    "output": "MP4 (24fps)"
  },
  "resolutions": ["480p", "720p"]
}
```

#### 3. Generate Video (Requires Auth)

**Basic Usage:**
```bash
curl -X POST https://your-app.modal.run/generate-video \
  -H "X-API-Key: your-api-key-here" \
  -F "image=@reference.jpg" \
  -F "audio=@audio.wav" \
  -F "prompt=A person talking about technology" \
  -F "resolution=720p"
```

**With All Parameters:**
```bash
curl -X POST https://your-app.modal.run/generate-video \
  -H "X-API-Key: your-api-key-here" \
  -F "image=@reference.jpg" \
  -F "audio=@audio.wav" \
  -F "prompt=Summer beach vacation style" \
  -F "resolution=720p" \
  -F "num_clips=5" \
  -F "pose_video=@pose.mp4"
```

**Python Example:**
```python
import requests

url = "https://your-app.modal.run/generate-video"
headers = {
    "X-API-Key": "your-api-key-here"
}
files = {
    "image": ("reference.jpg", open("reference.jpg", "rb"), "image/jpeg"),
    "audio": ("audio.wav", open("audio.wav", "rb"), "audio/wav"),
}
data = {
    "prompt": "A person talking",
    "resolution": "720p",
}

response = requests.post(url, headers=headers, files=files, data=data)
if response.status_code == 200:
    result = response.json()
    print("Video generated successfully!")
    # Video is base64 encoded in result['video']
else:
    print(f"Error: {response.json()['detail']}")
```

**JavaScript/Node.js Example:**
```javascript
const FormData = require('form-data');
const fs = require('fs');
const fetch = require('node-fetch');

const formData = new FormData();
formData.append('image', fs.createReadStream('reference.jpg'));
formData.append('audio', fs.createReadStream('audio.wav'));
formData.append('prompt', 'A person talking');
formData.append('resolution', '720p');

fetch('https://your-app.modal.run/generate-video', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-api-key-here'
  },
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Video generated:', data);
})
.catch(error => console.error('Error:', error));
```

---

## 🔒 Security Best Practices

### 1. Keep API Keys Secret
- ❌ Never commit API keys to version control
- ❌ Never expose keys in client-side code
- ✅ Use environment variables
- ✅ Rotate keys periodically

### 2. Use Environment Variables
```bash
# .env file (never commit this!)
WAN2_API_KEY=your-api-key-here

# Usage in Python
import os
api_key = os.environ.get("WAN2_API_KEY")
```

### 3. Implement Rate Limiting (Future Enhancement)
```python
# Future: Add to Modal deployment
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
web_app.state.limiter = limiter

@web_app.post("/generate-video")
@limiter.limit("5/minute")  # 5 requests per minute
async def generate_video(...):
    ...
```

---

## 🚨 Error Responses

### 401 Unauthorized - Missing API Key
```json
{
  "detail": "Missing API key. Include 'X-API-Key' header with your API key."
}
```

**Solution:** Add the `X-API-Key` header to your request.

### 403 Forbidden - Invalid API Key
```json
{
  "detail": "Invalid API key. Please check your credentials."
}
```

**Solution:** Verify your API key is correct and active.

### 422 Unprocessable Entity - Invalid Parameters
```json
{
  "detail": [
    {
      "loc": ["body", "image"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution:** Ensure all required parameters are provided.

---

## 🧪 Testing Mode (No Authentication)

If you want to test the API without authentication:

1. **Don't create the Modal Secret**, or
2. **Create the Secret with empty value**

The API will run in testing mode:
```json
{
  "authentication": {
    "required": false,
    "status": "disabled (testing mode)"
  }
}
```

⚠️ **Warning:** Only use this for development! Always enable authentication in production.

---

## 📊 Monitoring API Usage

### Track Requests
Monitor API usage through:
1. Modal dashboard logs
2. Custom logging (add to each endpoint)
3. Third-party analytics (e.g., PostHog, Mixpanel)

### Example: Add Request Logging
```python
import logging
from datetime import datetime

@web_app.post("/generate-video")
async def generate_video(...):
    logging.info(f"Video generation requested at {datetime.now()}")
    logging.info(f"Resolution: {resolution}, Prompt: {prompt}")
    # ... rest of the code
```

---

## 🔄 Key Rotation

To rotate API keys without downtime:

1. **Add new key** to Modal Secret (comma-separated):
   ```
   WAN2_API_KEYS=old-key,new-key
   ```

2. **Update clients** to use new key

3. **Remove old key** after all clients updated:
   ```
   WAN2_API_KEYS=new-key
   ```

---

## 📝 API Key Management Script

Save this script for easy key management:

```python
#!/usr/bin/env python3
"""
API Key Management for Wan2.2 S2V Modal Deployment
"""
import secrets
import sys

def generate_key():
    """Generate a new secure API key"""
    key = secrets.token_urlsafe(32)
    print(f"Generated API Key: {key}")
    print(f"\nAdd to Modal Secret 'wan2-api-keys':")
    print(f"WAN2_API_KEYS={key}")
    return key

def generate_multiple_keys(count=3):
    """Generate multiple API keys"""
    keys = [secrets.token_urlsafe(32) for _ in range(count)]
    print(f"Generated {count} API Keys:\n")
    for i, key in enumerate(keys, 1):
        print(f"Key {i}: {key}")
    
    print(f"\nAdd to Modal Secret 'wan2-api-keys':")
    print(f"WAN2_API_KEYS={','.join(keys)}")
    return keys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        generate_multiple_keys(int(sys.argv[1]))
    else:
        generate_key()
```

Usage:
```bash
# Generate 1 key
python generate_keys.py

# Generate 5 keys
python generate_keys.py 5
```

---

## 📞 Support

For issues with API key authentication:
1. Check Modal dashboard for Secret configuration
2. Verify environment variable name: `WAN2_API_KEYS`
3. Test with `/health` endpoint first
4. Check Modal logs for detailed error messages

---

## 🎯 Quick Start Checklist

- [ ] Generate secure API key(s)
- [ ] Create Modal Secret named `wan2-api-keys`
- [ ] Add environment variable `WAN2_API_KEYS`
- [ ] Deploy Modal app
- [ ] Test with `/health` endpoint
- [ ] Test with `X-API-Key` header on `/generate-video`
- [ ] Store API key securely (password manager/env vars)
- [ ] Document key for your team/users

**You're ready to use the Wan2.2 S2V API! 🚀**
