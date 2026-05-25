import os
import json
import time
import random
import requests
import textwrap
import subprocess
from pathlib import Path
from datetime import datetime

import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# ─── CONFIG ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY    = os.environ["GEMINI_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
PEXELS_API_KEY    = os.environ["PEXELS_API_KEY"]

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

HISTORICAL_FIGURES = [
    "Alexander the Great", "Cleopatra", "Julius Caesar", "Genghis Khan",
    "Napoleon Bonaparte", "Saladin", "Attila the Hun", "Hannibal Barca",
    "Cyrus the Great", "Ramesses II", "Suleiman the Magnificent",
    "Tamerlane", "Richard the Lionheart", "Frederick the Great",
    "Ashoka the Great", "Charlemagne", "Vlad the Impaler",
    "Ivan the Terrible", "Peter the Great", "Catherine the Great",
    "William the Conqueror", "Joan of Arc", "Marcus Aurelius",
    "Spartacus", "Nero", "Constantine the Great", "Justinian I",
    "Mehmed II", "Akbar the Great"
]

# ─── STEP 1: GENERATE STORY ───────────────────────────────────────────────────
def generate_story():
    print("📜 Generating historical story with Gemini...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    figure = random.choice(HISTORICAL_FIGURES)
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""You are a master historical storyteller for a YouTube channel called HistoriCove TV.

Today is {today}. Write a dramatic, cinematic, and deeply engaging historical narrative about: {figure}

REQUIREMENTS:
- Write exactly 10 scenes
- Each scene must have:
  * SCENE_NUMBER: (1-10)
  * SCENE_TITLE: (short dramatic title)
  * NARRATION: (150-200 words of vivid, emotional storytelling — this will be spoken aloud)
  * IMAGE_SEARCH: (3-5 specific keywords to find a matching historical image on Pexels)
- Total narration should be 1500-2000 words (about 10 minutes when spoken)
- Write in present tense for drama
- Use powerful, emotional language
- Include real historical facts mixed with vivid descriptions

Also provide at the end:
VIDEO_TITLE: (SEO-optimized YouTube title, 60 chars max, include the person's name)
VIDEO_DESCRIPTION: (300 word YouTube description with historical context, keywords naturally included)
VIDEO_TAGS: (20 comma-separated tags: mix of broad history tags and specific tags)
VIDEO_HASHTAGS: (8 hashtags like #HistoryDocumentary #AncientHistory etc)

Format each scene EXACTLY like this:
---SCENE---
SCENE_NUMBER: 1
SCENE_TITLE: The Rise of a Legend
NARRATION: [narration text here]
IMAGE_SEARCH: ancient warrior battle sword bronze age
---END_SCENE---

Then at the very end:
---META---
VIDEO_TITLE: [title]
VIDEO_DESCRIPTION: [description]
VIDEO_TAGS: [tags]
VIDEO_HASHTAGS: [hashtags]
---END_META---"""

    response = model.generate_content(prompt)
    raw = response.text

    # Parse scenes
    scenes = []
    scene_blocks = raw.split("---SCENE---")[1:]
    for block in scene_blocks:
        block = block.split("---END_SCENE---")[0].strip()
        scene = {}
        for line in block.split("\n"):
            if line.startswith("SCENE_NUMBER:"):
                scene["number"] = line.replace("SCENE_NUMBER:", "").strip()
            elif line.startswith("SCENE_TITLE:"):
                scene["title"] = line.replace("SCENE_TITLE:", "").strip()
            elif line.startswith("NARRATION:"):
                scene["narration"] = line.replace("NARRATION:", "").strip()
            elif line.startswith("IMAGE_SEARCH:"):
                scene["image_search"] = line.replace("IMAGE_SEARCH:", "").strip()
        if "narration" in scene and len(scene.get("narration","")) < 50:
            # narration might be multiline
            idx = block.find("NARRATION:")
            end = block.find("IMAGE_SEARCH:")
            if idx != -1 and end != -1:
                scene["narration"] = block[idx+10:end].strip()
        if scene:
            scenes.append(scene)

    # Parse meta
    meta = {}
    if "---META---" in raw:
        meta_block = raw.split("---META---")[1].split("---END_META---")[0].strip()
        for line in meta_block.split("\n"):
            if line.startswith("VIDEO_TITLE:"):
                meta["title"] = line.replace("VIDEO_TITLE:", "").strip()
            elif line.startswith("VIDEO_DESCRIPTION:"):
                meta["description"] = line.replace("VIDEO_DESCRIPTION:", "").strip()
            elif line.startswith("VIDEO_TAGS:"):
                meta["tags"] = line.replace("VIDEO_TAGS:", "").strip()
            elif line.startswith("VIDEO_HASHTAGS:"):
                meta["hashtags"] = line.replace("VIDEO_HASHTAGS:", "").strip()

    print(f"✅ Story generated: {len(scenes)} scenes about {figure}")
    print(f"   Title: {meta.get('title', 'N/A')}")

    return {"figure": figure, "scenes": scenes, "meta": meta}

# ─── STEP 2: FETCH IMAGES FROM PEXELS ─────────────────────────────────────────
def fetch_images(story_data):
    print("🖼️  Fetching historical images from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    image_paths = []

    for i, scene in enumerate(story_data["scenes"]):
        query = scene.get("image_search", f"ancient history {story_data['figure']}")
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&orientation=landscape"

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            data = resp.json()
            photos = data.get("photos", [])

            if not photos:
                # fallback search
                fallback = f"ancient history monument ruins"
                url2 = f"https://api.pexels.com/v1/search?query={fallback}&per_page=5&orientation=landscape"
                resp2 = requests.get(url2, headers=headers, timeout=15)
                photos = resp2.json().get("photos", [])

            if photos:
                photo = random.choice(photos[:3])
                img_url = photo["src"]["large2x"]
                img_path = OUTPUT_DIR / f"scene_{i+1:02d}.jpg"

                img_resp = requests.get(img_url, timeout=30)
                with open(img_path, "wb") as f:
                    f.write(img_resp.content)
                image_paths.append(str(img_path))
                print(f"   ✅ Scene {i+1}: image downloaded")
            else:
                print(f"   ⚠️  Scene {i+1}: no image found, using previous")
                if image_paths:
                    image_paths.append(image_paths[-1])

        except Exception as e:
            print(f"   ❌ Scene {i+1} image error: {e}")
            if image_paths:
                image_paths.append(image_paths[-1])

        time.sleep(0.5)

    return image_paths

# ─── STEP 3: GENERATE NARRATION AUDIO ─────────────────────────────────────────
def generate_audio(story_data):
    print("🎙️  Generating narration audio with ElevenLabs...")
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio_paths = []

    # Use a dramatic male narrator voice
    VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam - deep, dramatic

    for i, scene in enumerate(story_data["scenes"]):
        narration = scene.get("narration", "")
        if not narration:
            continue

        try:
            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=narration,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            )
            audio_path = OUTPUT_DIR / f"audio_{i+1:02d}.mp3"
            save(audio, str(audio_path))
            audio_paths.append(str(audio_path))
            print(f"   ✅ Scene {i+1}: audio generated")
            time.sleep(1)

        except Exception as e:
            print(f"   ❌ Scene {i+1} audio error: {e}")

    return audio_paths

# ─── STEP 4: GET AUDIO DURATION ────────────────────────────────────────────────
def get_duration(audio_path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", audio_path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except:
        return 30.0

# ─── STEP 5: BUILD VIDEO WITH FFMPEG ──────────────────────────────────────────
def build_video(image_paths, audio_paths, story_data):
    print("🎬 Building video with FFmpeg...")

    scene_videos = []

    for i, (img, aud) in enumerate(zip(image_paths, audio_paths)):
        if not os.path.exists(img) or not os.path.exists(aud):
            continue

        duration = get_duration(aud)
        out = str(OUTPUT_DIR / f"scene_{i+1:02d}.mp4")

        # Ken Burns effect: slow zoom in
        zoom_filter = (
            f"zoompan=z='min(zoom+0.0008,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration*25)}:s=1920x1080:fps=25"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img,
            "-i", aud,
            "-filter_complex",
            f"[0:v]{zoom_filter},format=yuv420p[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-t", str(duration + 0.5),
            out
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            scene_videos.append(out)
            print(f"   ✅ Scene {i+1}: video rendered ({duration:.1f}s)")
        else:
            print(f"   ❌ Scene {i+1}: FFmpeg error")
            print(result.stderr[-500:])

    if not scene_videos:
        raise Exception("No scene videos were created!")

    # Add title card at beginning
    figure = story_data["figure"]
    title_text = story_data["meta"].get("title", figure)
    title_card = str(OUTPUT_DIR / "title_card.mp4")

    title_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=4:r=25",
        "-filter_complex",
        f"drawtext=text='{title_text}':fontcolor=white:fontsize=60"
        f":x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-t", "4",
        title_card
    ]
    subprocess.run(title_cmd, capture_output=True)

    # Concatenate all scenes
    concat_list = str(OUTPUT_DIR / "concat_list.txt")
    with open(concat_list, "w") as f:
        if os.path.exists(title_card):
            f.write(f"file '{os.path.abspath(title_card)}'\n")
        for v in scene_videos:
            f.write(f"file '{os.path.abspath(v)}'\n")

    final_video = str(OUTPUT_DIR / "final_video.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        final_video
    ]
    result = subprocess.run(concat_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        duration = get_duration(final_video)
        print(f"✅ Final video created: {duration/60:.1f} minutes")
        return final_video
    else:
        raise Exception(f"Concat failed: {result.stderr[-500:]}")

# ─── STEP 6: UPLOAD TO YOUTUBE ────────────────────────────────────────────────
def get_youtube_service():
    creds = None
    token_path = "token.pickle"

    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_path, story_data):
    print("📤 Uploading to YouTube...")
    youtube = get_youtube_service()

    meta = story_data["meta"]
    title = meta.get("title", f"The Story of {story_data['figure']}")
    description = meta.get("description", "")
    tags_str = meta.get("tags", "history,documentary,ancient history")
    hashtags = meta.get("hashtags", "#HistoryDocumentary")

    tags = [t.strip() for t in tags_str.split(",")][:20]
    full_description = f"{description}\n\n{hashtags}\n\n© HistoriCove TV — Unlocking the Secrets of Time"

    body = {
        "snippet": {
            "title": title[:100],
            "description": full_description[:5000],
            "tags": tags,
            "categoryId": "27",  # Education
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024*1024*5
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"✅ Uploaded! https://www.youtube.com/watch?v={video_id}")
    return video_id

# ─── MAIN PIPELINE ────────────────────────────────────────────────────────────
def cleanup():
    """Remove temporary files to save space"""
    for f in OUTPUT_DIR.glob("scene_*.mp4"):
        f.unlink(missing_ok=True)
    for f in OUTPUT_DIR.glob("audio_*.mp3"):
        f.unlink(missing_ok=True)
    for f in OUTPUT_DIR.glob("scene_*.jpg"):
        f.unlink(missing_ok=True)
    for f in ["title_card.mp4", "concat_list.txt"]:
        (OUTPUT_DIR / f).unlink(missing_ok=True)

def main():
    print("=" * 60)
    print("🏛️  HistoriCove TV — Daily Video Pipeline")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # Step 1: Story
        story_data = generate_story()

        # Step 2: Images
        image_paths = fetch_images(story_data)

        # Step 3: Audio
        audio_paths = generate_audio(story_data)

        # Align: use only scenes that have both image and audio
        min_scenes = min(len(image_paths), len(audio_paths))
        image_paths = image_paths[:min_scenes]
        audio_paths = audio_paths[:min_scenes]
        story_data["scenes"] = story_data["scenes"][:min_scenes]

        # Step 4: Build video
        final_video = build_video(image_paths, audio_paths, story_data)

        # Step 5: Upload
        video_id = upload_to_youtube(final_video, story_data)

        # Cleanup
        cleanup()

        print("\n" + "=" * 60)
        print("✅ Pipeline complete!")
        print(f"   Video: https://www.youtube.com/watch?v={video_id}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
