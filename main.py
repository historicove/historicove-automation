import os
import json
import time
import random
import requests
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

GEMINI_API_KEY     = os.environ["GEMINI_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
PEXELS_API_KEY     = os.environ["PEXELS_API_KEY"]

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

HISTORICAL_FIGURES = [
    "Alexander the Great", "Cleopatra", "Julius Caesar", "Genghis Khan",
    "Napoleon Bonaparte", "Saladin", "Attila the Hun", "Hannibal Barca",
    "Cyrus the Great", "Ramesses II", "Suleiman the Magnificent",
    "Tamerlane", "Richard the Lionheart", "Ashoka the Great",
    "Charlemagne", "Vlad the Impaler", "Peter the Great",
    "Joan of Arc", "Marcus Aurelius", "Spartacus", "Mehmed II"
]

def generate_story():
    print("Generating historical story with Gemini...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")
    figure = random.choice(HISTORICAL_FIGURES)
    today = datetime.now().strftime("%B %d, %Y")
    prompt = f"""You are a master historical storyteller for HistoriCove TV on YouTube.
Write a dramatic cinematic narrative about: {figure}

Write exactly 10 scenes. Format EXACTLY like this:

---SCENE---
SCENE_NUMBER: 1
SCENE_TITLE: The Rise of a Legend
NARRATION: [150-200 words of vivid emotional storytelling]
IMAGE_SEARCH: ancient warrior battle sword
---END_SCENE---

After all scenes add:
---META---
VIDEO_TITLE: [SEO title max 60 chars with person name]
VIDEO_DESCRIPTION: [300 word description with keywords]
VIDEO_TAGS: history,documentary,ancient history,{figure},[16 more tags]
VIDEO_HASHTAGS: #HistoryDocumentary #AncientHistory #HistoriCoveTV #History
---END_META---"""

    response = model.generate_content(prompt)
    raw = response.text
    scenes = []
    for block in raw.split("---SCENE---")[1:]:
        block = block.split("---END_SCENE---")[0].strip()
        scene = {}
        narration_lines = []
        in_narration = False
        for line in block.split("\n"):
            if line.startswith("SCENE_NUMBER:"):
                scene["number"] = line.replace("SCENE_NUMBER:", "").strip()
                in_narration = False
            elif line.startswith("SCENE_TITLE:"):
                scene["title"] = line.replace("SCENE_TITLE:", "").strip()
                in_narration = False
            elif line.startswith("NARRATION:"):
                narration_lines = [line.replace("NARRATION:", "").strip()]
                in_narration = True
            elif line.startswith("IMAGE_SEARCH:"):
                scene["image_search"] = line.replace("IMAGE_SEARCH:", "").strip()
                in_narration = False
            elif in_narration and line.strip():
                narration_lines.append(line.strip())
        if narration_lines:
            scene["narration"] = " ".join(narration_lines)
        if scene:
            scenes.append(scene)

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

    print(f"Story generated: {len(scenes)} scenes about {figure}")
    return {"figure": figure, "scenes": scenes, "meta": meta}

def fetch_images(story_data):
    print("Fetching images from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    image_paths = []
    for i, scene in enumerate(story_data["scenes"]):
        query = scene.get("image_search", "ancient history")
        try:
            resp = requests.get(
                f"https://api.pexels.com/v1/search?query={query}&per_page=5&orientation=landscape",
                headers=headers, timeout=15)
            photos = resp.json().get("photos", [])
            if not photos:
                resp = requests.get(
                    "https://api.pexels.com/v1/search?query=ancient ruins history&per_page=5&orientation=landscape",
                    headers=headers, timeout=15)
                photos = resp.json().get("photos", [])
            if photos:
                img_url = random.choice(photos[:3])["src"]["large2x"]
                img_path = OUTPUT_DIR / f"scene_{i+1:02d}.jpg"
                with open(img_path, "wb") as f:
                    f.write(requests.get(img_url, timeout=30).content)
                image_paths.append(str(img_path))
                print(f"Scene {i+1}: image ok")
            elif image_paths:
                image_paths.append(image_paths[-1])
        except Exception as e:
            print(f"Scene {i+1} image error: {e}")
            if image_paths:
                image_paths.append(image_paths[-1])
        time.sleep(0.5)
    return image_paths

def generate_audio(story_data):
    print("Generating audio with ElevenLabs...")
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio_paths = []
    for i, scene in enumerate(story_data["scenes"]):
        narration = scene.get("narration", "")
        if not narration:
            continue
        try:
            audio = client.text_to_speech.convert(
                voice_id="pNInz6obpgDQGcFmaJgB",
                text=narration,
                model_id="eleven_multilingual_v2",
                voice_settings={"stability": 0.5, "similarity_boost": 0.8}
            )
            audio_path = OUTPUT_DIR / f"audio_{i+1:02d}.mp3"
            save(audio, str(audio_path))
            audio_paths.append(str(audio_path))
            print(f"Scene {i+1}: audio ok")
            time.sleep(1)
        except Exception as e:
            print(f"Scene {i+1} audio error: {e}")
    return audio_paths

def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 30.0

def build_video(image_paths, audio_paths, story_data):
    print("Building video with FFmpeg...")
    scene_videos = []
    for i, (img, aud) in enumerate(zip(image_paths, audio_paths)):
        if not os.path.exists(img) or not os.path.exists(aud):
            continue
        duration = get_duration(aud)
        out = str(OUTPUT_DIR / f"scene_{i+1:02d}.mp4")
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img, "-i", aud,
            "-filter_complex",
            f"[0:v]zoompan=z='min(zoom+0.0008,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration*25)}:s=1920x1080:fps=25,format=yuv420p[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-t", str(duration + 0.5), out
        ]
        if subprocess.run(cmd, capture_output=True).returncode == 0:
            scene_videos.append(out)
            print(f"Scene {i+1}: video ok ({duration:.1f}s)")

    if not scene_videos:
        raise Exception("No scene videos created!")

    concat_list = str(OUTPUT_DIR / "concat_list.txt")
    with open(concat_list, "w") as f:
        for v in scene_videos:
            f.write(f"file '{os.path.abspath(v)}'\n")

    final_video = str(OUTPUT_DIR / "final_video.mp4")
    result = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", "-b:a", "192k",
        final_video
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Concat failed: {result.stderr[-300:]}")
    duration = get_duration(final_video)
    print(f"Final video: {duration/60:.1f} minutes")
    return final_video

def get_youtube_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_path, story_data):
    print("Uploading to YouTube...")
    youtube = get_youtube_service()
    meta = story_data["meta"]
    title = meta.get("title", f"The Story of {story_data['figure']}")
    description = meta.get("description", "")
    tags = [t.strip() for t in meta.get("tags", "history,documentary").split(",")][:20]
    hashtags = meta.get("hashtags", "#HistoryDocumentary")
    full_desc = f"{description}\n\n{hashtags}\n\n© HistoriCove TV"

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:100],
                "description": full_desc[:5000],
                "tags": tags,
                "categoryId": "27",
                "defaultLanguage": "en",
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        },
        media_body=MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload: {int(status.progress()*100)}%")
    video_id = response["id"]
    print(f"Uploaded: https://www.youtube.com/watch?v={video_id}")
    return video_id

def cleanup():
    for pattern in ["scene_*.mp4", "audio_*.mp3", "scene_*.jpg", "concat_list.txt"]:
        for f in OUTPUT_DIR.glob(pattern):
            f.unlink(missing_ok=True)

def main():
    print("=" * 50)
    print("HistoriCove TV — Daily Video Pipeline")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    try:
        story_data = generate_story()
        image_paths = fetch_images(story_data)
        audio_paths = generate_audio(story_data)
        n = min(len(image_paths), len(audio_paths))
        final_video = build_video(image_paths[:n], audio_paths[:n], story_data)
        video_id = upload_to_youtube(final_video, story_data)
        cleanup()
        print(f"\nDone! https://www.youtube.com/watch?v={video_id}")
    except Exception as e:
        print(f"\nFailed: {e}")
        raise

if __name__ == "__main__":
    main()
