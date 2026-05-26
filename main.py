import os
import json
import time
import random
import requests
import subprocess
import jwt
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import base64

# ─── CONFIG ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
PEXELS_API_KEY     = os.environ["PEXELS_API_KEY"]
KLING_ACCESS_KEY   = os.environ["KLING_ACCESS_KEY"]
KLING_SECRET_KEY   = os.environ["KLING_SECRET_KEY"]

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── TOPICS ────────────────────────────────────────────────────────────────────
TOPICS = [
    "Alexander the Great's final days and mysterious death",
    "Genghis Khan: The rise of the most feared conqueror in history",
    "Hannibal Barca's impossible crossing of the Alps",
    "Attila the Hun: Why Rome trembled at his name",
    "Saladin and the recapture of Jerusalem",
    "Tamerlane: The lame conqueror who drowned cities in blood",
    "Spartacus: The slave who almost brought Rome to its knees",
    "Richard the Lionheart: The king who hated his own kingdom",
    "Suleiman the Magnificent: The emperor who rewrote Ottoman history",
    "Julius Caesar's assassination: The betrayal that changed Rome forever",
    "Napoleon Bonaparte's 100 days: The greatest comeback in history",
    "Nero: Monster or misunderstood emperor of Rome",
    "Ivan the Terrible: Russia's most brutal and brilliant tsar",
    "Peter the Great: How a giant tsar transformed a backward empire",
    "Akbar the Great: The Mughal emperor who united a continent",
    "Charlemagne: The barbarian king who became father of Europe",
    "Mehmed II: The 21-year-old sultan who ended the Byzantine Empire",
    "Frederick the Great: The philosopher king who never lost a war",
    "Cyrus the Great: How a shepherd's son built the world's first empire",
    "Ramesses II: The pharaoh who rewrote his own defeat as victory",
    "Ashoka: The warrior king who chose peace after a river of blood",
    "Constantine the Great: The vision that changed the Roman Empire forever",
    "Cleopatra: The truth behind history's most misunderstood queen",
    "Catherine the Great: How a German princess became Russia's greatest ruler",
    "Joan of Arc: The teenager who led France's army and died for it",
    "The Battle of Thermopylae: 300 Spartans vs a million Persians",
    "The fall of Constantinople: The day the Roman Empire finally died",
    "The Black Death: How the plague wiped out half of Europe",
    "Vlad the Impaler: The real Dracula and his reign of terror",
    "William the Conqueror: The bastard duke who conquered England in a day",
    "Boudicca: The warrior queen who nearly drove Rome from Britain",
    "The Mongol invasion: Why the most advanced civilizations fell in days",
    "Wu Zetian: China's only female emperor and her path to power",
    "Pompeii: The city frozen in time by a mountain of fire",
    "Spartacus: The slave rebellion that shook the Roman Empire",
]

# ─── STEP 1: GENERATE SCRIPT WITH CLAUDE ──────────────────────────────────────
def generate_script():
    print("📜 Generating cinematic script with Claude...")
    topic = random.choice(TOPICS)

    prompt = f"""You are a world-class YouTube scriptwriter for epic historical documentaries.
Your scripts go VIRAL because they combine cinematic storytelling, real shocking facts, emotional hooks, and perfect pacing.

Write a FULL YouTube script about: "{topic}"

Return ONLY a JSON object with these exact fields:
{{
  "title": "YouTube title under 60 chars, dramatic and clickbait but accurate",
  "description": "YouTube description 200 words SEO optimized",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12", "tag13", "tag14", "tag15", "tag16", "tag17", "tag18", "tag19", "tag20"],
  "thumbnail_text": "5-7 words MAX shocking dramatic text for thumbnail",
  "thumbnail_subtext": "2-4 words supporting text",
  "scenes": [
    {{
      "id": 1,
      "title": "HOOK",
      "narration": "90 seconds narration. Start with the most shocking fact. Drop viewer into action immediately. Present tense for drama. No introduction.",
      "image_prompt": "Cinematic oil painting, dramatic lighting, [specific historical scene], epic composition, dark dramatic atmosphere, 16:9"
    }},
    {{
      "id": 2,
      "title": "THE WORLD BEFORE",
      "narration": "90 seconds. Set the stage. Paint the world they lived in.",
      "image_prompt": "..."
    }},
    {{
      "id": 3,
      "title": "THE RISE",
      "narration": "120 seconds. The turning point. Build tension.",
      "image_prompt": "..."
    }},
    {{
      "id": 4,
      "title": "THE CONFLICT",
      "narration": "120 seconds. Great battle or betrayal. Maximum drama.",
      "image_prompt": "..."
    }},
    {{
      "id": 5,
      "title": "THE CLIMAX",
      "narration": "120 seconds. Peak moment. Decision that changed history.",
      "image_prompt": "..."
    }},
    {{
      "id": 6,
      "title": "THE LEGACY",
      "narration": "90 seconds. Ripple effects through history. End with thought-provoking question.",
      "image_prompt": "..."
    }},
    {{
      "id": 7,
      "title": "OUTRO",
      "narration": "30 seconds. Powerful closing. Subscribe call to action.",
      "image_prompt": "..."
    }}
  ]
}}

RULES:
- Total narration 8-12 minutes when read aloud (1200-1800 words total)
- Every scene has a cliffhanger to next scene
- Use vivid sensory details, real dates and facts
- Return ONLY the JSON, no other text"""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": "claude-opus-4-5",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    response.raise_for_status()

    text = response.json()["content"][0]["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    script = json.loads(text)
    print(f"✅ Script: {script['title']}")
    return script

# ─── STEP 2: GENERATE IMAGE WITH GEMINI/PEXELS ────────────────────────────────
def generate_image(prompt, filename):
    print(f"🎨 Generating image: {Path(filename).name}")

    # Try Gemini Imagen first
    try:
        from google import genai as genai2
        from google.genai import types

        client = genai2.Client(api_key=os.environ["GEMINI_API_KEY"])
        enhanced = f"{prompt}, cinematic masterpiece, dramatic shadows, epic historical art, ultra detailed"

        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=enhanced,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="block_only_high",
            )
        )
        img_bytes = response.generated_images[0].image.image_bytes
        with open(filename, 'wb') as f:
            f.write(img_bytes)
        print(f"   ✅ Imagen generated")
        return True
    except Exception as e:
        print(f"   ⚠️ Imagen failed: {e}")

    # Fallback: Pexels
    try:
        keywords = prompt.split(',')[0][:50]
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": keywords, "per_page": 5, "orientation": "landscape"}
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        photos = resp.json().get("photos", [])
        if photos:
            img_url = photos[0]["src"]["large2x"]
            img_resp = requests.get(img_url)
            with open(filename, 'wb') as f:
                f.write(img_resp.content)
            print(f"   ✅ Pexels fallback used")
            return True
    except Exception as e:
        print(f"   ❌ Pexels failed: {e}")

    return False

# ─── STEP 3: KLING AI - IMAGE TO VIDEO ────────────────────────────────────────
def get_kling_token():
    """Generate JWT token for Kling API"""
    headers = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": KLING_ACCESS_KEY,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, KLING_SECRET_KEY, algorithm="HS256", headers=headers)
    return token

def image_to_video_kling(image_path, scene_prompt, output_path, scene_num):
    """Convert image to cinematic video using Kling AI"""
    print(f"🎬 Kling AI: Converting image to video (scene {scene_num})...")

    token = get_kling_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Read and encode image
    with open(image_path, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')

    # Cinematic motion prompts for historical scenes
    motion_prompts = [
        "slow cinematic camera push forward, dramatic atmosphere, dust particles floating",
        "gentle camera pan right, epic scale revealed, atmospheric lighting",
        "slow zoom out revealing grand scene, majestic and dramatic",
        "camera slowly rises up, revealing epic landscape, cinematic feel",
        "slow dolly shot moving through scene, atmospheric depth",
        "subtle camera drift left, dramatic lighting shifts, epic mood",
        "slow pull back reveal, dramatic scale, cinematic masterpiece",
    ]
    motion = motion_prompts[scene_num % len(motion_prompts)]

    # Create video generation task
    payload = {
        "model_name": "kling-v2-master",
        "image": img_data,
        "prompt": f"{motion}. {scene_prompt[:200]}",
        "negative_prompt": "blurry, shaky, fast motion, modern elements, text, watermark",
        "cfg_scale": 0.5,
        "mode": "pro",
        "duration": "5",
        "aspect_ratio": "16:9"
    }

    resp = requests.post(
        "https://api.klingai.com/v1/videos/image2video",
        headers=headers,
        json=payload
    )

    if resp.status_code != 200:
        print(f"   ❌ Kling API error: {resp.status_code} - {resp.text}")
        return False

    task_data = resp.json()
    task_id = task_data.get("data", {}).get("task_id")

    if not task_id:
        print(f"   ❌ No task_id returned: {task_data}")
        return False

    print(f"   ⏳ Task created: {task_id}, waiting for video...")

    # Poll for completion
    max_wait = 300  # 5 minutes
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(15)
        elapsed += 15

        token = get_kling_token()  # Refresh token
        headers["Authorization"] = f"Bearer {token}"

        status_resp = requests.get(
            f"https://api.klingai.com/v1/videos/image2video/{task_id}",
            headers=headers
        )

        if status_resp.status_code != 200:
            print(f"   ⚠️ Status check failed: {status_resp.status_code}")
            continue

        status_data = status_resp.json()
        task_status = status_data.get("data", {}).get("task_status", "")
        print(f"   Status: {task_status} ({elapsed}s)")

        if task_status == "succeed":
            # Download video
            works = status_data.get("data", {}).get("task_result", {}).get("videos", [])
            if works:
                video_url = works[0].get("url")
                video_resp = requests.get(video_url)
                with open(output_path, 'wb') as f:
                    f.write(video_resp.content)
                print(f"   ✅ Kling video downloaded: {Path(output_path).name}")
                return True

        elif task_status == "failed":
            print(f"   ❌ Kling task failed")
            return False

    print(f"   ❌ Kling timeout after {max_wait}s")
    return False

# ─── STEP 4: FALLBACK - KEN BURNS VIDEO ───────────────────────────────────────
def image_to_video_ffmpeg(image_path, audio_path, output_path, scene_num):
    """Fallback: create video from image with Ken Burns effect"""
    print(f"   🔄 Using FFmpeg fallback for scene {scene_num}...")

    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', str(audio_path)
    ], capture_output=True, text=True)
    duration = float(result.stdout.strip())

    effects = [
        f"scale=8000:-1,zoompan=z='min(zoom+0.0008,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*25)}:s=1920x1080",
        f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),0,x+1.2)':y='ih/2-(ih/zoom/2)':d={int(duration*25)}:s=1920x1080",
        f"scale=8000:-1,zoompan=z='if(lte(on,1),1.5,max(1.001,zoom-0.001))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*25)}:s=1920x1080",
    ]

    color_grade = "eq=contrast=1.1:brightness=-0.05:saturation=0.85"
    effect = effects[scene_num % len(effects)]

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', str(image_path),
        '-i', str(audio_path),
        '-filter_complex', f'[0:v]{effect},{color_grade},format=yuv420p[v]',
        '-map', '[v]', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-r', '25', str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# ─── STEP 5: ADD AUDIO TO KLING VIDEO ─────────────────────────────────────────
def add_audio_to_video(video_path, audio_path, output_path):
    """Combine Kling video with narration audio"""
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-i', str(audio_path),
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# ─── STEP 6: LOOP VIDEO TO MATCH AUDIO LENGTH ─────────────────────────────────
def loop_video_to_audio(video_path, audio_path, output_path):
    """Loop short Kling video to match narration length"""
    # Get audio duration
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', str(audio_path)
    ], capture_output=True, text=True)
    audio_duration = float(result.stdout.strip())

    cmd = [
        'ffmpeg', '-y',
        '-stream_loop', '-1', '-i', str(video_path),
        '-i', str(audio_path),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-b:a', '192k',
        '-t', str(audio_duration),
        '-shortest',
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# ─── STEP 7: GENERATE NARRATION ───────────────────────────────────────────────
def generate_narration(text, filename):
    print(f"🎙️ Generating narration...")

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam - deep authoritative voice

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.85,
            "style": 0.35,
            "use_speaker_boost": True
        }
    }

    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers=headers, json=data
    )

    if resp.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(resp.content)
        print(f"   ✅ Narration saved")
        return True
    else:
        print(f"   ❌ ElevenLabs error: {resp.status_code}")
        return False

# ─── STEP 8: CREATE THUMBNAIL ─────────────────────────────────────────────────
def create_thumbnail(script, bg_image_path):
    print("🖼️ Creating professional thumbnail...")

    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(5, 5, 15))

    try:
        bg = Image.open(bg_image_path).convert('RGB')
        bg = bg.resize((width, height), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg).enhance(0.3)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=3))
        img.paste(bg, (0, 0))
    except:
        pass

    draw = ImageDraw.Draw(img)

    # Dark gradient on left
    for x in range(width * 2 // 3):
        alpha = int(160 * (1 - x / (width * 2 // 3)))
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            r = max(0, r - alpha // 4)
            g = max(0, g - alpha // 4)
            b = max(0, b - alpha // 4)
            img.putpixel((x, y), (r, g, b))

    # Red accent bar
    draw.rectangle([0, 0, 10, height], fill=(200, 20, 20))

    try:
        font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_xl = font_lg = font_sm = ImageFont.load_default()

    main_text = script.get('thumbnail_text', script['title'][:35]).upper()
    sub_text = script.get('thumbnail_subtext', 'THE UNTOLD STORY').upper()

    # Word wrap
    words = main_text.split()
    lines, current = [], []
    for word in words:
        current.append(word)
        if len(' '.join(current)) > 16:
            lines.append(' '.join(current[:-1]))
            current = [word]
    if current:
        lines.append(' '.join(current))

    y = height // 2 - (len(lines) * 100) // 2

    for i, line in enumerate(lines):
        x = 28
        # Shadow
        draw.text((x+3, y+3), line, font=font_xl, fill=(0, 0, 0))
        # Main - first line yellow, rest white
        color = (255, 220, 40) if i == 0 else (255, 255, 255)
        draw.text((x, y), line, font=font_xl, fill=color)
        y += 100

    # Subtext in red
    draw.text((30, y + 15), sub_text, font=font_lg, fill=(220, 30, 30))

    # Channel badge
    draw.rectangle([25, height - 55, 280, height - 15], fill=(200, 20, 20))
    draw.text((35, height - 48), "HISTORICOVE TV", font=font_sm, fill=(255, 255, 255))

    thumbnail_path = OUTPUT_DIR / "thumbnail.jpg"
    img.save(thumbnail_path, "JPEG", quality=95)
    print(f"   ✅ Thumbnail created")
    return thumbnail_path

# ─── STEP 9: TITLE CARD ───────────────────────────────────────────────────────
def create_title_card(title):
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color=(5, 5, 15))
    draw = ImageDraw.Draw(img)

    # Subtle grid texture
    for i in range(0, width, 60):
        draw.line([(i, 0), (i, height)], fill=(15, 15, 25), width=1)
    for j in range(0, height, 60):
        draw.line([(0, j), (width, j)], fill=(15, 15, 25), width=1)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_channel = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
    except:
        font_title = font_channel = ImageFont.load_default()

    # Red line
    draw.rectangle([width//2 - 300, height//2 - 70, width//2 + 300, height//2 - 66], fill=(200, 20, 20))

    # Channel name
    ch = "HISTORICOVE TV"
    bbox = draw.textbbox((0,0), ch, font=font_channel)
    x = (width - (bbox[2]-bbox[0])) // 2
    draw.text((x, height//2 - 55), ch, font=font_channel, fill=(150, 150, 170))

    # Title
    words = title.upper().split()
    lines, current = [], []
    for w in words:
        current.append(w)
        if len(' '.join(current)) > 28:
            lines.append(' '.join(current[:-1]))
            current = [w]
    if current:
        lines.append(' '.join(current))

    y = height//2 + 10
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_title)
        x = (width - (bbox[2]-bbox[0])) // 2
        draw.text((x+2, y+2), line, font=font_title, fill=(0,0,0))
        draw.text((x, y), line, font=font_title, fill=(255,255,255))
        y += 90

    title_img = OUTPUT_DIR / "title_card.jpg"
    img.save(title_img, "JPEG", quality=95)

    title_video = OUTPUT_DIR / "title_card.mp4"
    cmd = [
        'ffmpeg', '-y', '-loop', '1', '-i', str(title_img),
        '-t', '4', '-c:v', 'libx264', '-preset', 'fast',
        '-r', '25', '-pix_fmt', 'yuv420p', str(title_video)
    ]
    subprocess.run(cmd, capture_output=True)
    return title_video

# ─── STEP 10: MERGE ALL VIDEOS ────────────────────────────────────────────────
def merge_videos(video_files, output_path):
    print("🎬 Merging all scenes...")

    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, 'w') as f:
        for vf in video_files:
            f.write(f"file '{Path(vf).absolute()}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(concat_file),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-c:a', 'aac', '-b:a', '192k',
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = Path(output_path).stat().st_size / (1024*1024)
        print(f"   ✅ Final video: {size_mb:.1f} MB")
        return True
    print(f"   ❌ Merge error: {result.stderr[-300:]}")
    return False

# ─── STEP 11: UPLOAD TO YOUTUBE ───────────────────────────────────────────────
def upload_to_youtube(video_path, thumbnail_path, script):
    print("📺 Uploading to YouTube...")

    import pickle
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = None
    if Path("token.pickle").exists():
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)

    if not creds or not creds.valid:
        print("❌ No valid YouTube credentials!")
        return None

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": script["title"],
            "description": script["description"],
            "tags": script["tags"],
            "categoryId": "27",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Upload: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"   ✅ Uploaded: https://youtu.be/{video_id}")

    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
        ).execute()
        print("   ✅ Thumbnail set")
    except Exception as e:
        print(f"   ⚠️ Thumbnail failed: {e}")

    return video_id

# ─── MAIN PIPELINE ────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("🎬 HistoriCove TV — Production Pipeline v2 (Kling AI)")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Generate script
    script = generate_script()

    scene_videos = []
    first_image = None

    # 2. Title card
    title_video = create_title_card(script["title"])
    scene_videos.append(title_video)

    # 3. Process each scene
    for i, scene in enumerate(script["scenes"]):
        print(f"\n--- Scene {i+1}/{len(script['scenes'])}: {scene['title']} ---")

        img_path = OUTPUT_DIR / f"scene_{i+1:02d}.jpg"
        audio_path = OUTPUT_DIR / f"narration_{i+1:02d}.mp3"
        kling_video = OUTPUT_DIR / f"kling_{i+1:02d}.mp4"
        final_scene = OUTPUT_DIR / f"scene_{i+1:02d}.mp4"

        # Generate image
        if not generate_image(scene["image_prompt"], img_path):
            print(f"   ⚠️ Skipping scene {i+1} - no image")
            continue

        if first_image is None:
            first_image = img_path

        # Generate narration
        if not generate_narration(scene["narration"], audio_path):
            print(f"   ⚠️ Skipping scene {i+1} - no narration")
            continue

        # Try Kling AI first
        kling_ok = image_to_video_kling(img_path, scene["image_prompt"], kling_video, i)

        if kling_ok:
            # Loop Kling video to match audio length
            loop_ok = loop_video_to_audio(kling_video, audio_path, final_scene)
            if not loop_ok:
                # Fallback
                image_to_video_ffmpeg(img_path, audio_path, final_scene, i)
        else:
            # FFmpeg fallback
            image_to_video_ffmpeg(img_path, audio_path, final_scene, i)

        if final_scene.exists():
            scene_videos.append(final_scene)

        time.sleep(3)

    if len(scene_videos) < 2:
        print("❌ Not enough scenes. Aborting.")
        return

    # 4. Create thumbnail
    bg_img = first_image or OUTPUT_DIR / "scene_01.jpg"
    thumbnail_path = create_thumbnail(script, bg_img)

    # 5. Merge
    final_video = OUTPUT_DIR / "final_video.mp4"
    if not merge_videos(scene_videos, final_video):
        print("❌ Merge failed.")
        return

    # 6. Upload
    video_id = upload_to_youtube(final_video, thumbnail_path, script)

    print("\n" + "=" * 60)
    if video_id:
        print(f"🎉 SUCCESS! https://youtu.be/{video_id}")
    else:
        print("⚠️ Video created but upload failed")
    print("=" * 60)

if __name__ == "__main__":
    main()
