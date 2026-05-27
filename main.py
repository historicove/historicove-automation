import os
import json
import time
import random
import requests
import subprocess
import jwt
import base64
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# ─── CONFIG ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]
ELEVENLABS_API_KEY  = os.environ["ELEVENLABS_API_KEY"]
KLING_ACCESS_KEY    = os.environ["KLING_ACCESS_KEY"]
KLING_SECRET_KEY    = os.environ["KLING_SECRET_KEY"]
PEXELS_API_KEY      = os.environ.get("PEXELS_API_KEY", "")
ELEVENLABS_VOICE_ID = "JJCR1UICgHnHljtvu5uF"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── TOPICS ────────────────────────────────────────────────────────────────────
TOPICS = [
    "Alexander the Great's final days and mysterious death in Babylon",
    "Genghis Khan: The shepherd boy who conquered half the world",
    "Hannibal Barca's impossible crossing of the Alps with war elephants",
    "Attila the Hun: The scourge of God who made Rome tremble",
    "Saladin and the recapture of Jerusalem from the Crusaders",
    "Tamerlane: The lame conqueror who built pyramids of skulls",
    "Suleiman the Magnificent: The golden age of the Ottoman Empire",
    "Julius Caesar's assassination on the Ides of March",
    "Napoleon Bonaparte's catastrophic invasion of Russia",
    "Ivan the Terrible: Russia's most brutal and brilliant tsar",
    "Mehmed II: The 21-year-old sultan who ended the Byzantine Empire",
    "Cyrus the Great: The shepherd's son who built history's first empire",
    "Cleopatra: The last pharaoh and her battle to save Egypt",
    "Catherine the Great: The German princess who became Russia's empress",
    "Joan of Arc: The peasant girl who changed the course of history",
    "The Battle of Thermopylae: 300 Spartans against a million Persians",
    "The fall of Constantinople: The day the Roman Empire finally died",
    "Vlad the Impaler: The real Dracula and his forest of death",
    "Boudicca: The warrior queen who burned Roman London to ashes",
    "Wu Zetian: The concubine who became China's only female emperor",
    "Richard the Lionheart: The crusader king who hated his own kingdom",
    "Charlemagne: The illiterate king who became father of Europe",
    "Ashoka: The warrior emperor who chose peace after a river of blood",
    "Akbar the Great: The Mughal emperor who united a continent",
    "Hatshepsut: The female pharaoh who erased herself from history",
    "Zheng He: The Chinese admiral who explored the world before Columbus",
    "Peter the Great: The giant tsar who dragged Russia into modernity",
    "Nero: The emperor who fiddled while Rome burned",
    "Spartacus: The slave gladiator who almost destroyed Rome",
    "Ramesses II: The pharaoh who turned his greatest defeat into victory",
]

# ─── STEP 1: GENERATE FULL SCRIPT WITH CLAUDE ─────────────────────────────────
def generate_script():
    print("📜 Generating cinematic script with Claude...")
    topic = random.choice(TOPICS)
    print(f"   Topic: {topic}")

    prompt = f"""You are the world's best YouTube scriptwriter for epic historical documentaries with 10 million subscribers.

Write a COMPLETE professional YouTube script about: "{topic}"

CRITICAL: For each scene, generate MULTIPLE shot descriptions (sub_shots).
Each sub_shot = one image + one 5-second video clip.
A 60-second narration needs 12 sub_shots. A 90-second narration needs 18 sub_shots.

Return ONLY this exact JSON, no other text:
{{
  "title": "Dramatic YouTube title under 60 chars",
  "description": "SEO-optimized YouTube description 250 words with timestamps",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10","tag11","tag12","tag13","tag14","tag15","tag16","tag17","tag18","tag19","tag20"],
  "thumbnail_text": "MAX 6 WORDS shocking dramatic ALL CAPS",
  "thumbnail_subtext": "3-4 words supporting",
  "scenes": [
    {{
      "id": 1,
      "title": "HOOK",
      "narration": "Start mid-action. 80-100 words. Most shocking moment. Present tense. No welcome or introduction.",
      "sub_shots": [
        {{
          "shot_id": "1a",
          "image_prompt": "Ultra-realistic historical oil painting style. [Very specific scene detail]. Dramatic chiaroscuro lighting like Rembrandt. Dark epic atmosphere. Authentic period costumes and setting. 16:9 cinematic.",
          "motion_prompt": "Slow dramatic camera push forward. Dust particles in golden light. Epic cinematic movement."
        }},
        {{
          "shot_id": "1b",
          "image_prompt": "Ultra-realistic historical painting. [Different angle of same scene]. Close-up on faces showing emotion. Dramatic shadows.",
          "motion_prompt": "Slow pan revealing hidden depth. Atmospheric mist. Masterful composition."
        }},
        {{
          "shot_id": "1c",
          "image_prompt": "Cinematic wide shot. [Epic landscape or battlefield]. Golden hour dramatic lighting. Authentic historical details.",
          "motion_prompt": "Camera slowly rises revealing epic scale. Wind moves banners. Cinematic reveal."
        }},
        {{
          "shot_id": "1d",
          "image_prompt": "Close-up detail shot. [Specific object, weapon, or face]. Ultra detailed realistic painting. Dramatic lighting.",
          "motion_prompt": "Slow zoom into detail. Atmosphere breathes. Torchlight flickers."
        }},
        {{
          "shot_id": "1e",
          "image_prompt": "Medium shot. [Character in action]. Authentic period setting. Epic scale. Realistic historical painting.",
          "motion_prompt": "Gentle camera drift. Shadows dance. Environmental animation."
        }},
        {{
          "shot_id": "1f",
          "image_prompt": "Establishing wide shot. [Location overview]. Dramatic sky. Historical accuracy. Cinematic composition.",
          "motion_prompt": "Slow pull back reveal. Full scene unfolds. Epic atmosphere."
        }}
      ]
    }},
    {{
      "id": 2,
      "title": "THE WORLD",
      "narration": "100-120 words. Paint the world vividly. Show the stakes. What made this unique?",
      "sub_shots": [
        {{"shot_id":"2a","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"2b","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"2c","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"2d","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"2e","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"2f","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"2g","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"2h","image_prompt":"...","motion_prompt":"..."}}
      ]
    }},
    {{
      "id": 3,
      "title": "THE RISE",
      "narration": "120-140 words. The turning point. Rising tension. Cliffhanger ending.",
      "sub_shots": [
        {{"shot_id":"3a","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3b","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3c","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3d","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3e","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3f","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3g","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3h","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"3i","image_prompt":"...","motion_prompt":"..."}}
      ]
    }},
    {{
      "id": 4,
      "title": "THE CONFLICT",
      "narration": "130-150 words. Maximum drama. The great battle or betrayal. Visceral and emotional.",
      "sub_shots": [
        {{"shot_id":"4a","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4b","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4c","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4d","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4e","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4f","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4g","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4h","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4i","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"4j","image_prompt":"...","motion_prompt":"..."}}
      ]
    }},
    {{
      "id": 5,
      "title": "THE CLIMAX",
      "narration": "130-150 words. Peak moment. Decision that changed history. Maximum emotional impact.",
      "sub_shots": [
        {{"shot_id":"5a","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5b","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5c","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5d","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5e","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5f","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5g","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5h","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5i","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"5j","image_prompt":"...","motion_prompt":"..."}}
      ]
    }},
    {{
      "id": 6,
      "title": "THE LEGACY",
      "narration": "100-120 words. What happened next. Why this matters TODAY. End with powerful question. Subscribe CTA.",
      "sub_shots": [
        {{"shot_id":"6a","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"6b","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"6c","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"6d","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"6e","image_prompt":"...","motion_prompt":"..."}},
        {{"shot_id":"6f","image_prompt":"...","motion_prompt":"..."}}
      ]
    }}
  ]
}}

RULES:
- Fill ALL image_prompt and motion_prompt fields with specific, detailed content
- Each image_prompt must be unique and specific to that exact moment
- Images must look ULTRA REALISTIC, not cartoonish or AI-looking
- Use style: "photorealistic historical oil painting, Rembrandt lighting, museum quality"
- Return ONLY the JSON"""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-opus-4-5",
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": prompt}]
    }

    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    resp.raise_for_status()

    text = resp.json()["content"][0]["text"].strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    script = json.loads(text)
    total_shots = sum(len(s.get("sub_shots", [])) for s in script["scenes"])
    print(f"   ✅ Script: '{script['title']}'")
    print(f"   Scenes: {len(script['scenes'])}, Total shots: {total_shots}")
    return script

# ─── KLING TOKEN ───────────────────────────────────────────────────────────────
def get_kling_token():
    payload = {
        "iss": KLING_ACCESS_KEY,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5
    }
    return jwt.encode(payload, KLING_SECRET_KEY, algorithm="HS256")

def kling_headers():
    return {
        "Authorization": f"Bearer {get_kling_token()}",
        "Content-Type": "application/json"
    }

# ─── STEP 2: GENERATE IMAGE WITH KLING ────────────────────────────────────────
def generate_image_kling(prompt, filename):
    enhanced = f"Photorealistic historical oil painting masterpiece. {prompt} Style: Rembrandt chiaroscuro lighting, museum quality, ultra detailed authentic period costumes and architecture, dramatic atmosphere, 8K resolution. NOT cartoon, NOT AI-looking, NOT modern."

    payload = {
        "model": "kling-v2-1",
        "prompt": enhanced,
        "negative_prompt": "cartoon, anime, CGI, modern, watermark, text, blurry, distorted, unrealistic, plastic, AI-looking",
        "aspect_ratio": "16:9",
        "n": 1
    }

    resp = requests.post(
        "https://api.klingai.com/v1/images/generations",
        headers=kling_headers(), json=payload
    )

    if resp.status_code != 200:
        return fetch_pexels(prompt, filename)

    task_id = resp.json().get("data", {}).get("task_id")
    if not task_id:
        return fetch_pexels(prompt, filename)

    for _ in range(20):
        time.sleep(8)
        check = requests.get(
            f"https://api.klingai.com/v1/images/generations/{task_id}",
            headers=kling_headers()
        )
        if check.status_code != 200:
            continue
        data = check.json().get("data", {})
        status = data.get("task_status", "")
        if status == "succeed":
            images = data.get("task_result", {}).get("images", [])
            if images:
                img_resp = requests.get(images[0]["url"], timeout=30)
                with open(filename, 'wb') as f:
                    f.write(img_resp.content)
                return True
        elif status == "failed":
            return fetch_pexels(prompt, filename)

    return fetch_pexels(prompt, filename)

def fetch_pexels(prompt, filename):
    try:
        keywords = prompt.split('.')[0][:50]
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": keywords, "per_page": 3, "orientation": "landscape"}
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        photos = resp.json().get("photos", [])
        if photos:
            img_resp = requests.get(photos[0]["src"]["large2x"], timeout=30)
            with open(filename, 'wb') as f:
                f.write(img_resp.content)
            return True
    except:
        pass
    return False

# ─── STEP 3: IMAGE TO VIDEO WITH KLING ────────────────────────────────────────
def image_to_video_kling(image_path, motion_prompt, output_path):
    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        "model_name": "kling-v2-master",
        "image": img_b64,
        "prompt": f"{motion_prompt} Cinematic, dramatic, historically authentic.",
        "negative_prompt": "shaky, fast motion, modern, text, watermark, distortion",
        "cfg_scale": 0.5,
        "mode": "pro",
        "duration": "5",
        "aspect_ratio": "16:9"
    }

    resp = requests.post(
        "https://api.klingai.com/v1/videos/image2video",
        headers=kling_headers(), json=payload
    )

    if resp.status_code != 200:
        return False

    task_id = resp.json().get("data", {}).get("task_id")
    if not task_id:
        return False

    for _ in range(24):
        time.sleep(15)
        check = requests.get(
            f"https://api.klingai.com/v1/videos/image2video/{task_id}",
            headers=kling_headers()
        )
        if check.status_code != 200:
            continue
        data = check.json().get("data", {})
        status = data.get("task_status", "")
        if status == "succeed":
            videos = data.get("task_result", {}).get("videos", [])
            if videos:
                video_resp = requests.get(videos[0]["url"], timeout=60)
                with open(output_path, 'wb') as f:
                    f.write(video_resp.content)
                return True
        elif status == "failed":
            return False

    return False

# ─── STEP 4: GENERATE NARRATION ───────────────────────────────────────────────
def generate_narration(text, filename):
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY.strip(),
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.40,
            "similarity_boost": 0.88,
            "style": 0.40,
            "use_speaker_boost": True
        }
    }
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers=headers, json=data, timeout=60
    )
    if resp.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(resp.content)
        return True
    print(f"   ❌ ElevenLabs: {resp.status_code}")
    return False

# ─── STEP 5: CONCATENATE SHOT VIDEOS ──────────────────────────────────────────
def concat_shot_videos(video_paths, output_path):
    """Join all 5-second shot videos into one scene video (no audio)"""
    concat_file = OUTPUT_DIR / f"concat_shots_{int(time.time())}.txt"
    with open(concat_file, 'w') as f:
        for vp in video_paths:
            f.write(f"file '{Path(vp).absolute()}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(concat_file),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-an',
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    concat_file.unlink(missing_ok=True)
    return result.returncode == 0

# ─── STEP 6: MERGE VIDEO + AUDIO ──────────────────────────────────────────────
def merge_video_audio(video_path, audio_path, output_path):
    """Add narration audio to scene video"""
    # Get durations
    def get_duration(path):
        r = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', str(path)
        ], capture_output=True, text=True)
        return float(r.stdout.strip())

    video_dur = get_duration(video_path)
    audio_dur = get_duration(audio_path)
    print(f"   Video: {video_dur:.1f}s | Audio: {audio_dur:.1f}s")

    if video_dur >= audio_dur:
        # Video is long enough — just merge
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(output_path)
        ]
    else:
        # Video shorter than audio — loop video
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1', '-i', str(video_path),
            '-i', str(audio_path),
            '-map', '0:v:0', '-map', '1:a:0',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            '-t', str(audio_dur),
            str(output_path)
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ Audio merged")
        return True
    print(f"   ❌ Merge error: {result.stderr[-200:]}")
    return False

# ─── STEP 7: THUMBNAIL ────────────────────────────────────────────────────────
def create_thumbnail(script, bg_image_path):
    print("🖼️ Creating thumbnail...")
    W, H = 1280, 720
    img = Image.new('RGB', (W, H), (5, 5, 15))

    try:
        bg = Image.open(bg_image_path).convert('RGB')
        bg = bg.resize((W, H), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg).enhance(0.28)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
        img.paste(bg, (0, 0))
    except:
        pass

    draw = ImageDraw.Draw(img)

    for x in range(W * 3 // 4):
        alpha = int(150 * max(0, 1 - x / (W * 3 // 4)))
        for y in range(H):
            r, g, b = img.getpixel((x, y))
            img.putpixel((x, y), (max(0, r-alpha//4), max(0, g-alpha//4), max(0, b-alpha//3)))

    draw.rectangle([0, 0, 12, H], fill=(220, 25, 25))
    draw.rectangle([20, H//2-2, W//2, H//2+2], fill=(220, 180, 40))

    try:
        font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 95)
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except:
        font_xl = font_lg = font_sm = ImageFont.load_default()

    main_text = script.get('thumbnail_text', script['title'][:30]).upper()
    sub_text = script.get('thumbnail_subtext', 'THE UNTOLD STORY').upper()

    words = main_text.split()
    lines, current = [], []
    for word in words:
        current.append(word)
        if len(' '.join(current)) > 14:
            lines.append(' '.join(current[:-1]))
            current = [word]
    if current:
        lines.append(' '.join(current))

    y = H//2 - (len(lines)*105)//2
    for i, line in enumerate(lines):
        for sx, sy in [(4,4),(3,3),(2,2)]:
            draw.text((28+sx, y+sy), line, font=font_xl, fill=(0,0,0))
        draw.text((28, y), line, font=font_xl, fill=(255,220,30) if i==0 else (255,255,255))
        y += 105

    draw.text((30, y+13), sub_text, font=font_lg, fill=(0,0,0))
    draw.text((28, y+10), sub_text, font=font_lg, fill=(220,25,25))
    draw.rectangle([20, H-58, 280, H-15], fill=(180,15,15))
    draw.text((30, H-50), "▶ HISTORICOVE TV", font=font_sm, fill=(255,255,255))

    path = OUTPUT_DIR / "thumbnail.jpg"
    img.save(path, "JPEG", quality=95)
    print("   ✅ Thumbnail created")
    return path

# ─── STEP 8: TITLE CARD ───────────────────────────────────────────────────────
def create_title_card(title):
    W, H = 1920, 1080
    img = Image.new('RGB', (W, H), (5, 5, 15))
    draw = ImageDraw.Draw(img)

    for i in range(0, W, 80):
        draw.line([(i,0),(i,H)], fill=(12,12,22), width=1)
    for j in range(0, H, 80):
        draw.line([(0,j),(W,j)], fill=(12,12,22), width=1)

    try:
        font_ch = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 82)
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_ch = font_title = font_tag = ImageFont.load_default()

    ch = "HISTORICOVE  TV"
    bbox = draw.textbbox((0,0), ch, font=font_ch)
    x = (W-(bbox[2]-bbox[0]))//2
    draw.text((x, H//2-100), ch, font=font_ch, fill=(140,140,160))
    draw.rectangle([W//2-280, H//2-55, W//2+280, H//2-51], fill=(200,20,20))

    words = title.upper().split()
    lines, current = [], []
    for w in words:
        current.append(w)
        if len(' '.join(current)) > 26:
            lines.append(' '.join(current[:-1]))
            current = [w]
    if current:
        lines.append(' '.join(current))

    y = H//2-20
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_title)
        x = (W-(bbox[2]-bbox[0]))//2
        draw.text((x+3,y+3), line, font=font_title, fill=(0,0,0))
        draw.text((x,y), line, font=font_title, fill=(255,255,255))
        y += 90

    tagline = "WHERE HISTORY COMES ALIVE"
    bbox = draw.textbbox((0,0), tagline, font=font_tag)
    x = (W-(bbox[2]-bbox[0]))//2
    draw.text((x, y+15), tagline, font=font_tag, fill=(180,20,20))

    title_img = OUTPUT_DIR / "title_card.jpg"
    img.save(title_img, "JPEG", quality=95)

    title_video = OUTPUT_DIR / "title_card.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', str(title_img),
        '-t', '4', '-vf', 'fade=in:0:25,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-r', '25', '-an', str(title_video)
    ], capture_output=True)
    return title_video

# ─── STEP 9: MERGE ALL SCENES ─────────────────────────────────────────────────
def merge_all_scenes(scene_video_paths, output_path):
    print(f"🎬 Merging {len(scene_video_paths)} scenes...")
    concat_file = OUTPUT_DIR / "final_concat.txt"
    with open(concat_file, 'w') as f:
        for vp in scene_video_paths:
            f.write(f"file '{Path(vp).absolute()}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(concat_file),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size = Path(output_path).stat().st_size / (1024*1024)
        print(f"   ✅ Final video: {size:.1f} MB")
        return True
    print(f"   ❌ Merge failed: {result.stderr[-300:]}")
    return False

# ─── STEP 10: UPLOAD TO YOUTUBE ───────────────────────────────────────────────
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
        print("❌ No YouTube credentials!")
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
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Upload: {int(status.progress()*100)}%")

    video_id = response["id"]
    print(f"   ✅ https://youtu.be/{video_id}")

    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
        ).execute()
        print("   ✅ Thumbnail set")
    except Exception as e:
        print(f"   ⚠️ Thumbnail: {e}")

    return video_id

# ─── MAIN PIPELINE ────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("🎬  HistoriCove TV — Professional Pipeline v4")
    print(f"    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    # 1. Generate script with sub_shots
    script = generate_script()

    all_scene_videos = []
    first_image = None

    # 2. Title card
    title_video = create_title_card(script["title"])
    all_scene_videos.append(title_video)

    # 3. Process each scene
    for scene in script["scenes"]:
        print(f"\n{'─'*55}")
        print(f"🎭 Scene {scene['id']}/6: {scene['title']}")
        print(f"{'─'*55}")

        sub_shots = scene.get("sub_shots", [])
        print(f"   Sub-shots: {len(sub_shots)}")

        # Generate narration for this scene
        audio_path = OUTPUT_DIR / f"narration_{scene['id']:02d}.mp3"
        print(f"🎙️ Generating narration...")
        audio_ok = generate_narration(scene["narration"], audio_path)
        if not audio_ok:
            print(f"   ⚠️ No narration, skipping scene")
            continue

        # Process each sub_shot
        shot_videos = []
        for j, shot in enumerate(sub_shots):
            shot_id = shot.get("shot_id", f"{scene['id']}{j}")
            img_path = OUTPUT_DIR / f"img_{shot_id}.jpg"
            vid_path = OUTPUT_DIR / f"vid_{shot_id}.mp4"

            print(f"\n   🖼️ Shot {shot_id} ({j+1}/{len(sub_shots)})")

            # Generate image
            img_ok = generate_image_kling(shot["image_prompt"], img_path)
            if not img_ok:
                print(f"      ⚠️ No image")
                continue

            if first_image is None:
                first_image = img_path

            # Generate 5-second video from image
            print(f"      🎬 Kling video...")
            vid_ok = image_to_video_kling(img_path, shot["motion_prompt"], vid_path)
            if vid_ok:
                shot_videos.append(vid_path)
                print(f"      ✅ Shot {shot_id} done")
            else:
                print(f"      ⚠️ Kling failed for shot {shot_id}")

        if not shot_videos:
            print(f"   ⚠️ No videos for scene {scene['id']}")
            continue

        # Concatenate all shot videos for this scene (no audio)
        scene_video_raw = OUTPUT_DIR / f"scene_{scene['id']:02d}_raw.mp4"
        print(f"\n   🔗 Joining {len(shot_videos)} shots...")
        concat_ok = concat_shot_videos(shot_videos, scene_video_raw)
        if not concat_ok:
            print(f"   ❌ Concat failed")
            continue

        # Merge scene video with narration audio
        scene_video_final = OUTPUT_DIR / f"scene_{scene['id']:02d}_final.mp4"
        merge_ok = merge_video_audio(scene_video_raw, audio_path, scene_video_final)
        if merge_ok and scene_video_final.exists():
            all_scene_videos.append(scene_video_final)
            print(f"   ✅ Scene {scene['id']} complete!")

    if len(all_scene_videos) < 2:
        print("\n❌ Not enough scenes. Aborting.")
        return

    # 4. Thumbnail
    bg = first_image or OUTPUT_DIR / "img_1a.jpg"
    thumbnail = create_thumbnail(script, bg)

    # 5. Merge all scenes
    final_video = OUTPUT_DIR / "final_video.mp4"
    if not merge_all_scenes(all_scene_videos, final_video):
        print("❌ Final merge failed.")
        return

    # 6. Upload
    video_id = upload_to_youtube(final_video, thumbnail, script)

    print("\n" + "=" * 65)
    if video_id:
        print(f"🎉  SUCCESS!")
        print(f"    https://youtu.be/{video_id}")
        print(f"    Title: {script['title']}")
    else:
        print("⚠️  Video created but upload failed")
    print("=" * 65)

if __name__ == "__main__":
    main()
