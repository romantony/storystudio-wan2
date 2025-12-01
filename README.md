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

## Quick Start

### Prerequisites
```bash
pip install modal
modal setup
```

### Deploy to Modal
```bash
modal deploy wan2_modal.py
```

### Generate Video
```python
import modal

Wan2Model = modal.Cls.lookup("wan2-s2v", "Wan2S2VModel")

with Wan2Model() as model:
    video_bytes = model.generate.remote(
        image_path="reference.jpg",
        audio_path="audio.wav",
        prompt="A person talking",
        resolution="720p"
    )
    
    with open("output.mp4", "wb") as f:
        f.write(video_bytes)
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

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Technical details
- [API Documentation](API.md) - API reference
- [Deployment Guide](DEPLOYMENT.md) - Setup instructions
- [Cost Analysis](COSTS.md) - Pricing details

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
