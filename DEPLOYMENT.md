# Deployment Guide - Wan2.2 S2V to Modal

This guide will walk you through deploying the Wan2.2-S2V-14B model to Modal platform.

---

## 📋 Prerequisites

1. **Modal Account**
   - Sign up at https://modal.com/
   - Install Modal CLI: `pip install modal`
   - Authenticate: `modal setup`

2. **System Requirements**
   - Python 3.11+
   - ~50GB available for model download (one-time)
   - Internet connection for deployment

3. **API Key (Optional but Recommended)**
   - Generate with: `python generate_api_keys.py`

---

## 🚀 Quick Deployment (5 Steps)

### Step 1: Install Modal
```bash
pip install modal
modal setup
```

### Step 2: Generate API Key (Optional)
```bash
python generate_api_keys.py
```

Save the generated key for later use.

### Step 3: Configure Modal Secret (Optional)
If you generated an API key:

1. Go to https://modal.com/ → Your Workspace → Secrets
2. Click "New Secret"
3. Name: `wan2-api-keys`
4. Add environment variable:
   - **Key:** `WAN2_API_KEYS`
   - **Value:** `your-generated-api-key`
5. Save

### Step 4: Deploy to Modal
```bash
modal deploy wan2_modal.py
```

This will:
- Build the Docker image with all dependencies (~5-10 minutes)
- Deploy the application to Modal
- Return your app URL (e.g., `https://your-username--wan2-s2v-fastapi-app.modal.run`)

### Step 5: Test the Deployment
```bash
# Test health endpoint (no auth required)
curl https://your-app-url.modal.run/health

# Test with test client
python test_client.py \
  --url https://your-app-url.modal.run \
  --api-key your-api-key \
  --health-only
```

---

## 📊 What Happens on First Request

The first video generation request will:
1. **Download the model** (~49GB, one-time, ~10-30 min depending on connection)
2. **Cache the model** in Modal Volume (persistent across requests)
3. **Generate the video** (~15-20 minutes for 720p)

Subsequent requests will skip step 1 and use the cached model.

---

## 🧪 Testing the API

### Test 1: Health Check (No Auth)
```bash
curl https://your-app-url.modal.run/health
```

Expected response:
```json
{
  "status": "healthy",
  "model": "Wan2.2-S2V-14B"
}
```

### Test 2: API Information
```bash
curl https://your-app-url.modal.run/
```

### Test 3: Generate Video (Requires Auth if configured)

#### Using cURL:
```bash
curl -X POST https://your-app-url.modal.run/generate-video \
  -H "X-API-Key: your-api-key" \
  -F "image=@reference.jpg" \
  -F "audio=@audio.wav" \
  -F "prompt=A person talking about technology" \
  -F "resolution=720p"
```

#### Using Test Client (Recommended):
```bash
python test_client.py \
  --url https://your-app-url.modal.run \
  --api-key your-api-key \
  --image examples/reference.jpg \
  --audio examples/audio.wav \
  --prompt "A person talking" \
  --resolution 720p \
  --output my_video.mp4
```

---

## 📂 Prepare Test Files

You'll need:
1. **Reference Image** (JPG/PNG) - A photo/image of a person or character
2. **Audio File** (WAV/MP3) - Speech, singing, or other audio

### Example Test Files:
You can use:
- Sample image: Any portrait photo
- Sample audio: Record a short audio clip or use text-to-speech

```bash
# Example directory structure
examples/
  ├── reference.jpg    # Your reference image
  └── audio.wav        # Your audio file
```

---

## ⚙️ Configuration Options

### GPU Configuration
Edit `wan2_modal.py` to change GPU:

```python
@app.cls(
    gpu="A100-80GB",  # Options: "A100-40GB", "A100-80GB", "H100"
    timeout=1800,      # Increase for longer videos
    ...
)
```

### Resolution Options
- `480p` - Faster generation (~10 min), lower quality
- `720p` - Standard generation (~15-20 min), good quality

### Timeout Settings
```python
timeout=1800  # 30 minutes (default)
timeout=3600  # 60 minutes (for longer videos)
```

---

## 💰 Cost Estimates

### Per Video Generation:
| Resolution | GPU | Time | Cost |
|------------|-----|------|------|
| 480p | A100-80GB | ~10 min | ~$0.67 |
| 720p | A100-80GB | ~15-20 min | ~$1.00-$1.33 |

### First-Time Setup:
- Model download: ~30 min on A100-80GB = ~$2.00 (one-time)
- Storage: Modal Volume ~50GB = ~$0.30/month

### Monthly Estimates:
- Light (10 videos/month): ~$10-15
- Medium (50 videos/month): ~$50-75
- Heavy (200 videos/month): ~$200-300

---

## 🔍 Monitoring and Logs

### View Logs in Modal Dashboard:
1. Go to https://modal.com/
2. Click on your app: `wan2-s2v`
3. View real-time logs and metrics

### Check Container Status:
```bash
modal app logs wan2-s2v
```

### View Volume Contents:
```bash
modal volume ls wan2-models
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution:** Redeploy with `modal deploy wan2_modal.py`

### Issue: "Model download taking too long"
**Solution:** First download is ~49GB. Wait 10-30 minutes. Check logs:
```bash
modal app logs wan2-s2v
```

### Issue: "Generation timing out"
**Solution:** Increase timeout in `wan2_modal.py`:
```python
timeout=3600  # 60 minutes
```

### Issue: "Out of memory"
**Solution:** Model requires minimum 80GB VRAM. Verify GPU:
```python
gpu="A100-80GB"  # Not "A100-40GB"
```

### Issue: "API key not working"
**Solution:** 
1. Verify Modal Secret is named: `wan2-api-keys`
2. Verify env var is: `WAN2_API_KEYS` (not `API_KEY`)
3. Redeploy after changing secrets

---

## 🔄 Updating the Deployment

### Update Code:
```bash
# After modifying wan2_modal.py
modal deploy wan2_modal.py
```

### Update API Keys:
1. Update Modal Secret: `wan2-api-keys`
2. Redeploy: `modal deploy wan2_modal.py`

### Clear Model Cache (if needed):
```bash
modal volume delete wan2-models
# Redeploy to recreate
modal deploy wan2_modal.py
```

---

## 📊 Production Recommendations

### 1. Enable API Key Authentication
- Generate strong keys with `generate_api_keys.py`
- Configure Modal Secret
- Never expose keys in code

### 2. Implement Job Queue
For production, consider:
- Async job processing
- Webhook callbacks
- Status polling endpoint

### 3. Add Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

### 4. Enable Monitoring
- Log all requests
- Track generation times
- Monitor costs

### 5. Use Multiple GPUs (Optional)
For faster generation:
```python
gpu="A100-80GB:4"  # 4 GPUs
```

---

## 📚 Additional Resources

- [Modal Documentation](https://modal.com/docs)
- [Wan2.2 GitHub](https://github.com/Wan-Video/Wan2.2)
- [Wan2.2-S2V HuggingFace](https://huggingface.co/Wan-AI/Wan2.2-S2V-14B)
- [API Key Setup Guide](API_KEY_SETUP.md)

---

## ✅ Deployment Checklist

- [ ] Modal account created and CLI installed
- [ ] Modal authenticated: `modal setup`
- [ ] API key generated (optional)
- [ ] Modal Secret configured (optional)
- [ ] App deployed: `modal deploy wan2_modal.py`
- [ ] Health check passing
- [ ] Test files prepared (image + audio)
- [ ] First test generation successful
- [ ] Production API key configured (if production)
- [ ] Monitoring enabled

**You're ready to generate videos! 🎉**

---

## 🆘 Getting Help

1. Check the [troubleshooting section](#-troubleshooting)
2. View Modal logs: `modal app logs wan2-s2v`
3. Check Modal dashboard for errors
4. Review [API_KEY_SETUP.md](API_KEY_SETUP.md) for auth issues
5. Verify GPU and timeout settings in `wan2_modal.py`

For Modal-specific issues, see: https://modal.com/docs
