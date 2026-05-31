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
    # ── Conquerors & Warriors ──────────────────────────────────────────
    "Alexander the Great's final days and mysterious death in Babylon",
    "Genghis Khan: The shepherd boy who conquered half the world",
    "Hannibal Barca's impossible crossing of the Alps with war elephants",
    "Attila the Hun: The scourge of God who made Rome tremble",
    "Saladin and the recapture of Jerusalem from the Crusaders",
    "Tamerlane: The lame conqueror who built pyramids of skulls",
    "Julius Caesar's assassination on the Ides of March",
    "Napoleon Bonaparte's catastrophic invasion of Russia",
    "Spartacus: The slave gladiator who almost destroyed Rome",
    "Boudicca: The warrior queen who burned Roman London to ashes",
    "Richard the Lionheart: The crusader king who barely knew England",
    "Khalid ibn al-Walid: The undefeated sword of Islam",
    "Sun Tzu: The mysterious general who wrote the Art of War",
    "Shaka Zulu: The warrior king who revolutionized African warfare",
    "El Cid: Spain's greatest warrior and his life after death",

    # ── Kings, Queens & Emperors ───────────────────────────────────────
    "Cleopatra: The last pharaoh and her battle to save Egypt",
    "Catherine the Great: The German princess who became Russia's empress",
    "Ivan the Terrible: Russia's most brutal and brilliant tsar",
    "Peter the Great: The giant tsar who dragged Russia into modernity",
    "Cyrus the Great: The shepherd son who built history's first empire",
    "Ramesses II: The pharaoh who turned his greatest defeat into victory",
    "Hatshepsut: The female pharaoh who erased himself from history",
    "Ashoka: The warrior emperor who chose peace after a river of blood",
    "Henry VIII: The king who broke with God to break his marriages",
    "Elizabeth I: The virgin queen who defeated the Spanish Armada",
    "Mary Queen of Scots: The queen who died on her cousin's orders",
    "Louis XIV: The Sun King who built the most extravagant court in history",
    "Nero: The emperor who fiddled while Rome burned",
    "Caligula: Rome's most depraved emperor and his shocking reign",
    "Qin Shi Huang: The first emperor who unified China and feared death",
    "Akbar the Great: The Mughal emperor who built an empire of tolerance",
    "Frederick the Great: The philosopher king who made Prussia a superpower",
    "Maria Theresa: The empress who ruled an empire and raised 16 children",
    "Vlad the Impaler: The real Dracula and his forest of death",

    # ── Political Giants of the Modern Era ────────────────────────────
    "Winston Churchill: The man who refused to surrender when all hope was lost",
    "Joseph Stalin: The peasant boy who became history's most paranoid dictator",
    "Adolf Hitler: The rise and fall of the most evil regime in history",
    "Abraham Lincoln: From log cabin to leading America through its bloodiest war",
    "Mao Zedong: The poet revolutionary who starved millions in the name of progress",
    "Franklin D. Roosevelt: The paralyzed president who saved democracy",
    "John F. Kennedy: The assassination that changed America forever",
    "Mahatma Gandhi: The lawyer who brought down an empire without firing a shot",
    "Nelson Mandela: 27 years in prison and still became president",
    "Vladimir Lenin: The exile who returned to start the Russian Revolution",
    "Leon Trotsky: The revolutionary who was hunted to the ends of the earth",
    "Benito Mussolini: The journalist who became a dictator and died on a lamppost",
    "Fidel Castro: The lawyer who outsmarted the CIA for 50 years",
    "Che Guevara: The doctor who became the world's most famous revolutionary",
    "Mao's Cultural Revolution: When China turned on its own intellectuals",
    "The last days of Adolf Hitler in the Berlin bunker",
    "Richard Nixon: The president who bugged himself out of power",
    "J. Edgar Hoover: The man who blackmailed every president for 48 years",

    # ── Great Wars & Battles ───────────────────────────────────────────
    "The Battle of Thermopylae: 300 Spartans against a million Persians",
    "The fall of Constantinople: The day the Roman Empire finally died",
    "The D-Day invasion: The largest military operation in human history",
    "The Battle of Stalingrad: The bloodiest battle in the history of warfare",
    "The Battle of Waterloo: Napoleon's final defeat and exile",
    "The Mongol invasion of Baghdad: The day the Islamic Golden Age ended",
    "The Battle of Marathon: How 10,000 Athenians stopped the Persian Empire",
    "The Siege of Masada: 960 Jews who chose death over Roman slavery",
    "World War I: The assassination that killed 20 million people",
    "The atomic bombing of Hiroshima: The day the world changed forever",
    "The fall of the Berlin Wall: How one press conference ended the Cold War",
    "The Cuban Missile Crisis: 13 days that almost ended the world",
    "The Vietnam War: America's most controversial and costly defeat",
    "The Six-Day War: How Israel won a war in less than a week",

    # ── Ancient Civilizations ──────────────────────────────────────────
    "The mystery of the Egyptian pyramids: How and why they were really built",
    "Pompeii: The city that was frozen in time by a volcano",
    "The lost city of Troy: Myth or reality?",
    "Ancient Rome: How a small village became the greatest empire on earth",
    "The Library of Alexandria: What was really lost when it burned",
    "The Maya civilization: Why did millions of people simply vanish?",
    "Sparta vs Athens: The war that defined Western civilization",
    "The Persian Empire: The most tolerant superpower of the ancient world",
    "Ancient Egypt's Book of the Dead: The real beliefs about the afterlife",
    "Carthage: The great civilization that Rome erased from history",
    "The Vikings: Raiders, traders and explorers who reached America first",
    "The Aztec Empire: The shocking truth behind human sacrifice",
    "The Inca Empire: How Spain destroyed the greatest civilization in the Americas",
    "Babylon: The world's first great city and its legendary hanging gardens",

    # ── Mysterious & Controversial Figures ────────────────────────────
    "Rasputin: The mad monk who could not be killed",
    "Nikola Tesla: The genius who was robbed, mocked and forgotten",
    "Jack the Ripper: The unsolved murders that shocked Victorian London",
    "Mata Hari: The spy dancer executed for secrets she may not have known",
    "Anastasia Romanov: The princess who may have escaped the firing squad",
    "Howard Hughes: The billionaire who went from playboy to paranoid recluse",
    "Amelia Earhart: The world's most famous disappearance over the Pacific",
    "D.B. Cooper: The only unsolved skyjacking in American history",
    "The Romanov execution: The night Russia's royal family was murdered",
    "The Zodiac Killer: The serial killer who taunted police and was never caught",
    "Grigori Rasputin's impossible death: Poisoned, shot and drowned",
    "The Dyatlov Pass incident: Nine hikers who died in unexplained terror",
    "Nostradamus: The prophet who predicted the future or just wrote poetry?",
    "Nikola Tesla vs Thomas Edison: The war of currents that lit the world",

    # ── Zheng He & Explorers ───────────────────────────────────────────
    "Zheng He: The Chinese admiral who explored the world before Columbus",
    "Christopher Columbus: The man who discovered America by accident",
    "Marco Polo: Did he really go to China or was it all a lie?",
    "Ferdinand Magellan: The first man to circumnavigate the globe — who died halfway",
    "Vasco da Gama: The explorer who opened the sea route to India and destroyed it",
]

def claude_request(prompt, max_tokens=3000, retries=3):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-sonnet-4-5",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }
    for attempt in range(retries):
        try:
            resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            return resp.json()["content"][0]["text"].strip()
        except Exception as e:
            print("   Claude attempt " + str(attempt+1) + " failed: " + str(e))
            if attempt < retries - 1:
                time.sleep(5)
    raise ValueError("Claude API failed after " + str(retries) + " attempts")

def parse_json(text):
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except:
            # Try to fix common JSON issues
            cleaned = text[start:end]
            # Remove trailing commas
            import re
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            try:
                return json.loads(cleaned)
            except:
                pass
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
    # Step 1: Get title, tags, thumbnail + short narrations
    p1 = ('Write a YouTube historical documentary script about: "' + topic + '"\n\n'
          'Return ONLY this JSON (keep narrations under 50 words each as placeholders):\n'
          '{"title":"Dramatic title under 60 chars","description":"SEO description 200 words","tags":["history","documentary","ancient","war","empire","conquest","kings","battle","legend","mystery","untold","facts","historical","epic","civilization","rulers","warriors","secrets","power","death"],"thumbnail_text":"6 SHOCKING WORDS CAPS","thumbnail_subtext":"THE UNTOLD STORY","scenes":['
          '{"id":1,"title":"HOOK","narration":"placeholder"},'
          '{"id":2,"title":"THE WORLD","narration":"placeholder"},'
          '{"id":3,"title":"THE RISE","narration":"placeholder"},'
          '{"id":4,"title":"THE CONFLICT","narration":"placeholder"},'
          '{"id":5,"title":"THE CLIMAX","narration":"placeholder"},'
          '{"id":6,"title":"THE LEGACY","narration":"placeholder"}]}'
          '\nReturn ONLY raw JSON. No markdown. No backticks. No explanation. Start with { and end with }.')

    script = None
    for attempt in range(3):
        text1 = claude_request(p1, max_tokens=800)
        script = parse_json(text1)
        if script:
            break
        print("   JSON parse attempt " + str(attempt+1) + " failed, retrying...")
        time.sleep(3)
    if not script:
        raise ValueError("Failed to parse script JSON after 3 attempts")
    print("   Script: " + script["title"])

    # Step 1b: Get full narrations for each scene separately
    scene_titles = ["HOOK", "THE WORLD", "THE RISE", "THE CONFLICT", "THE CLIMAX", "THE LEGACY"]
    scene_instructions = [
        "Write in SIMPLE conversational English that anyone can understand. No complex words. Start with the most shocking moment - drop viewer into action. Use short punchy sentences. Make it feel like a friend telling an amazing story. Present tense for drama.",
        "Write in SIMPLE conversational English. Paint the world like you are describing it to a friend. Short sentences. Easy words. Make it vivid and exciting.",
        "Write in SIMPLE conversational English. Build tension naturally. Short sentences. Easy to follow. Keep viewer hooked with suspense.",
        "Write in SIMPLE conversational English. Describe the battle or conflict like an exciting movie. Easy words. Short punchy sentences. Maximum drama without complex language.",
        "Write in SIMPLE conversational English. The peak moment - make it feel real and immediate. Short sentences. Easy words. Maximum emotional impact.",
        "Write in SIMPLE conversational English. Why does this matter today? Connect to modern life simply. End with a thought-provoking question anyone can understand. Ask viewers to subscribe naturally."
    ]

    for i, scene in enumerate(script["scenes"]):
        p_narr = ('Write a 200-word narration for a YouTube historical documentary.\n'
                  'Topic: "' + topic + '"\n'
                  'Scene: "' + scene_titles[i] + '"\n'
                  'Style: ' + scene_instructions[i] + '\n\n'
                  'IMPORTANT RULES:\n'
                  '- Use SIMPLE everyday English words\n'
                  '- Short sentences (max 15 words each)\n'
                  '- Like talking to a friend, not writing a book\n'
                  '- No complex historical jargon\n'
                  '- Make it exciting and easy to follow\n'
                  '- Exactly 200 words\n\n'
                  'Write ONLY the narration text. No JSON. No titles. Just the narration.')
        narr_text = claude_request(p_narr, max_tokens=600)
        scene["narration"] = narr_text.strip()
        print("   Narration " + str(i+1) + ": " + str(len(narr_text.split())) + " words")
        time.sleep(1)

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

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

def image_to_video_replicate(image_path, motion_prompt, output_path):
    """Use Replicate Wan 2.7 for image to video - free credits available"""
    try:
        # Convert image to base64 data URL
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        img_data_url = "data:image/jpeg;base64," + img_b64

        headers = {
            "Authorization": "Bearer " + REPLICATE_API_TOKEN,
            "Content-Type": "application/json",
            "Prefer": "wait"
        }

        # Use Wan 2.5 image to video model
        payload = {
            "version": "wan-ai/wan2.5-i2v-480p",
            "input": {
                "image": img_data_url,
                "prompt": motion_prompt + " Cinematic. Historically authentic. Epic atmosphere.",
                "negative_prompt": "modern, text, watermark, distortion, low quality",
                "num_frames": 81,
                "fps": 16,
                "guidance_scale": 5.0,
                "num_inference_steps": 30
            }
        }

        resp = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=payload,
            timeout=300
        )

        if resp.status_code not in [200, 201]:
            print("      Replicate error: " + str(resp.status_code))
            return False

        result = resp.json()
        prediction_id = result.get("id")

        # If not completed yet, poll
        if result.get("status") not in ["succeeded", "failed"]:
            for _ in range(40):
                time.sleep(10)
                poll = requests.get(
                    "https://api.replicate.com/v1/predictions/" + prediction_id,
                    headers=headers
                )
                result = poll.json()
                status = result.get("status", "")
                print("      Replicate status: " + status)
                if status == "succeeded":
                    break
                elif status == "failed":
                    print("      Replicate failed: " + str(result.get("error")))
                    return False

        output = result.get("output")
        if output:
            video_url = output if isinstance(output, str) else output[0]
            vr = requests.get(video_url, timeout=60)
            with open(output_path, "wb") as f:
                f.write(vr.content)
            return True

    except Exception as e:
        print("      Replicate exception: " + str(e))

    return False

def image_to_video_kling(image_path, motion_prompt, output_path):
    """Kling video generation as fallback"""
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

def ken_burns_video(image_path, output_path, shot_num, duration=5):
    """Create 5-second cinematic video - 18 unique effects, no repeat"""
    frames = duration * 25  # 125 frames at 25fps
    effects = [
        # Zoom in slow
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        # Pan right
        f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),0,min(x+2,iw*(1-1/zoom)))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        # Zoom out slow
        f"scale=8000:-1,zoompan=z='if(lte(on,1),1.5,max(1.001,zoom-0.001))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        # Pan left
        f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),iw*0.3,max(0,x-1.5))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        # Pan up
        f"scale=8000:-1,zoompan=z='1.3':x='iw/2-(iw/zoom/2)':y='if(lte(on,1),ih*0.3,max(0,y-1))':d={frames}:s=1920x1080",
        # Pan down
        f"scale=8000:-1,zoompan=z='1.3':x='iw/2-(iw/zoom/2)':y='if(lte(on,1),0,min(y+1,ih*(1-1/zoom)))':d={frames}:s=1920x1080",
        # Zoom in top-left
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='0':y='0':d={frames}:s=1920x1080",
        # Zoom in top-right
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='iw*(1-1/zoom)':y='0':d={frames}:s=1920x1080",
        # Zoom in bottom-left
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='0':y='ih*(1-1/zoom)':d={frames}:s=1920x1080",
        # Zoom in bottom-right
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='iw*(1-1/zoom)':y='ih*(1-1/zoom)':d={frames}:s=1920x1080",
        # Diagonal pan top-left to bottom-right
        f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),0,min(x+1.5,iw*(1-1/zoom)))':y='if(lte(on,1),0,min(y+1,ih*(1-1/zoom)))':d={frames}:s=1920x1080",
        # Diagonal pan top-right to bottom-left
        f"scale=8000:-1,zoompan=z='1.3':x='if(lte(on,1),iw*0.3,max(0,x-1.5))':y='if(lte(on,1),0,min(y+1,ih*(1-1/zoom)))':d={frames}:s=1920x1080",
        # Slow zoom in center with slight pan right
        f"scale=8000:-1,zoompan=z='min(zoom+0.0004,1.3)':x='if(lte(on,1),iw/2-(iw/zoom/2),min(x+0.5,iw*(1-1/zoom)))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        # Slow zoom out with pan left
        f"scale=8000:-1,zoompan=z='if(lte(on,1),1.4,max(1.001,zoom-0.0008))':x='if(lte(on,1),iw*0.2,max(0,x-0.5))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        # Zoom in from bottom center
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='iw/2-(iw/zoom/2)':y='ih*(1-1/zoom)':d={frames}:s=1920x1080",
        # Zoom in from top center
        f"scale=8000:-1,zoompan=z='min(zoom+0.0006,1.4)':x='iw/2-(iw/zoom/2)':y='0':d={frames}:s=1920x1080",
        # Wide slow pan left to right
        f"scale=8000:-1,zoompan=z='1.2':x='if(lte(on,1),0,min(x+1.2,iw*(1-1/zoom)))':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
        # Dramatic zoom in fast
        f"scale=8000:-1,zoompan=z='min(zoom+0.001,1.6)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080",
    ]

    effect = effects[shot_num % 18]
    color = "eq=contrast=1.08:brightness=-0.03:saturation=0.85"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-t", str(duration),
        "-vf", effect + "," + color + ",format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-r", "25", "-an",
        str(output_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("      Ken Burns error: " + r.stderr[-100:])
    return r.returncode == 0

def search_pexels_video(query, output_path):
    """Search and download relevant video from Pexels"""
    try:
        # Map historical keywords to Pexels-friendly search terms
        keyword_map = {
            "battle": "ancient battle war soldiers",
            "war": "ancient warriors soldiers",
            "king": "medieval castle throne",
            "emperor": "ancient palace throne room",
            "army": "soldiers marching medieval",
            "sword": "medieval sword warrior",
            "castle": "medieval castle fortress",
            "rome": "ancient rome columns",
            "egypt": "ancient egypt desert pyramid",
            "horse": "horses galloping epic",
            "fire": "fire flames dramatic",
            "crowd": "medieval crowd people",
            "night": "night fire torches dark",
            "mountain": "epic mountain landscape",
            "desert": "desert landscape dramatic",
            "ocean": "ocean waves dramatic",
            "death": "dramatic dark atmospheric",
            "victory": "epic celebration crowd",
            "throne": "throne room palace medieval",
            "prayer": "ancient religious ceremony",
        }

        # Find best keyword match
        query_lower = query.lower()
        search_term = "ancient historical cinematic"
        for key, value in keyword_map.items():
            if key in query_lower:
                search_term = value
                break

        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": search_term,
            "per_page": 10,
            "orientation": "landscape",
            "size": "medium"
        }
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=30
        )

        if resp.status_code != 200:
            return False

        videos = resp.json().get("videos", [])
        if not videos:
            # Try generic search
            params["query"] = "cinematic nature landscape epic"
            resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
            videos = resp.json().get("videos", [])

        if not videos:
            return False

        # Pick random video from top 5
        video = random.choice(videos[:5])

        # Get HD video file
        video_files = video.get("video_files", [])
        # Sort by resolution and pick best
        hd_files = [f for f in video_files if f.get("width", 0) >= 1280]
        if not hd_files:
            hd_files = video_files

        if not hd_files:
            return False

        best_file = sorted(hd_files, key=lambda x: x.get("width", 0), reverse=True)[0]
        video_url = best_file.get("link")

        if not video_url:
            return False

        # Download video
        vr = requests.get(video_url, timeout=60, stream=True)
        with open(output_path, "wb") as f:
            for chunk in vr.iter_content(chunk_size=8192):
                f.write(chunk)

        print("      ✅ Pexels video: " + search_term)
        return True

    except Exception as e:
        print("      Pexels video error: " + str(e))
        return False

def trim_video_to_duration(input_path, output_path, duration=5):
    """Trim or loop video to exact duration"""
    vid_dur = get_duration(input_path)

    if vid_dur >= duration:
        # Trim to duration
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            str(output_path)
        ]
    else:
        # Loop to duration
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", str(input_path),
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            str(output_path)
        ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0

def image_to_video(image_path, motion_prompt, output_path, shot_num=0):
    """Create cinematic video from image using Ken Burns - each shot has different effect"""
    return ken_burns_video(image_path, output_path, shot_num)

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
    # Create title card WITH silent audio so concat works properly
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(ti),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-t", "4",
        "-vf", "fade=in:0:25,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-r", "25", "-shortest",
        str(tv)
    ], capture_output=True)
    return tv

def merge_final(scene_videos, output_path):
    print("Merging " + str(len(scene_videos)) + " scenes...")

    # First verify each scene has audio
    for i, vp in enumerate(scene_videos):
        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_streams",
            "-select_streams", "a", str(vp)
        ], capture_output=True, text=True)
        has_audio = "codec_type=audio" in probe.stdout
        print("   Scene " + str(i) + " audio: " + ("✅" if has_audio else "❌ MISSING"))

    cf = OUTPUT_DIR / "final_concat.txt"
    with open(cf, "w") as f:
        for vp in scene_videos:
            f.write("file '" + str(Path(vp).absolute()) + "'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(cf),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        size = Path(output_path).stat().st_size / (1024*1024)
        print("   Final video: " + str(round(size,1)) + " MB")
        # Verify final audio
        probe = subprocess.run([
            "ffprobe", "-v", "quiet", "-show_streams",
            "-select_streams", "a", str(output_path)
        ], capture_output=True, text=True)
        if "codec_type=audio" in probe.stdout:
            print("   ✅ Audio confirmed in final video!")
        else:
            print("   ❌ No audio in final video!")
        return True
    print("   Merge failed: " + r.stderr[-300:])
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

    # NO title card - start directly with HOOK scene for maximum impact

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

            # Create 5-second Ken Burns video from image
            kb_ok = ken_burns_video(img_path, vid_path, j)
            if kb_ok:
                shot_videos.append(vid_path)
                print("  Shot " + shot_id + " done")
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
