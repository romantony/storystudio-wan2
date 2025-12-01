# Wan2.2 S2V-14B Modal Deployment

Audio-driven cinematic video generation model deployed on Modal platform.

## Model Information

**Wan2.2-S2V-14B** is a state-of-the-art audio-driven video generation model that creates cinematic-quality videos from:
- Audio input (speech, singing, etc.)
- Reference image
- Optional text prompt
- Optional pose video

**Key Features:**
- 🎬 Cinematic quality video generation
- 🎵 Audio-driven character animation
- 📸 High-quality lip sync
- 🎭 Pose-driven generation support
- 🌟 14B parameter MoE architecture
- 📺 720P @ 24fps output

## Quick Start (3 Steps)

### Option A: Automated Deployment (Easiest)
```bash
python deploy.py
```
This script will guide you through the entire deployment process!

### Option B: Manual Deployment

#### 1. Prerequisites & Deploy
```bash
pip install modal
modal setup
modal deploy wan2_modal.py
```

#### 2. Test the Deployment
```bash
# Get your app URL from deployment output
# Test health endpoint
curl https://your-app-url.modal.run/health

# Test video generation
python test_client.py \
  --url https://your-app-url.modal.run \
  --image reference.jpg \
  --audio audio.wav \
  --prompt "A person talking"
```

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions.

### 3. Use the API

**HTTP Request:**
```bash
curl -X POST https://your-app.modal.run/generate-video \
  -H "X-API-Key: your-api-key-here" \
  -F "image=@reference.jpg" \
  -F "audio=@audio.wav" \
  -F "prompt=A person talking" \
  -F "resolution=720p"
```

**Python Client:**
```python
import requests

url = "https://your-app.modal.run/generate-video"
headers = {"X-API-Key": "your-api-key-here"}
files = {
    "image": open("reference.jpg", "rb"),
    "audio": open("audio.wav", "rb"),
}
data = {
    "prompt": "A person talking",
    "resolution": "720p"
}

response = requests.post(url, headers=headers, files=files, data=data)
video_data = response.json()
```

## Model Specifications

| Aspect | Details |
|--------|---------|
| **Parameters** | 14B (MoE: 27B total, 14B active) |
| **Model Size** | ~60GB |
| **Min GPU** | 1x A100-80GB |
| **Recommended** | 4-8x A100-80GB |
| **Output Resolution** | 480P, 720P |
| **Frame Rate** | 24fps |
| **Generation Time** | 3-20 minutes |

## Cost Estimates

| Configuration | Time/Video | Cost/Video | Cost/Hour |
|---------------|-----------|-----------|-----------|
| 1x A100-80GB | 15 min | $1.00 | $4.00 |
| 4x A100-80GB | 5 min | $1.33 | $16.00 |
| 8x A100-80GB | 3 min | $1.60 | $32.00 |

## Features

### Supported Inputs
- ✅ Audio formats: WAV, MP3, AAC
- ✅ Image formats: JPG, PNG
- ✅ Video formats: MP4 (for pose)
- ✅ Resolutions: 480P, 720P

### Use Cases
- 🎤 Speech-to-video generation
- 🎵 Music video creation
- 🎭 Character animation
- 📹 Lip-sync video editing
- 🎬 Film production

## Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Technical details and architecture
- [API Key Setup](API_KEY_SETUP.md) - **Security and authentication guide**
- [Model Details Verified](MODEL_DETAILS_VERIFIED.md) - Complete model specifications

## Repository Structure

```
storystudio-wan2/
├── wan2_modal.py          # Modal deployment
├── wan2_model.py          # Model wrapper
├── wan2_audio.py          # Audio processing
├── wan2_generate.py       # Generation pipeline
├── requirements.txt       # Dependencies
├── README.md             # This file
├── IMPLEMENTATION_PLAN.md
├── tests/
│   ├── test_generation.py
│   └── test_api.py
└── examples/
    ├── basic_generation.py
    ├── pose_driven.py
    └── batch_process.py
```

## Security

### API Key Authentication
This deployment uses API key authentication via the `X-API-Key` header.

**Setup:**
1. Generate key: `python generate_api_keys.py`
2. Configure Modal Secret: `wan2-api-keys`
3. Set environment variable: `WAN2_API_KEYS`

**Best Practices:**
- ✅ Use strong, randomly generated keys
- ✅ Store keys in environment variables
- ✅ Rotate keys periodically
- ❌ Never commit keys to version control
- ❌ Never expose keys in client-side code

See [API_KEY_SETUP.md](API_KEY_SETUP.md) for complete guide.

## Resources

- **Model:** [Wan-AI/Wan2.2-S2V-14B](https://huggingface.co/Wan-AI/Wan2.2-S2V-14B)
- **Paper:** [Wan-S2V: Audio-Driven Cinematic Video Generation](https://arxiv.org/abs/2508.18621)
- **Homepage:** [wan.video](https://wan.video/)
- **GitHub:** [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2)

## License

Apache 2.0 - See [LICENSE](LICENSE) for details

## Citation

```bibtex
@article{wan2025s2v,
   title={Wan-S2V:Audio-Driven Cinematic Video Generation},
   author={Xin Gao, Li Hu, Siqi Hu, et al.},
   journal={arXiv preprint arXiv:2508.18621},
   year={2025}
}
```

## Status

🚧 **Under Development** - Initial implementation in progress

## Contact

For questions or issues, please open a GitHub issue.
