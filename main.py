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
ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
KLING_ACCESS_KEY   = os.environ["KLING_ACCESS_KEY"]
KLING_SECRET_KEY   = os.environ["KLING_SECRET_KEY"]
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
    "Spartacus: The slave gladiator who almost destroyed Rome",
    "Suleiman the Magnificent: The golden age of the Ottoman Empire",
    "Julius Caesar's assassination on the Ides of March",
    "Napoleon Bonaparte's catastrophic invasion of Russia",
    "Nero: The emperor who fiddled while Rome burned",
    "Ivan the Terrible: Russia's most brutal and brilliant tsar",
    "Peter the Great: The giant tsar who dragged Russia into modernity",
    "Mehmed II: The 21-year-old sultan who ended the Byzantine Empire",
    "Cyrus the Great: The shepherd's son who built history's first empire",
    "Ramesses II: The pharaoh who turned his greatest defeat into victory",
    "Cleopatra: The last pharaoh and her battle to save Egypt",
    "Catherine the Great: The German princess who became Russia's empress",
    "Joan of Arc: The peasant girl who changed the course of history",
    "The Battle of Thermopylae: 300 Spartans against a million Persians",
    "The fall of Constantinople: The day the Roman Empire finally died",
    "The Black Death: How the plague killed half of medieval Europe",
    "Vlad the Impaler: The real Dracula and his forest of death",
    "William the Conqueror: How one battle changed England forever",
    "Boudicca: The warrior queen who burned Roman London to ashes",
    "Wu Zetian: The concubine who became China's only female emperor",
    "Pompei: The city frozen in time by the fury of Vesuvius",
    "Richard the Lionheart: The crusader king who hated his own kingdom",
    "Charlemagne: The illiterate king who became father of Europe",
    "Frederick the Great: The philosopher king who never lost a war",
    "Ashoka: The warrior emperor who chose peace after a river of blood",
    "Akbar the Great: The Mughal emperor who united a continent",
    "The Mongol invasion: How nomads destroyed the world's greatest cities",
    "Constantine the Great: The vision that changed the Roman Empire",
    "Hatshepsut: The female pharaoh who erased herself from history",
    "Zheng He: The Chinese admiral who explored the world before Columbus",
]

# ─── STEP 1: GENERATE CINEMATIC SCRIPT WITH CLAUDE ────────────────────────────
def generate_script():
    print("📜 Generating cinematic script with Claude...")
    topic = random.choice(TOPICS)
    print(f"   Topic: {topic}")

    prompt = f"""You are the world's best YouTube scriptwriter for epic historical documentaries.
Your channel has 10 million subscribers because your scripts are:
- Cinematic like a Hollywood blockbuster
- Packed with shocking real historical facts
- Written with perfect pacing and rhythm
- Emotionally gripping from first to last second

Write a COMPLETE YouTube script about: "{topic}"

CRITICAL RULES:
1. Start with the most SHOCKING moment — no introduction, drop viewer straight into action
2. Use present tense for maximum drama ("The year is 480 BC. You are standing...")
3. Every scene must end with a hook to the next
4. Include real dates, real numbers, real names
5. Use sensory details — sounds, smells, heat, cold, fear
6. Build to an emotional climax

Return ONLY this exact JSON structure, no other text:
{{
  "title": "Dramatic YouTube title under 60 chars, no quotes inside",
  "description": "SEO-optimized YouTube description, 250 words, with timestamps and keywords",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10","tag11","tag12","tag13","tag14","tag15","tag16","tag17","tag18","tag19","tag20"],
  "thumbnail_text": "MAX 6 WORDS, shocking and dramatic, ALL CAPS",
  "thumbnail_subtext": "3-4 words, supporting drama",
  "scenes": [
    {{
      "id": 1,
      "title": "HOOK",
      "narration": "Start MID-ACTION. 80-100 words. Most shocking fact or moment. Present tense. No 'welcome' or 'today we'. Example: 'The year is 323 BC. Alexander the Great lies dying...' Make viewer UNABLE to stop watching.",
      "image_prompt": "Dramatic cinematic oil painting style. [Specific historical scene with exact details]. Epic composition, chiaroscuro lighting, dark dramatic atmosphere, masterpiece quality. 16:9 widescreen format. Ultra detailed faces and costumes."
    }},
    {{
      "id": 2,
      "title": "THE WORLD",
      "narration": "100-120 words. Paint the world vividly. Show the stakes. Build the atmosphere. What was life like? What made this person/event unique?",
      "image_prompt": "..."
    }},
    {{
      "id": 3,
      "title": "THE RISE",
      "narration": "120-140 words. The turning point. Rising tension. The moment everything changed. Cliffhanger ending.",
      "image_prompt": "..."
    }},
    {{
      "id": 4,
      "title": "THE CONFLICT",
      "narration": "130-150 words. Maximum drama. The great battle, betrayal, or crisis. Real tactical and human details. Visceral and emotional.",
      "image_prompt": "..."
    }},
    {{
      "id": 5,
      "title": "THE CLIMAX",
      "narration": "130-150 words. The peak moment. The decision that changed history forever. Maximum emotional impact.",
      "image_prompt": "..."
    }},
    {{
      "id": 6,
      "title": "THE LEGACY",
      "narration": "100-120 words. What happened next. Why this matters TODAY. End with a powerful question that makes viewers think and comment. Subscribe call to action.",
      "image_prompt": "..."
    }}
  ]
}}"""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-opus-4-5",
        "max_tokens": 6000,
        "messages": [{"role": "user", "content": prompt}]
    }

    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    resp.raise_for_status()

    text = resp.json()["content"][0]["text"].strip()

    # Clean JSON
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            if part.startswith("json"):
                text = part[4:].strip()
                break
            elif "{" in part:
                text = part.strip()
                break

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    try:
        script = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON error: {e}")
        # Try to fix common issues
        text = text.replace('\n', ' ').replace('\r', '')
        script = json.loads(text)
    print(f"   ✅ Script: '{script['title']}'")
    print(f"   Scenes: {len(script['scenes'])}")
    return script

# ─── KLING JWT TOKEN ───────────────────────────────────────────────────────────
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

# ─── STEP 2: GENERATE CINEMATIC IMAGE WITH KLING ──────────────────────────────
def generate_image_kling(prompt, filename, scene_num):
    print(f"🎨 Generating cinematic image (scene {scene_num})...")

    # Enhanced prompt for historical cinematic style
    enhanced = f"""Epic historical cinematic painting. {prompt}
    Style: Dramatic chiaroscuro oil painting, reminiscent of Rembrandt and Caravaggio.
    Lighting: Dramatic side lighting with deep shadows and golden highlights.
    Mood: Powerful, epic, emotional, historically authentic.
    Quality: Museum masterpiece, ultra detailed, 8K resolution.
    Format: Cinematic widescreen 16:9."""

    payload = {
        "model": "kling-v2-1",
        "prompt": enhanced,
        "negative_prompt": "modern elements, cartoon, anime, text, watermark, blurry, low quality, distorted faces",
        "aspect_ratio": "16:9",
        "n": 1,
        "image_reference": None
    }

    resp = requests.post(
        "https://api.klingai.com/v1/images/generations",
        headers=kling_headers(),
        json=payload
    )

    if resp.status_code != 200:
        print(f"   ❌ Kling Image error: {resp.status_code} - {resp.text[:200]}")
        return fetch_pexels_fallback(prompt, filename)

    task_id = resp.json().get("data", {}).get("task_id")
    if not task_id:
        print(f"   ❌ No task_id")
        return fetch_pexels_fallback(prompt, filename)

    # Poll for result
    for attempt in range(20):
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
                img_url = images[0].get("url")
                img_resp = requests.get(img_url, timeout=30)
                with open(filename, 'wb') as f:
                    f.write(img_resp.content)
                print(f"   ✅ Kling image saved")
                return True
        elif status == "failed":
            print(f"   ❌ Kling image failed")
            return fetch_pexels_fallback(prompt, filename)

        print(f"   ⏳ Image status: {status} ({attempt+1}/20)")

    return fetch_pexels_fallback(prompt, filename)

def fetch_pexels_fallback(prompt, filename):
    """Fallback to Pexels if Kling fails"""
    print(f"   🔄 Pexels fallback...")
    try:
        keywords = prompt.split('.')[0][:60]
        headers = {"Authorization": os.environ.get("PEXELS_API_KEY", "")}
        params = {"query": keywords, "per_page": 5, "orientation": "landscape"}
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        photos = resp.json().get("photos", [])
        if photos:
            img_url = photos[0]["src"]["large2x"]
            img_resp = requests.get(img_url, timeout=30)
            with open(filename, 'wb') as f:
                f.write(img_resp.content)
            print(f"   ✅ Pexels fallback used")
            return True
    except Exception as e:
        print(f"   ❌ Pexels failed: {e}")
    return False

# ─── STEP 3: GENERATE NARRATION WITH ELEVENLABS ───────────────────────────────
def generate_narration(text, filename):
    print(f"🎙️ Generating narration...")

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
        headers=headers,
        json=data,
        timeout=60
    )

    if resp.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(resp.content)
        print(f"   ✅ Narration saved")
        return True

    print(f"   ❌ ElevenLabs error: {resp.status_code} - {resp.text[:200]}")
    return False

# ─── STEP 4: IMAGE TO VIDEO WITH KLING ────────────────────────────────────────
def image_to_video_kling(image_path, scene_prompt, output_path, scene_num):
    print(f"🎬 Kling: Image → Video (scene {scene_num})...")

    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')

    # Cinematic camera movements for historical scenes
    camera_moves = [
        "Slow cinematic push forward into the scene. Dust particles float in dramatic light. Epic atmosphere.",
        "Majestic slow pan revealing the grand scale. Dramatic clouds move overhead. Cinematic depth.",
        "Slow zoom out from close detail revealing epic landscape. Golden hour lighting shifts.",
        "Gentle camera drift revealing hidden depth. Smoke and mist add atmosphere. Masterful composition.",
        "Slow dolly shot moving through the historical scene. Torchlight flickers. Shadows dance.",
        "Camera slowly rises up revealing the full epic scale. Wind moves through the scene.",
        "Slow pull back reveal. The full dramatic scene unfolds. Cinematic masterpiece movement.",
        "Subtle environmental animation. Flames flicker, banners wave, atmosphere breathes.",
    ]
    camera = camera_moves[scene_num % len(camera_moves)]

    payload = {
        "model_name": "kling-v2-master",
        "image": img_b64,
        "prompt": f"{camera} Scene context: {scene_prompt[:150]}",
        "negative_prompt": "shaky camera, fast motion, modern elements, text, watermark, distortion, artifacts",
        "cfg_scale": 0.5,
        "mode": "pro",
        "duration": "5",
        "aspect_ratio": "16:9"
    }

    resp = requests.post(
        "https://api.klingai.com/v1/videos/image2video",
        headers=kling_headers(),
        json=payload
    )

    if resp.status_code != 200:
        print(f"   ❌ Kling Video error: {resp.status_code} - {resp.text[:200]}")
        return False

    task_id = resp.json().get("data", {}).get("task_id")
    if not task_id:
        print(f"   ❌ No task_id")
        return False

    print(f"   ⏳ Video task: {task_id}")

    # Poll for completion (max 6 minutes)
    for attempt in range(24):
        time.sleep(15)
        check = requests.get(
            f"https://api.klingai.com/v1/videos/image2video/{task_id}",
            headers=kling_headers()
        )

        if check.status_code != 200:
            continue

        data = check.json().get("data", {})
        status = data.get("task_status", "")
        print(f"   Status: {status} ({(attempt+1)*15}s)")

        if status == "succeed":
            videos = data.get("task_result", {}).get("videos", [])
            if videos:
                video_url = videos[0].get("url")
                video_resp = requests.get(video_url, timeout=60)
                with open(output_path, 'wb') as f:
                    f.write(video_resp.content)
                print(f"   ✅ Kling video downloaded")
                return True
        elif status == "failed":
            print(f"   ❌ Kling video failed")
            return False

    print(f"   ❌ Kling timeout")
    return False

# ─── STEP 5: LOOP VIDEO TO AUDIO LENGTH ───────────────────────────────────────
def loop_video_to_audio(video_path, audio_path, output_path):
    """Loop 5s Kling video to match full narration length"""
    # Get audio duration
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', str(audio_path)
    ], capture_output=True, text=True)
    duration = float(result.stdout.strip())

    color_grade = "eq=contrast=1.08:brightness=-0.03:saturation=0.88"

    cmd = [
        'ffmpeg', '-y',
        '-stream_loop', '-1',
        '-i', str(video_path),
        '-i', str(audio_path),
        '-filter_complex',
        f'[0:v]{color_grade},format=yuv420p[v];[1:a]aformat=sample_rates=44100:channel_layouts=stereo[a]',
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-t', str(duration),
        '-shortest',
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ⚠️ Loop error: {result.stderr[-200:]}")
    return result.returncode == 0

# ─── STEP 6: KEN BURNS FALLBACK ───────────────────────────────────────────────
def ken_burns_fallback(image_path, audio_path, output_path, scene_num):
    """High quality Ken Burns effect as fallback"""
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', str(audio_path)
    ], capture_output=True, text=True)
    duration = float(result.stdout.strip())
    frames = int(duration * 25)

    effects = [
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),0,min(x+1.5,iw*(1-1/zoom)))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        f"scale=8000:-1,zoompan=z='if(lte(on,1),1.4,max(1.001,zoom-0.0008))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),iw*0.3,max(0,x-1.2))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
    ]
    color_grade = "eq=contrast=1.08:brightness=-0.03:saturation=0.88"
    effect = effects[scene_num % len(effects)]

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', str(image_path),
        '-i', str(audio_path),
        '-filter_complex', f'[0:v]{effect},{color_grade},format=yuv420p[v]',
        '-map', '[v]', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest', '-r', '25', str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# ─── STEP 7: PROFESSIONAL THUMBNAIL ──────────────────────────────────────────
def create_thumbnail(script, bg_image_path):
    print("🖼️ Creating professional thumbnail...")

    W, H = 1280, 720
    img = Image.new('RGB', (W, H), (5, 5, 15))

    # Load and process background
    try:
        bg = Image.open(bg_image_path).convert('RGB')
        bg = bg.resize((W, H), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg).enhance(0.28)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
        img.paste(bg, (0, 0))
    except:
        pass

    draw = ImageDraw.Draw(img)

    # Gradient overlay left side
    for x in range(W * 3 // 4):
        alpha = int(150 * max(0, 1 - x / (W * 3 // 4)))
        for y in range(H):
            r, g, b = img.getpixel((x, y))
            img.putpixel((x, y), (
                max(0, r - alpha // 4),
                max(0, g - alpha // 4),
                max(0, b - alpha // 3)
            ))

    # Red accent bar left
    draw.rectangle([0, 0, 12, H], fill=(220, 25, 25))

    # Golden horizontal line
    draw.rectangle([20, H // 2 - 2, W // 2, H // 2 + 2], fill=(220, 180, 40))

    # Load fonts
    try:
        font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 95)
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except:
        font_xl = font_lg = font_sm = ImageFont.load_default()

    main_text = script.get('thumbnail_text', script['title'][:30]).upper()
    sub_text = script.get('thumbnail_subtext', 'THE UNTOLD STORY').upper()

    # Word wrap main text
    words = main_text.split()
    lines, current = [], []
    for word in words:
        current.append(word)
        if len(' '.join(current)) > 14:
            lines.append(' '.join(current[:-1]))
            current = [word]
    if current:
        lines.append(' '.join(current))

    # Draw main text
    y = H // 2 - (len(lines) * 105) // 2
    for i, line in enumerate(lines):
        x = 28
        # Shadow layers
        for sx, sy in [(4,4), (3,3), (2,2)]:
            draw.text((x+sx, y+sy), line, font=font_xl, fill=(0,0,0))
        # Main text
        color = (255, 220, 30) if i == 0 else (255, 255, 255)
        draw.text((x, y), line, font=font_xl, fill=color)
        y += 105

    # Subtext
    sub_y = y + 10
    draw.text((30, sub_y + 3), sub_text, font=font_lg, fill=(0,0,0))
    draw.text((28, sub_y), sub_text, font=font_lg, fill=(220, 25, 25))

    # Channel badge
    badge_w = 260
    draw.rectangle([20, H-58, 20+badge_w, H-15], fill=(180, 15, 15))
    draw.text((30, H-50), "▶ HISTORICOVE TV", font=font_sm, fill=(255,255,255))

    thumbnail_path = OUTPUT_DIR / "thumbnail.jpg"
    img.save(thumbnail_path, "JPEG", quality=95)
    print(f"   ✅ Thumbnail created")
    return thumbnail_path

# ─── STEP 8: TITLE CARD ───────────────────────────────────────────────────────
def create_title_card(title):
    W, H = 1920, 1080
    img = Image.new('RGB', (W, H), (5, 5, 15))
    draw = ImageDraw.Draw(img)

    # Grid texture
    for i in range(0, W, 80):
        draw.line([(i, 0), (i, H)], fill=(12, 12, 22), width=1)
    for j in range(0, H, 80):
        draw.line([(0, j), (W, j)], fill=(12, 12, 22), width=1)

    # Vignette effect
    center_x, center_y = W//2, H//2
    for radius in range(min(W,H)//2, 0, -20):
        alpha = int(80 * (1 - radius / (min(W,H)//2)))
        # Just darken corners conceptually via rectangles
        pass

    try:
        font_ch = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 82)
        font_tagline = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_ch = font_title = font_tagline = ImageFont.load_default()

    # Channel name
    ch = "HISTORICOVE  TV"
    bbox = draw.textbbox((0,0), ch, font=font_ch)
    x = (W - (bbox[2]-bbox[0])) // 2
    draw.text((x, H//2 - 100), ch, font=font_ch, fill=(140, 140, 160))

    # Red divider line
    draw.rectangle([W//2-280, H//2-55, W//2+280, H//2-51], fill=(200,20,20))

    # Title
    words = title.upper().split()
    lines, current = [], []
    for w in words:
        current.append(w)
        if len(' '.join(current)) > 26:
            lines.append(' '.join(current[:-1]))
            current = [w]
    if current:
        lines.append(' '.join(current))

    y = H//2 - 20
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_title)
        x = (W - (bbox[2]-bbox[0])) // 2
        draw.text((x+3, y+3), line, font=font_title, fill=(0,0,0))
        draw.text((x, y), line, font=font_title, fill=(255,255,255))
        y += 90

    # Tagline
    tagline = "WHERE HISTORY COMES ALIVE"
    bbox = draw.textbbox((0,0), tagline, font=font_tagline)
    x = (W - (bbox[2]-bbox[0])) // 2
    draw.text((x, y+15), tagline, font=font_tagline, fill=(180,20,20))

    title_img = OUTPUT_DIR / "title_card.jpg"
    img.save(title_img, "JPEG", quality=95)

    title_video = OUTPUT_DIR / "title_card.mp4"
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', str(title_img),
        '-t', '5',
        '-vf', 'fade=in:0:25,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-r', '25', str(title_video)
    ]
    subprocess.run(cmd, capture_output=True)
    print("   ✅ Title card created")
    return title_video

# ─── STEP 9: MERGE ALL SCENES ─────────────────────────────────────────────────
def merge_videos(video_files, output_path):
    print(f"🎬 Merging {len(video_files)} scenes...")

    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, 'w') as f:
        for vf in video_files:
            f.write(f"file '{Path(vf).absolute()}'\n")

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

    media = MediaFileUpload(
        str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4"
    )
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"   Upload: {pct}%")

    video_id = response["id"]
    print(f"   ✅ Uploaded: https://youtu.be/{video_id}")

    # Set thumbnail
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
    print("=" * 65)
    print("🎬  HistoriCove TV — Professional Production Pipeline v3")
    print(f"    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    # 1. Generate script
    script = generate_script()

    scene_videos = []
    first_image = None

    # 2. Title card
    print("\n📽️ Creating title card...")
    title_video = create_title_card(script["title"])
    scene_videos.append(title_video)

    # 3. Process each scene
    total = len(script["scenes"])
    for i, scene in enumerate(script["scenes"]):
        print(f"\n{'─'*50}")
        print(f"🎭 Scene {i+1}/{total}: {scene['title']}")
        print(f"{'─'*50}")

        img_path    = OUTPUT_DIR / f"scene_{i+1:02d}.jpg"
        audio_path  = OUTPUT_DIR / f"narration_{i+1:02d}.mp3"
        kling_vid   = OUTPUT_DIR / f"kling_{i+1:02d}.mp4"
        final_scene = OUTPUT_DIR / f"final_{i+1:02d}.mp4"

        # Generate image
        img_ok = generate_image_kling(scene["image_prompt"], img_path, i)
        if not img_ok:
            print(f"   ⚠️ Skipping scene {i+1} — no image")
            continue

        if first_image is None:
            first_image = img_path

        # Generate narration
        audio_ok = generate_narration(scene["narration"], audio_path)
        if not audio_ok:
            print(f"   ⚠️ Skipping scene {i+1} — no narration")
            continue

        # Try Kling image→video
        kling_ok = image_to_video_kling(img_path, scene["image_prompt"], kling_vid, i)

        if kling_ok:
            loop_ok = loop_video_to_audio(kling_vid, audio_path, final_scene)
            if not loop_ok:
                print("   🔄 Loop failed, using Ken Burns...")
                ken_burns_fallback(img_path, audio_path, final_scene, i)
        else:
            print("   🔄 Using Ken Burns fallback...")
            ken_burns_fallback(img_path, audio_path, final_scene, i)

        if final_scene.exists() and final_scene.stat().st_size > 0:
            scene_videos.append(final_scene)
            print(f"   ✅ Scene {i+1} complete")
        
        time.sleep(2)

    if len(scene_videos) < 3:
        print("\n❌ Not enough scenes. Aborting.")
        return

    # 4. Thumbnail
    bg = first_image or OUTPUT_DIR / "scene_01.jpg"
    thumbnail = create_thumbnail(script, bg)

    # 5. Merge
    final_video = OUTPUT_DIR / "final_video.mp4"
    if not merge_videos(scene_videos, final_video):
        print("❌ Merge failed.")
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
