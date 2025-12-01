"""
Wan2.2 S2V-14B Model Deployment on Modal
Audio-driven cinematic video generation

Official Repository: https://github.com/Wan-Video/Wan2.2
HuggingFace: https://huggingface.co/Wan-AI/Wan2.2-S2V-14B
Paper: https://arxiv.org/abs/2508.18621
"""

import modal
import os
import io
from pathlib import Path

# Create Modal app
app = modal.App("wan2-s2v")

# Define the image with all required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libsndfile1", "wget")
    .pip_install(
        "torch>=2.4.0",
        "diffusers>=0.30.0",
        "transformers>=4.40.0",
        "accelerate>=0.30.0",
        "safetensors>=0.4.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.0",
        "torchaudio>=2.0.0",
        "opencv-python>=4.8.0",
        "imageio-ffmpeg>=0.4.9",
        "einops>=0.7.0",
        "omegaconf>=2.3.0",
        "huggingface-hub",
        "fastapi",
        "pydantic",
        "python-multipart",
        "pillow",
        "numpy",
    )
    # Clone the official Wan2.2 repository
    .run_commands(
        "cd /root && git clone https://github.com/Wan-Video/Wan2.2.git",
        "cd /root/Wan2.2 && pip install -e .",
    )
)

# Model configuration
MODEL_ID = "Wan-AI/Wan2.2-S2V-14B"
MODEL_CACHE_DIR = "/cache/models"
GITHUB_REPO = "https://github.com/Wan-Video/Wan2.2.git"

# Model files (49.1 GB total)
MODEL_FILES = {
    "diffusion_model_shards": [
        "diffusion_pytorch_model-00001-of-00004.safetensors",  # 9.97 GB
        "diffusion_pytorch_model-00002-of-00004.safetensors",  # 9.89 GB
        "diffusion_pytorch_model-00003-of-00004.safetensors",  # 9.96 GB
        "diffusion_pytorch_model-00004-of-00004.safetensors",  # 2.77 GB
    ],
    "diffusion_index": "diffusion_pytorch_model.safetensors.index.json",
    "vae": "Wan2.1_VAE.pth",  # 508 MB
    "text_encoder": "models_t5_umt5-xxl-enc-bf16.pth",  # 11.4 GB
    "audio_encoder_dir": "wav2vec2-large-xlsr-53-english",  # Audio encoder folder
    "config": ["config.json", "configuration.json"],
}

# Volume for model caching
volume = modal.Volume.from_name("wan2-models", create_if_missing=True)


@app.cls(
    image=image,
    gpu="A100-80GB",  # Minimum for single-GPU deployment
    timeout=1800,  # 30 minutes for video generation
    volumes={MODEL_CACHE_DIR: volume},
    scaledown_window=600,  # Keep warm for 10 minutes
)
class Wan2S2VModel:
    """Wan2.2 S2V Model Class for Modal deployment"""

    @modal.enter()
    def load_model(self):
        """Load the Wan2.2 S2V model on container startup"""
        import sys
        import subprocess
        from huggingface_hub import snapshot_download
        
        print("=" * 70)
        print("Loading Wan2.2-S2V-14B Model")
        print("=" * 70)
        
        # Add Wan2.2 repo to Python path
        sys.path.insert(0, "/root/Wan2.2")
        
        # Step 1: Download model weights from HuggingFace (if not cached)
        print("\n[1/3] Checking model cache...")
        model_dir = f"{MODEL_CACHE_DIR}/{MODEL_ID}"
        
        if not Path(model_dir).exists():
            print(f"Downloading model from HuggingFace: {MODEL_ID}")
            print("This is a one-time download (~49GB). Please wait...")
            snapshot_download(
                repo_id=MODEL_ID,
                local_dir=model_dir,
                cache_dir=MODEL_CACHE_DIR,
            )
            volume.commit()  # Save to persistent storage
            print("✅ Model downloaded and cached")
        else:
            print(f"✅ Model found in cache: {model_dir}")
        
        # Step 2: Initialize model components
        print("\n[2/3] Loading model components...")
        self.model_dir = model_dir
        self.ckpt_dir = model_dir
        
        # Import Wan2.2 modules
    @modal.method()
    def generate(
        self,
        image_bytes: bytes,
        audio_bytes: bytes,
        prompt: str = "",
        resolution: str = "720p",
        num_clips: int = None,
        pose_video_bytes: bytes = None,
    ) -> bytes:
        """
        Generate a video from audio and reference image
        
        Official command reference:
        python generate.py --task s2v-14B --size 1024*704 \
            --ckpt_dir ./Wan2.2-S2V-14B/ --offload_model True \
            --convert_model_dtype --prompt "..." \
            --image "input.jpg" --audio "audio.wav"
        
        Args:
            image_bytes: Reference image as bytes (JPG/PNG)
            audio_bytes: Audio file as bytes (WAV/MP3)
            prompt: Text description (optional)
            resolution: "480p" (640x480) or "720p" (1024x704)
            num_clips: Number of clips (auto-adjusts to audio length if None)
            pose_video_bytes: Optional pose video for pose-driven generation
        
        Returns:
            Video as bytes (MP4 format, 24fps)
        """
        import tempfile
        import subprocess
        import sys
        from pathlib import Path
        
        print("=" * 70)
        print("🎬 Starting Wan2.2-S2V Video Generation")
        print("=" * 70)
        print(f"Resolution: {resolution}")
        print(f"Prompt: {prompt}")
        print(f"Has pose video: {pose_video_bytes is not None}")
        print(f"Num clips: {num_clips if num_clips else 'auto (based on audio)'}")
        
        # Determine size based on resolution
        size_map = {
            "480p": "640*480",
            "720p": "1024*704",
        }
        size = size_map.get(resolution, "1024*704")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Save input files
            print("\n[1/4] Saving input files...")
            image_path = tmpdir_path / "input_image.jpg"
            audio_path = tmpdir_path / "input_audio.wav"
            output_path = tmpdir_path / "output_video.mp4"
            
            image_path.write_bytes(image_bytes)
            audio_path.write_bytes(audio_bytes)
            print(f"✅ Image saved: {image_path}")
            print(f"✅ Audio saved: {audio_path}")
            
            if pose_video_bytes:
                pose_path = tmpdir_path / "pose_video.mp4"
                pose_path.write_bytes(pose_video_bytes)
                print(f"✅ Pose video saved: {pose_path}")
            
            # Build command
            print("\n[2/4] Preparing generation command...")
            cmd = [
                "python", "/root/Wan2.2/generate.py",
                "--task", "s2v-14B",
                "--size", size,
                "--ckpt_dir", self.ckpt_dir,
                "--offload_model", "True",
                "--convert_model_dtype",
                "--image", str(image_path),
                "--audio", str(audio_path),
                "--output", str(output_path),
            ]
            
            if prompt:
                cmd.extend(["--prompt", prompt])
            
            if num_clips:
                cmd.extend(["--num_clip", str(num_clips)])
            
            if pose_video_bytes:
                cmd.extend(["--pose_video", str(pose_path)])
            
            print(f"Command: {' '.join(cmd)}")
            
            # Run generation
            print("\n[3/4] Generating video (this may take 15-20 minutes)...")
            print("Please wait while the model processes your request...")
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd="/root/Wan2.2",
                    capture_output=True,
                    text=True,
                    timeout=1800,  # 30 minute timeout
                )
                
                if result.returncode != 0:
                    print(f"❌ Generation failed with code {result.returncode}")
                    print(f"STDOUT: {result.stdout}")
                    print(f"STDERR: {result.stderr}")
                    raise RuntimeError(f"Video generation failed: {result.stderr}")
                
                print("✅ Video generation complete!")
                
            except subprocess.TimeoutExpired:
                raise RuntimeError("Video generation timed out after 30 minutes")
            
            # Read generated video
            print("\n[4/4] Reading generated video...")
            if not output_path.exists():
                raise FileNotFoundError(f"Output video not found at {output_path}")
            
            video_bytes = output_path.read_bytes()
            video_size_mb = len(video_bytes) / (1024 * 1024)
            
            print(f"✅ Video size: {video_size_mb:.2f} MB")
            print("=" * 70)
            print("🎉 Video generation successful!")
            print("=" * 70)
            
            return video_bytes
        # Resize according to resolution (maintains aspect ratio)
        # Size parameter format: 1024*704 (area, not exact dimensions)
        
        # Step 4: Generate video using MoE architecture
        # - Use high-noise expert for early denoising steps
        # - Switch to low-noise expert for refinement
        # - Synchronize with audio features
        # - Optional: Apply pose guidance if pose_video provided
        
        # Step 5: Encode to MP4 at 24fps
        # Video length auto-adjusts to audio duration unless num_clips specified
        
        # Step 6: Return video bytes
        
        raise NotImplementedError("Video generation not yet implemented")


# Web endpoint for REST API access
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("wan2-api-keys")],  # Create this secret in Modal dashboard
)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI, HTTPException, Header, Depends, UploadFile, File, Form
    from pydantic import BaseModel
    import base64
    import os
    
    web_app = FastAPI(title="Wan2.2 S2V API", version="0.1.0")
    
    # API Key validation
    def verify_api_key(x_api_key: str = Header(None)):
        """Verify API key from request header"""
        # Get valid API keys from Modal Secret (comma-separated for multiple keys)
        valid_api_keys_str = os.environ.get("WAN2_API_KEYS", "")
        
        # If no keys configured, allow access (for testing)
        if not valid_api_keys_str:
            print("⚠️  Warning: No API keys configured. Access is unrestricted!")
            return True
        
        # Parse multiple API keys (comma-separated)
        valid_api_keys = [key.strip() for key in valid_api_keys_str.split(",")]
        
        # Check if API key is provided
        if x_api_key is None:
            raise HTTPException(
                status_code=401,
                detail="Missing API key. Include 'X-API-Key' header with your API key.",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Verify API key
        if x_api_key not in valid_api_keys:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key. Please check your credentials.",
            )
        
        return True
    
    @web_app.get("/")
    def root():
        """Health check endpoint"""
        api_keys_configured = bool(os.environ.get("WAN2_API_KEYS"))
        return {
            "status": "online",
            "model": "Wan2.2-S2V-14B",
            "version": "0.1.0",
            "endpoints": {
                "POST /generate-video": "Generate video from audio and image",
                "GET /health": "Health check",
            },
            "authentication": {
                "required": api_keys_configured,
                "method": "API Key in X-API-Key header",
                "status": "enabled" if api_keys_configured else "disabled (testing mode)"
            },
            "supported_formats": {
                "image": ["JPG", "PNG"],
                "audio": ["WAV", "MP3"],
                "output": "MP4 (24fps)"
            },
            "resolutions": ["480p", "720p"],
            "note": "Implementation in progress"
        }
    
    @web_app.get("/health")
    def health():
        """Simple health check endpoint"""
        return {"status": "healthy", "model": "Wan2.2-S2V-14B"}
    
    @web_app.post("/generate-video")
    async def generate_video(
        image: UploadFile = File(...),
        audio: UploadFile = File(...),
        prompt: str = Form(""),
        resolution: str = Form("720p"),
        num_clips: int = Form(None),
        pose_video: UploadFile = File(None),
        authenticated: bool = Depends(verify_api_key)
    ):
        """
        Generate video from audio and image
        
        Based on official Wan2.2-S2V-14B model
        Supports 480P (640x480) and 720P (1024x704) at 24fps
        
        Parameters:
        - image: Reference image file (JPG/PNG)
        - audio: Audio file (WAV/MP3)
        - prompt: Text description (optional)
        - resolution: "480p" or "720p"
        - num_clips: Number of video clips (optional, auto-adjusts to audio length)
        - pose_video: Optional pose video for pose-driven generation (MP4)
        """
        try:
            # Read uploaded files
            image_bytes = await image.read()
            audio_bytes = await audio.read()
            pose_video_bytes = await pose_video.read() if pose_video else None
            
            # Generate video
            model = Wan2S2VModel()
            video_bytes = model.generate.remote(
                image_bytes=image_bytes,
                audio_bytes=audio_bytes,
                prompt=prompt,
                resolution=resolution,
                num_clips=num_clips,
                pose_video_bytes=pose_video_bytes,
            )
            
            # Encode as base64 for JSON response
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
            
            return {
                "success": True,
                "video": video_base64,
                "format": "mp4",
                "resolution": resolution,
            }
        except NotImplementedError as e:
            raise HTTPException(
                status_code=501,
                detail="Video generation not yet implemented. Coming soon!"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return web_app


# CLI function for testing
@app.local_entrypoint()
def main(
    image_path: str,
    audio_path: str,
    output_path: str = "output.mp4",
    prompt: str = "",
    resolution: str = "720p",
):
    """
    CLI entry point for testing the model locally
    
    Usage:
        modal run wan2_modal.py \
            --image-path reference.jpg \
            --audio-path audio.wav \
            --prompt "A person talking" \
            --resolution 720p
    """
    print(f"Generating video from:")
    print(f"  Image: {image_path}")
    print(f"  Audio: {audio_path}")
    print(f"  Prompt: {prompt}")
    print(f"  Resolution: {resolution}")
    
    # Read input files
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    
    # Generate video
    model = Wan2S2VModel()
    video_bytes = model.generate.remote(
        image_bytes=image_bytes,
        audio_bytes=audio_bytes,
        prompt=prompt,
        resolution=resolution,
    )
    
    # Save the video
    with open(output_path, "wb") as f:
        f.write(video_bytes)
    
    print(f"Video saved to {output_path}")
