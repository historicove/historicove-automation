import os, json, time, random, requests, subprocess, jwt, base64
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]
ELEVENLABS_API_KEY  = os.environ["ELEVENLABS_API_KEY"]
KLING_ACCESS_KEY    = os.environ["KLING_ACCESS_KEY"]
KLING_SECRET_KEY    = os.environ["KLING_SECRET_KEY"]
PEXELS_API_KEY      = os.environ.get("PEXELS_API_KEY", "")
ELEVENLABS_VOICE_ID = "JJCR1UICgHnHljtvu5uF"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

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
    "Cyrus the Great: The shepherd son who built history's first empire",
    "Cleopatra: The last pharaoh and her battle to save Egypt",
    "Catherine the Great: The German princess who became Russia's empress",
    "Joan of Arc: The peasant girl who changed the course of history",
    "The Battle of Thermopylae: 300 Spartans against a million Persians",
    "The fall of Constantinople: The day the Roman Empire finally died",
    "Vlad the Impaler: The real Dracula and his forest of death",
    "Boudicca: The warrior queen who burned Roman London to ashes",
    "Spartacus: The slave gladiator who almost destroyed Rome",
    "Ramesses II: The pharaoh who turned his greatest defeat into victory",
    "Peter the Great: The giant tsar who dragged Russia into modernity",
    "Ashoka: The warrior emperor who chose peace after a river of blood",
    "Hatshepsut: The female pharaoh who erased herself from history",
    "Zheng He: The Chinese admiral who explored the world before Columbus",
]

def claude_request(prompt, max_tokens=3000):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-opus-4-5",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()

def parse_json(text):
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return None

def parse_json_array(text):
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return None

def fallback_shots(scene_id, topic, scene_title):
    moves = ["Slow push forward.", "Slow pan left.", "Camera rises.", "Slow zoom in.",
             "Gentle drift right.", "Pull back reveal.", "Sweeping pan.", "Push into scene.",
             "Slow orbit.", "Wide reveal.", "Fast push.", "Slow circle.", "Rise up.",
             "Drift left.", "Push toward.", "Pull away.", "Slow rise.", "Epic wide."]
    return [
        {"id": str(scene_id) + "-" + str(k+1).zfill(2),
         "img": "Photorealistic oil painting. " + topic + " - " + scene_title + " scene " + str(k+1) + ". Dramatic Rembrandt lighting. Authentic historical costumes. Epic atmosphere. 16:9.",
         "mov": moves[k % 18]}
        for k in range(18)
    ]

def generate_script():
    print("📜 Generating script...")
    topic = random.choice(TOPICS)
    print("   Topic: " + topic)

    # Step 1: Story + narrations
    p1 = ('Write a YouTube historical documentary script about: "' + topic + '"\n\n'
          'Return ONLY this JSON:\n'
          '{"title":"Dramatic title under 60 chars","description":"SEO description 200 words","tags":["history","documentary","ancient","war","empire","conquest","kings","battle","legend","mystery","untold","facts","historical","epic","civilization","rulers","warriors","secrets","power","death"],"thumbnail_text":"6 SHOCKING WORDS CAPS","thumbnail_subtext":"THE UNTOLD STORY","scenes":['
          '{"id":1,"title":"HOOK","narration":"90 words. Start mid-action. Most shocking moment. Present tense."},'
          '{"id":2,"title":"THE WORLD","narration":"90 words. Paint the world. Show the stakes."},'
          '{"id":3,"title":"THE RISE","narration":"90 words. Turning point. Rising tension. Cliffhanger."},'
          '{"id":4,"title":"THE CONFLICT","narration":"90 words. Maximum drama. Battle or betrayal."},'
          '{"id":5,"title":"THE CLIMAX","narration":"90 words. Peak moment. Decision that changed history."},'
          '{"id":6,"title":"THE LEGACY","narration":"90 words. Why this matters today. Subscribe CTA."}]}'
          '\nReturn ONLY JSON. No markdown.')

    text1 = claude_request(p1, max_tokens=2000)
    script = parse_json(text1)
    if not script:
        raise ValueError("Failed to parse script JSON")
    print("   Script: " + script["title"])

    # Step 2: 18 shots per scene
    for scene in script["scenes"]:
        sid = str(scene["id"])
        stitle = scene["title"]
        snarr = scene["narration"][:80]

        p2 = ('Generate exactly 18 unique shot descriptions for a historical documentary.\n'
              'Topic: "' + topic + '"\n'
              'Scene: "' + stitle + '"\n'
              'Narration sample: "' + snarr + '"\n\n'
              'Return ONLY a JSON array of exactly 18 items.\n'
              'Each item: {"id":"' + sid + '-01","img":"Photorealistic oil painting. [specific unique scene]. Rembrandt lighting. Authentic period. 16:9.","mov":"[camera movement]"}\n'
              'IDs go from ' + sid + '-01 to ' + sid + '-18.\n'
              'All shots unique and specific to this topic and scene.\n'
              'Return ONLY the JSON array. No markdown.')

        try:
            text2 = claude_request(p2, max_tokens=3000)
            shots = parse_json_array(text2)
            if shots and len(shots) >= 6:
                scene["shots"] = shots[:18]
                print("   Scene " + sid + " shots: " + str(len(scene["shots"])))
            else:
                scene["shots"] = fallback_shots(scene["id"], topic, stitle)
                print("   Scene " + sid + " fallback shots")
        except Exception as e:
            print("   Scene " + sid + " error: " + str(e))
            scene["shots"] = fallback_shots(scene["id"], topic, stitle)

        time.sleep(2)

    total = sum(len(s.get("shots", [])) for s in script["scenes"])
    print("   Total shots: " + str(total))
    return script

def get_kling_token():
    payload = {"iss": KLING_ACCESS_KEY, "exp": int(time.time()) + 1800, "nbf": int(time.time()) - 5}
    return jwt.encode(payload, KLING_SECRET_KEY, algorithm="HS256")

def kling_headers():
    return {"Authorization": "Bearer " + get_kling_token(), "Content-Type": "application/json"}

def generate_image(prompt, filename):
    enhanced = "Photorealistic historical oil painting masterpiece. " + prompt + " Rembrandt chiaroscuro lighting. Museum quality. Ultra detailed authentic period costumes. NOT cartoon. NOT CGI. NOT modern."
    payload = {"model": "kling-v2-1", "prompt": enhanced, "negative_prompt": "cartoon, anime, CGI, modern, watermark, text, blurry, distorted, AI-looking", "aspect_ratio": "16:9", "n": 1}
    resp = requests.post("https://api.klingai.com/v1/images/generations", headers=kling_headers(), json=payload)
    if resp.status_code != 200:
        return fetch_pexels(prompt, filename)
    task_id = resp.json().get("data", {}).get("task_id")
    if not task_id:
        return fetch_pexels(prompt, filename)
    for _ in range(20):
        time.sleep(8)
        check = requests.get("https://api.klingai.com/v1/images/generations/" + task_id, headers=kling_headers())
        if check.status_code != 200:
            continue
        data = check.json().get("data", {})
        if data.get("task_status") == "succeed":
            imgs = data.get("task_result", {}).get("images", [])
            if imgs:
                r = requests.get(imgs[0]["url"], timeout=30)
                with open(filename, "wb") as f:
                    f.write(r.content)
                return True
        elif data.get("task_status") == "failed":
            return fetch_pexels(prompt, filename)
    return fetch_pexels(prompt, filename)

def fetch_pexels(prompt, filename):
    try:
        kw = prompt.split(".")[0][:50]
        h = {"Authorization": PEXELS_API_KEY}
        r = requests.get("https://api.pexels.com/v1/search", headers=h, params={"query": kw, "per_page": 3, "orientation": "landscape"})
        photos = r.json().get("photos", [])
        if photos:
            ir = requests.get(photos[0]["src"]["large2x"], timeout=30)
            with open(filename, "wb") as f:
                f.write(ir.content)
            return True
    except:
        pass
    return False

def image_to_video(image_path, motion_prompt, output_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "model_name": "kling-v2-master",
        "image": img_b64,
        "prompt": motion_prompt + " Cinematic. Historically authentic. No modern elements.",
        "negative_prompt": "shaky, fast motion, modern, text, watermark, distortion, flash",
        "cfg_scale": 0.5, "mode": "pro", "duration": "5", "aspect_ratio": "16:9"
    }
    resp = requests.post("https://api.klingai.com/v1/videos/image2video", headers=kling_headers(), json=payload)
    if resp.status_code != 200:
        return False
    task_id = resp.json().get("data", {}).get("task_id")
    if not task_id:
        return False
    for _ in range(24):
        time.sleep(15)
        check = requests.get("https://api.klingai.com/v1/videos/image2video/" + task_id, headers=kling_headers())
        if check.status_code != 200:
            continue
        data = check.json().get("data", {})
        if data.get("task_status") == "succeed":
            vids = data.get("task_result", {}).get("videos", [])
            if vids:
                vr = requests.get(vids[0]["url"], timeout=60)
                with open(output_path, "wb") as f:
                    f.write(vr.content)
                return True
        elif data.get("task_status") == "failed":
            return False
    return False

def generate_narration(text, filename):
    h = {"xi-api-key": ELEVENLABS_API_KEY.strip(), "Content-Type": "application/json"}
    d = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.40, "similarity_boost": 0.88, "style": 0.40, "use_speaker_boost": True}}
    r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/" + ELEVENLABS_VOICE_ID, headers=h, json=d, timeout=60)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            f.write(r.content)
        return True
    print("      ElevenLabs: " + str(r.status_code))
    return False

def get_duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0

def concat_shots(video_paths, output_path):
    cf = OUTPUT_DIR / ("concat_" + str(int(time.time())) + ".txt")
    with open(cf, "w") as f:
        for vp in video_paths:
            f.write("file '" + str(Path(vp).absolute()) + "'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cf), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(output_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    cf.unlink(missing_ok=True)
    return r.returncode == 0

def add_audio_to_scene(video_path, audio_path, output_path):
    vid_dur = get_duration(video_path)
    aud_dur = get_duration(audio_path)
    print("      Video: " + str(round(vid_dur, 1)) + "s | Audio: " + str(round(aud_dur, 1)) + "s")
    if vid_dur <= 0 or aud_dur <= 0:
        return False
    if vid_dur >= aud_dur:
        cmd = ["ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(aud_dur), str(output_path)]
    else:
        cmd = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(video_path), "-i", str(audio_path), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-t", str(aud_dur), str(output_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        print("      Audio added successfully")
        return True
    print("      Audio merge error: " + r.stderr[-100:])
    return False

def create_thumbnail(script, bg_path):
    print("Creating thumbnail...")
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (5, 5, 15))
    try:
        bg = Image.open(bg_path).convert("RGB")
        bg = bg.resize((W, H), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg).enhance(0.28)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=2))
        img.paste(bg, (0, 0))
    except:
        pass
    draw = ImageDraw.Draw(img)
    for x in range(W*3//4):
        alpha = int(150 * max(0, 1 - x/(W*3//4)))
        for y in range(H):
            r, g, b = img.getpixel((x, y))
            img.putpixel((x, y), (max(0,r-alpha//4), max(0,g-alpha//4), max(0,b-alpha//3)))
    draw.rectangle([0, 0, 12, H], fill=(220,25,25))
    draw.rectangle([20, H//2-2, W//2, H//2+2], fill=(220,180,40))
    try:
        fxl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 95)
        flg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
        fsm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except:
        fxl = flg = fsm = ImageFont.load_default()
    main = script.get("thumbnail_text", script["title"][:30]).upper()
    sub = script.get("thumbnail_subtext", "THE UNTOLD STORY").upper()
    words = main.split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > 14:
            lines.append(" ".join(cur[:-1]))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    y = H//2 - (len(lines)*105)//2
    for i, line in enumerate(lines):
        for sx, sy in [(4,4),(3,3),(2,2)]:
            draw.text((28+sx, y+sy), line, font=fxl, fill=(0,0,0))
        draw.text((28, y), line, font=fxl, fill=(255,220,30) if i==0 else (255,255,255))
        y += 105
    draw.text((30, y+13), sub, font=flg, fill=(0,0,0))
    draw.text((28, y+10), sub, font=flg, fill=(220,25,25))
    draw.rectangle([20, H-58, 280, H-15], fill=(180,15,15))
    draw.text((30, H-50), "HISTORICOVE TV", font=fsm, fill=(255,255,255))
    path = OUTPUT_DIR / "thumbnail.jpg"
    img.save(path, "JPEG", quality=95)
    print("   Thumbnail created")
    return path

def create_title_card(title):
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), (5, 5, 15))
    draw = ImageDraw.Draw(img)
    for i in range(0, W, 80): draw.line([(i,0),(i,H)], fill=(12,12,22), width=1)
    for j in range(0, H, 80): draw.line([(0,j),(W,j)], fill=(12,12,22), width=1)
    try:
        fc = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 82)
        fg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        fc = ft = fg = ImageFont.load_default()
    ch = "HISTORICOVE  TV"
    bbox = draw.textbbox((0,0), ch, font=fc)
    x = (W-(bbox[2]-bbox[0]))//2
    draw.text((x, H//2-100), ch, font=fc, fill=(140,140,160))
    draw.rectangle([W//2-280, H//2-55, W//2+280, H//2-51], fill=(200,20,20))
    words = title.upper().split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > 26:
            lines.append(" ".join(cur[:-1]))
            cur = [w]
    if cur: lines.append(" ".join(cur))
    y = H//2 - 20
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=ft)
        x = (W-(bbox[2]-bbox[0]))//2
        draw.text((x+3,y+3), line, font=ft, fill=(0,0,0))
        draw.text((x,y), line, font=ft, fill=(255,255,255))
        y += 90
    tag = "WHERE HISTORY COMES ALIVE"
    bbox = draw.textbbox((0,0), tag, font=fg)
    x = (W-(bbox[2]-bbox[0]))//2
    draw.text((x, y+15), tag, font=fg, fill=(180,20,20))
    ti = OUTPUT_DIR / "title_card.jpg"
    img.save(ti, "JPEG", quality=95)
    tv = OUTPUT_DIR / "title_card.mp4"
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(ti), "-t", "4", "-vf", "fade=in:0:25,format=yuv420p", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "25", "-an", str(tv)], capture_output=True)
    return tv

def merge_final(scene_videos, output_path):
    print("Merging " + str(len(scene_videos)) + " scenes...")
    cf = OUTPUT_DIR / "final_concat.txt"
    with open(cf, "w") as f:
        for vp in scene_videos:
            f.write("file '" + str(Path(vp).absolute()) + "'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cf), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        size = Path(output_path).stat().st_size / (1024*1024)
        print("   Final video: " + str(round(size,1)) + " MB")
        return True
    print("   Merge failed: " + r.stderr[-200:])
    return False

def upload_youtube(video_path, thumb_path, script):
    print("Uploading to YouTube...")
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
        print("No YouTube credentials!")
        return None
    youtube = build("youtube", "v3", credentials=creds)
    body = {"snippet": {"title": script["title"], "description": script["description"], "tags": script["tags"], "categoryId": "27", "defaultLanguage": "en"}, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print("   Upload: " + str(int(status.progress()*100)) + "%")
    vid_id = response["id"]
    print("   Uploaded: https://youtu.be/" + vid_id)
    try:
        youtube.thumbnails().set(videoId=vid_id, media_body=MediaFileUpload(str(thumb_path), mimetype="image/jpeg")).execute()
        print("   Thumbnail set")
    except Exception as e:
        print("   Thumbnail error: " + str(e))
    return vid_id

def main():
    print("=" * 65)
    print("HistoriCove TV - Professional Pipeline v5")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("18 shots x 5s = 90s video = NO REPEAT")
    print("=" * 65)

    script = generate_script()
    all_scene_videos = []
    first_image = None

    title_vid = create_title_card(script["title"])
    all_scene_videos.append(title_vid)

    for scene in script["scenes"]:
        print("\n" + "="*55)
        print("Scene " + str(scene["id"]) + "/6: " + scene["title"])
        print("="*55)

        shots = scene.get("shots", [])
        print("Shots: " + str(len(shots)))

        audio_path = OUTPUT_DIR / ("narration_" + str(scene["id"]).zfill(2) + ".mp3")
        print("Generating narration...")
        if not generate_narration(scene["narration"], audio_path):
            print("No narration - skipping scene")
            continue

        shot_videos = []
        for j, shot in enumerate(shots):
            shot_id = str(shot.get("id", str(scene["id"]) + "-" + str(j+1).zfill(2)))
            safe_id = shot_id.replace("-", "_")
            img_path = OUTPUT_DIR / ("img_" + safe_id + ".jpg")
            vid_path = OUTPUT_DIR / ("vid_" + safe_id + ".mp4")

            print("Shot " + shot_id + " (" + str(j+1) + "/" + str(len(shots)) + ")")

            img_ok = generate_image(shot["img"], img_path)
            if not img_ok:
                print("  No image")
                continue

            if first_image is None:
                first_image = img_path

            vid_ok = image_to_video(img_path, shot["mov"], vid_path)
            if vid_ok:
                shot_videos.append(vid_path)
                print("  Shot done")
            else:
                print("  Video failed")

        if not shot_videos:
            print("No shot videos for scene " + str(scene["id"]))
            continue

        scene_raw = OUTPUT_DIR / ("scene_" + str(scene["id"]).zfill(2) + "_raw.mp4")
        print("Joining " + str(len(shot_videos)) + " shots...")
        if not concat_shots(shot_videos, scene_raw):
            print("Concat failed")
            continue

        scene_final = OUTPUT_DIR / ("scene_" + str(scene["id"]).zfill(2) + "_final.mp4")
        print("Adding audio...")
        if add_audio_to_scene(scene_raw, audio_path, scene_final):
            all_scene_videos.append(scene_final)
            print("Scene " + str(scene["id"]) + " COMPLETE!")
        else:
            print("Audio failed for scene " + str(scene["id"]))

    if len(all_scene_videos) < 2:
        print("Not enough scenes. Aborting.")
        return

    bg = first_image or OUTPUT_DIR / "img_1_01.jpg"
    thumbnail = create_thumbnail(script, bg)

    final_video = OUTPUT_DIR / "final_video.mp4"
    if not merge_final(all_scene_videos, final_video):
        print("Final merge failed.")
        return

    vid_id = upload_youtube(final_video, thumbnail, script)

    print("\n" + "="*65)
    if vid_id:
        print("SUCCESS! https://youtu.be/" + vid_id)
        print("Title: " + script["title"])
    else:
        print("Video created but upload failed")
    print("="*65)

if __name__ == "__main__":
    main()
