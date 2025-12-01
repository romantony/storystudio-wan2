# Test Files and Examples

This directory contains example files and instructions for testing the Wan2.2 S2V API.

## 📁 Required Test Files

To test video generation, you need:

### 1. Reference Image (JPG/PNG)
- A photo or image of a person, character, or object
- Recommended: Clear, well-lit portrait photo
- Resolution: 512x512 or higher
- Format: JPG or PNG

**Where to get:**
- Use your own photo
- Free stock photos: [Unsplash](https://unsplash.com/), [Pexels](https://pexels.com/)
- AI-generated: [Midjourney](https://midjourney.com/), [DALL-E](https://openai.com/dall-e)

### 2. Audio File (WAV/MP3)
- Speech, singing, or any audio you want to sync
- Duration: 2-10 seconds recommended for testing
- Format: WAV or MP3
- Sample rate: 16kHz or 44.1kHz

**Where to get:**
- Record your own voice
- Text-to-speech: [ElevenLabs](https://elevenlabs.io/), [Google TTS](https://cloud.google.com/text-to-speech)
- Free audio: [Freesound](https://freesound.org/)

## 🎬 Example Test Cases

### Test Case 1: Simple Portrait + Speech
```bash
python test_client.py \
  --url https://your-app.modal.run \
  --api-key your-key \
  --image examples/portrait.jpg \
  --audio examples/speech.wav \
  --prompt "A person talking about technology" \
  --resolution 720p
```

**Expected:**
- Video with person's face animated
- Lip sync with audio
- Duration: matches audio length
- Output: `output.mp4`

### Test Case 2: Character Portrait + Singing
```bash
python test_client.py \
  --url https://your-app.modal.run \
  --api-key your-key \
  --image examples/character.png \
  --audio examples/singing.mp3 \
  --prompt "A character singing a song" \
  --resolution 720p \
  --output singing_output.mp4
```

### Test Case 3: Quick Test (480p for faster generation)
```bash
python test_client.py \
  --url https://your-app.modal.run \
  --api-key your-key \
  --image examples/test.jpg \
  --audio examples/test_audio.wav \
  --resolution 480p
```

**Note:** 480p generates faster (~10 min vs 15-20 min for 720p)

## 🧪 Creating Test Files Quickly

### Option 1: Download Sample Files

```bash
# Create examples directory
mkdir -p examples

# Download sample image (replace with actual URL)
curl -o examples/portrait.jpg "URL_TO_SAMPLE_IMAGE"

# Download sample audio
curl -o examples/speech.wav "URL_TO_SAMPLE_AUDIO"
```

### Option 2: Use Your Own Files

```bash
# Create examples directory
mkdir -p examples

# Copy your files
cp /path/to/your/photo.jpg examples/portrait.jpg
cp /path/to/your/audio.wav examples/speech.wav
```

### Option 3: Generate with Python

```python
# generate_test_audio.py
from gtts import gTTS
import os

text = "Hello, this is a test of the Wan2.2 speech to video model."
tts = gTTS(text=text, lang='en')
tts.save("examples/test_audio.mp3")
print("Test audio generated: examples/test_audio.mp3")
```

## 📊 Expected Results

### First Request (Includes Model Download)
- **Time:** ~30-45 minutes
- **Breakdown:**
  - Model download: ~10-30 min (49GB, one-time)
  - Video generation: ~15-20 min (720p)
- **Cost:** ~$2-3 (one-time setup)

### Subsequent Requests
- **Time:** ~15-20 minutes (720p) or ~10 minutes (480p)
- **Cost:** ~$1.00-1.33 per video (720p)

### Output Video
- **Format:** MP4
- **Resolution:** 480p (640×480) or 720p (1280×720)
- **Frame Rate:** 24fps
- **Duration:** Matches audio input
- **Features:** Lip sync, facial animation, audio-driven motion

## 🔍 Verifying Output

### Check Video File
```bash
# Check file exists
ls -lh output.mp4

# Get video info (requires ffmpeg)
ffprobe output.mp4

# Play video
# Windows: start output.mp4
# Mac: open output.mp4
# Linux: xdg-open output.mp4
```

### Quality Checklist
- ✅ Video plays smoothly
- ✅ Audio is synchronized
- ✅ Lip movements match speech
- ✅ Facial expressions are natural
- ✅ No artifacts or glitches
- ✅ Duration matches audio

## 🎨 Tips for Best Results

### Image Selection
- ✅ Use clear, well-lit photos
- ✅ Face should be clearly visible
- ✅ Neutral or front-facing pose works best
- ❌ Avoid blurry or low-resolution images
- ❌ Avoid extreme angles or occlusions

### Audio Quality
- ✅ Clear speech without background noise
- ✅ Normal speaking pace
- ✅ Consistent volume
- ❌ Avoid heavily distorted audio
- ❌ Avoid very fast or very slow speech

### Prompts
- ✅ Describe the desired mood/style
- ✅ Mention specific actions if needed
- ✅ Keep it concise (1-2 sentences)
- Examples:
  - "A person talking confidently"
  - "A character singing emotionally"
  - "Professional presentation style"
  - "Casual conversation with gestures"

## 📝 Example Files Structure

```
examples/
├── README.md                 # This file
├── portrait.jpg              # Sample portrait photo
├── speech.wav               # Sample speech audio
├── singing.mp3              # Sample singing audio
├── character.png            # Sample character image
└── test_results/            # Output directory
    ├── test1_output.mp4
    ├── test2_output.mp4
    └── ...
```

## 🚨 Troubleshooting Tests

### Issue: "File not found"
**Solution:** Check file paths are correct
```bash
ls -la examples/
```

### Issue: "Invalid image format"
**Solution:** Convert to JPG
```bash
convert your_image.png examples/portrait.jpg
```

### Issue: "Audio format not supported"
**Solution:** Convert to WAV
```bash
ffmpeg -i input.mp3 -ar 16000 examples/audio.wav
```

### Issue: "Generation taking too long"
**Solution:** 
- First generation includes model download (30-45 min total)
- Subsequent generations: 15-20 min for 720p
- Use 480p for faster results (~10 min)

### Issue: "Out of memory"
**Solution:** Model requires A100-80GB minimum. Check GPU in `wan2_modal.py`

## 📚 Additional Resources

- [DEPLOYMENT.md](../DEPLOYMENT.md) - Full deployment guide
- [API_KEY_SETUP.md](../API_KEY_SETUP.md) - Security setup
- [test_client.py](../test_client.py) - Test client script
- [Official Wan2.2 Repo](https://github.com/Wan-Video/Wan2.2)

---

**Ready to test? Start with Option 2 or 3 above to create your test files!**
