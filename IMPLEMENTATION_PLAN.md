# Wan2.2 S2V-14B Modal Implementation Plan

## Executive Summary

**Model:** Wan2.2-S2V-14B (Speech/Audio-to-Video)
**Type:** Audio-driven cinematic video generation (14B parameters)
**Task:** Generate videos from audio + reference image + optional text prompt
**Output:** 480P or 720P video at 24fps
**Official Repo:** https://github.com/Wan-Video/Wan2.2
**HuggingFace:** https://huggingface.co/Wan-AI/Wan2.2-S2V-14B

## Repository Decision

### Recommendation: **CREATE A SEPARATE REPOSITORY**

#### Reasons:
1. **Different Model Architecture**
   - Z-Image: Text-to-Image (6B params, diffusion transformer)
   - Wan2.2-S2V: Audio-to-Video (14B params, MoE architecture)
   
2. **Different Dependencies**
   - Z-Image: Simple diffusers pipeline
   - Wan2.2: Complex multi-modal (audio, video, pose), requires flash_attn, custom code
   
3. **Massive Model Size**
   - Z-Image: ~33GB
   - Wan2.2-S2V: ~50-60GB (14B model + VAE + text encoder)
   
4. **Different Use Cases**
   - Z-Image: Quick image generation API
   - Wan2.2: Long-running video generation (minutes per video)
   
5. **Different GPU Requirements**
   - Z-Image: A100-40GB/80GB sufficient
   - Wan2.2: Minimum 80GB VRAM, ideally multi-GPU (8xA100)

### Suggested Repository Structure:
```
storystudio-zimage/          (existing - keep for image generation)
storystudio-wan2/             (new - for video generation)
```

---

## Technical Specifications

### Model Details
- **Model Size:** 14B parameters (MoE: 27B total, 14B active)
- **Model Files:** 49.1GB total from HuggingFace
  - Diffusion Model (4 shards):
    - `diffusion_pytorch_model-00001-of-00004.safetensors` (9.97 GB)
    - `diffusion_pytorch_model-00002-of-00004.safetensors` (9.89 GB)
    - `diffusion_pytorch_model-00003-of-00004.safetensors` (9.96 GB)
    - `diffusion_pytorch_model-00004-of-00004.safetensors` (2.77 GB)
    - `diffusion_pytorch_model.safetensors.index.json` (113 KB)
  - VAE: `Wan2.1_VAE.pth` (508 MB)
  - Text Encoder: `models_t5_umt5-xxl-enc-bf16.pth` (11.4 GB)
  - Audio Encoder: `wav2vec2-large-xlsr-53-english/` (folder)
  - Config files: `config.json`, `configuration.json`
  
### Requirements
- **Minimum GPU:** 1x A100-80GB (with model offloading)
- **Recommended GPU:** 4-8x A100-80GB (FSDP + Ulysses parallelism)
- **Memory:** 80GB+ VRAM per GPU
- **Storage:** ~60GB for model weights

### Input/Output
**Inputs:**
- Reference image (required)
- Audio file (.wav, .mp3) (required)
- Text prompt (optional)
- Pose video (optional - for pose-driven generation)

**Outputs:**
- Video resolution: 480P (640×480) or 720P (1280×720)
- Frame rate: 24fps
- Duration: Auto-adjusts to audio length
- Format: MP4

### Generation Time
| Configuration | Resolution | Duration | Time |
|---------------|-----------|----------|------|
| 1x A100-80GB | 720P | 5 sec | ~15-20 min |
| 4x A100-80GB | 720P | 5 sec | ~5-8 min |
| 8x A100-80GB | 720P | 5 sec | ~3-5 min |

---

## Dependencies

```python
# Core dependencies
torch >= 2.4.0
flash_attn >= 2.5.0  # Critical for Wan2.2
diffusers >= 0.30.0
transformers >= 4.40.0
accelerate >= 0.30.0

# Audio processing
librosa >= 0.10.0
soundfile >= 0.12.0
torchaudio >= 2.0.0
transformers >= 4.40.0  # For wav2vec2 audio encoder

# Video processing
opencv-python >= 4.8.0
imageio-ffmpeg >= 0.4.9
moviepy >= 1.0.3

# Model specific
safetensors >= 0.4.0
einops >= 0.7.0
omegaconf >= 2.3.0

# API
fastapi >= 0.110.0
pydantic >= 2.0.0
```

---

## Modal Deployment Architecture

### Option 1: Single-GPU (Budget)
```python
@app.cls(
    gpu="A100-80GB",
    timeout=1800,  # 30 minutes per request
    image=image,
    volumes={"/models": volume},
)
class Wan2S2VModel:
    # Model with CPU offloading
    pass
```

**Pros:** Lower cost (~$4/hour)
**Cons:** Slow generation (15-20 min per video)
**Best for:** Testing, low-volume usage

### Option 2: Multi-GPU (Production)
```python
@app.cls(
    gpu="A100-80GB:4",  # 4x A100
    timeout=900,  # 15 minutes per request
    image=image,
    volumes={"/models": volume},
)
class Wan2S2VModel:
    # FSDP + Ulysses parallelism
    pass
```

**Pros:** Fast generation (5-8 min per video)
**Cons:** Higher cost (~$16/hour)
**Best for:** Production, high-volume usage

### Option 3: Serverless with Auto-scaling
```python
@app.function(
    gpu="A100-80GB",
    timeout=1800,
    image=image,
    volumes={"/models": volume},
    scaledown_window=600,  # 10 min keep-alive
)
def generate_video(...):
    # On-demand generation
    pass
```

**Pros:** Pay per use, auto-scales
**Cons:** Cold start time (~2-3 min)
**Best for:** Sporadic usage

---

## Cost Analysis

### Per Video Cost (720P, 5 seconds)

| Setup | Time | GPU Cost | Total Cost |
|-------|------|----------|------------|
| 1x A100-80GB | 15 min | $4.00/hr | **$1.00** |
| 4x A100-80GB | 5 min | $16.00/hr | **$1.33** |
| 8x A100-80GB | 3 min | $32.00/hr | **$1.60** |

### Monthly Estimates

| Usage | Videos/Month | Cost (1 GPU) | Cost (4 GPU) |
|-------|--------------|--------------|--------------|
| Light (10/month) | 10 | $10 | $13 |
| Medium (50/month) | 50 | $50 | $67 |
| Heavy (200/month) | 200 | $200 | $267 |

**Note:** 4-GPU setup is more cost-effective for production despite higher hourly rate due to faster generation.

---

## Implementation Steps

### Phase 1: Setup New Repository
```bash
# Create new repo
mkdir storystudio-wan2
cd storystudio-wan2
git init

# Set up Modal
modal setup
```

### Phase 2: Model Download Strategy

**Official Download Command:**
```bash
# Using huggingface-cli (recommended)
pip install "huggingface_hub[cli]"
huggingface-cli download Wan-AI/Wan2.2-S2V-14B --local-dir ./Wan2.2-S2V-14B

# OR using modelscope-cli
pip install modelscope
modelscope download Wan-AI/Wan2.2-S2V-14B --local_dir ./Wan2.2-S2V-14B
```

**For Modal:**
```python
# Use Modal volumes for caching
volume = modal.Volume.from_name("wan2-models", create_if_missing=True)

@app.function(timeout=3600, image=image)
def download_models():
    """Download models to Modal volume"""
    import subprocess
    subprocess.run([
        "huggingface-cli", "download", 
        "Wan-AI/Wan2.2-S2V-14B",
        "--local-dir", "/models/Wan2.2-S2V-14B"
    ])
    print("Model downloaded successfully!")
```

### Phase 3: Core Implementation

**Official Single-GPU Command:**
```bash
python generate.py \
  --task s2v-14B \
  --size 1024*704 \
  --ckpt_dir ./Wan2.2-S2V-14B/ \
  --offload_model True \
  --convert_model_dtype \
  --prompt "Summer beach vacation style, a white cat wearing sunglasses sits on a surfboard." \
  --image "examples/i2v_input.JPG" \
  --audio "examples/talk.wav"
# Requires 80GB VRAM minimum
```

**Official Multi-GPU Command (8 GPUs):**
```bash
torchrun --nproc_per_node=8 generate.py \
  --task s2v-14B \
  --size 1024*704 \
  --ckpt_dir ./Wan2.2-S2V-14B/ \
  --dit_fsdp \
  --t5_fsdp \
  --ulysses_size 8 \
  --prompt "Summer beach vacation style, a white cat wearing sunglasses sits on a surfboard." \
  --image "examples/i2v_input.JPG" \
  --audio "examples/talk.wav"
```

**Modal Wrapper:**
```python
class Wan2S2VModel:
    @modal.enter()
    def load_model(self):
        # Clone official repo
        # Load models from /models volume
        # Configure FSDP if multi-GPU
        # Load audio processor (wav2vec2)
        pass
    
    @modal.method()
    def generate(self, image, audio, prompt, **kwargs):
        # Use official generate.py logic
        # Process audio with wav2vec2
        # Generate video with MoE architecture
        # Return video bytes
        pass
```

### Phase 4: API Endpoint
```python
@app.function()
@modal.asgi_app()
def fastapi_app():
    app = FastAPI()
    
    @app.post("/generate-video")
    async def generate_video(
        image: UploadFile,
        audio: UploadFile,
        prompt: str = None
    ):
        # Process and generate
        pass
```

---

## File Structure

```
storystudio-wan2/
├── wan2_modal.py           # Main Modal deployment
├── wan2_generate.py        # Generation logic
├── wan2_audio.py           # Audio processing
├── wan2_model.py           # Model wrapper
├── requirements.txt
├── README.md
├── API_KEY_SETUP.md
├── test_wan2.py           # Test scripts
├── examples/
│   ├── generate_basic.py
│   ├── generate_with_pose.py
│   └── batch_generate.py
└── docs/
    ├── DEPLOYMENT.md
    ├── USAGE.md
    └── COSTS.md
```

---

## Key Challenges

### 1. Model Size (60GB)
**Solution:** Use Modal volumes for persistent storage, download once

### 2. Long Generation Time (15+ min)
**Solution:** 
- Use background tasks
- Implement job queue system
- WebSocket for progress updates

### 3. High GPU Cost
**Solution:**
- Multi-GPU for production
- Batch processing
- Smart scaling policies

### 4. Complex Dependencies
**Solution:**
- Custom Docker image
- Pre-compiled flash_attn
- Tested dependency versions

### 5. Audio Processing
**Solution:**
- Use librosa for audio features
- Support multiple audio formats
- Auto-detect audio length

---

## API Design

### REST API
```python
POST /generate-video
Headers:
  X-API-Key: your_api_key
  Content-Type: multipart/form-data

Body:
  image: file (JPG/PNG)
  audio: file (WAV/MP3)
  prompt: string (optional)
  resolution: "480p" | "720p"
  num_clips: int (optional)

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "estimated_time": 900  // seconds
}

GET /status/{job_id}
Response:
{
  "job_id": "uuid",
  "status": "completed",
  "video_url": "https://...",
  "duration": 5.0,
  "resolution": "720p"
}
```

---

## Comparison: Same Repo vs Separate

| Aspect | Same Repo | Separate Repo |
|--------|-----------|---------------|
| Code Organization | ❌ Mixed concerns | ✅ Clear separation |
| Dependencies | ❌ Conflicts | ✅ Independent |
| Deployment | ❌ Coupled | ✅ Independent |
| Scaling | ❌ Limited | ✅ Flexible |
| Cost Optimization | ❌ Shared resources | ✅ Optimized per model |
| Maintenance | ❌ Complex | ✅ Simple |
| Team Collaboration | ❌ Merge conflicts | ✅ Parallel work |

---

## Recommendation Summary

### ✅ CREATE SEPARATE REPOSITORY: `storystudio-wan2`

**Key Benefits:**
1. Clean separation of concerns
2. Independent scaling and deployment
3. Optimized for video generation workloads
4. No dependency conflicts
5. Easier to maintain and update
6. Better cost optimization per use case

**Next Steps:**
1. Create new GitHub repo: `storystudio-wan2`
2. Set up Modal project
3. Download and cache models (one-time)
4. Implement core generation pipeline
5. Add API endpoints
6. Test and optimize
7. Deploy to production

---

## Timeline Estimate

| Phase | Tasks | Duration |
|-------|-------|----------|
| **Phase 1: Setup** | Repo, Modal, dependencies | 1-2 days |
| **Phase 2: Model Integration** | Download, load, test | 2-3 days |
| **Phase 3: Core Implementation** | Generation pipeline | 3-4 days |
| **Phase 4: API Development** | FastAPI endpoints | 2-3 days |
| **Phase 5: Testing** | Integration tests | 2-3 days |
| **Phase 6: Optimization** | Performance tuning | 2-3 days |
| **Phase 7: Documentation** | Guides, examples | 1-2 days |

**Total:** 13-20 days for full implementation

---

## Conclusion

Wan2.2 S2V-14B is a significantly more complex model than Z-Image and requires:
- **Separate repository** for clean architecture
- **Higher GPU resources** (80GB+ VRAM)
- **Longer generation times** (minutes vs seconds)
- **More complex infrastructure** (audio processing, video encoding)

**Recommendation:** Create `storystudio-wan2` as a new, dedicated repository for video generation.

Would you like me to proceed with creating the new repository and implementation?
