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
SHOTS_PER_SCENE     = 18  # 18 shots × 5s = 90s = no repeat

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
    "Peter the Great: The giant tsar who dragged Russia into modernity",
    "Spartacus: The slave gladiator who almost destroyed Rome",
    "Ramesses II: The pharaoh who turned his greatest defeat into victory",
]

# ─── STEP 1: GENERATE SCRIPT ───────────────────────────────────────────────────
def generate_script():
    print("📜 Generating cinematic script with Claude...")
    topic = random.choice(TOPICS)
    print(f"   Topic: {topic}")

    prompt = f"""You are the world's best YouTube scriptwriter for epic historical documentaries.

Write a complete professional script about: "{topic}"

Each scene needs exactly 18 unique shot descriptions. Each shot = 1 image + 1 five-second video.
18 shots × 5 seconds = 90 seconds of video per scene (matching the narration length).

Return ONLY this valid JSON:
{{
  "title": "Dramatic YouTube title under 60 chars",
  "description": "SEO YouTube description 200 words with keywords",
  "tags": ["history","documentary","ancient","war","empire","conquest","kings","battle","legend","mystery","untold","facts","historical","epic","civilization","rulers","warriors","secrets","power","death"],
  "thumbnail_text": "6 SHOCKING WORDS ALL CAPS",
  "thumbnail_subtext": "THE UNTOLD STORY",
  "scenes": [
    {{
      "id": 1,
      "title": "HOOK",
      "narration": "90 words. Start mid-action. Most shocking moment. Present tense. No welcome. Drop viewer into the action immediately.",
      "shots": [
        {{"id":"1-01","img":"Photorealistic oil painting. [Scene specific to {topic}]. Dramatic Rembrandt lighting. Dark epic atmosphere. Authentic period costumes. 16:9.","mov":"Slow dramatic push forward. Dust in golden light."}},
        {{"id":"1-02","img":"Photorealistic oil painting. [Different angle, closer]. Faces showing terror or determination. Deep shadows.","mov":"Slow pan left revealing depth. Mist and atmosphere."}},
        {{"id":"1-03","img":"Photorealistic oil painting. [Wide epic shot]. Golden hour. Authentic historical landscape.","mov":"Camera rises slowly. Banners wave in wind."}},
        {{"id":"1-04","img":"Photorealistic oil painting. [Close-up of key object or weapon]. Ultra detailed. Dramatic side light.","mov":"Slow zoom into detail. Torchlight flickers."}},
        {{"id":"1-05","img":"Photorealistic oil painting. [Character in decisive moment]. Emotion on face. Period authentic.","mov":"Gentle camera drift. Shadows dance on walls."}},
        {{"id":"1-06","img":"Photorealistic oil painting. [Establishing wide shot of location]. Dramatic storm clouds. Epic scale.","mov":"Slow pull back reveal. Full scene unfolds."}},
        {{"id":"1-07","img":"Photorealistic oil painting. [Crowd or army scene]. Epic numbers. Authentic uniforms. Chaos.","mov":"Sweeping pan across the epic scene."}},
        {{"id":"1-08","img":"Photorealistic oil painting. [Architecture or throne room]. Grand interior. Torchlit. Authentic.","mov":"Slow push through grand space."}},
        {{"id":"1-09","img":"Photorealistic oil painting. [Key figure portrait]. Strong emotion. Museum quality. Dramatic.","mov":"Slow zoom on face. Intense close-up."}},
        {{"id":"1-10","img":"Photorealistic oil painting. [Action sequence]. Movement captured. Authentic weapons. Dramatic.","mov":"Dynamic but controlled camera movement."}},
        {{"id":"1-11","img":"Photorealistic oil painting. [Landscape at dusk]. Epic sky. Historical setting. Atmospheric.","mov":"Camera drifts across the landscape."}},
        {{"id":"1-12","img":"Photorealistic oil painting. [Symbol or important object]. Ultra detailed. Historical accuracy.","mov":"Slow orbit around the object."}},
        {{"id":"1-13","img":"Photorealistic oil painting. [Two figures in confrontation]. Tension. Dramatic lighting.","mov":"Slow push in. Rising tension."}},
        {{"id":"1-14","img":"Photorealistic oil painting. [Wide battle or crowd]. Scale of events. Epic. Authentic.","mov":"Slow rise revealing full scale."}},
        {{"id":"1-15","img":"Photorealistic oil painting. [Aftermath or consequence]. Somber. Emotional. Real.","mov":"Slow pull back. Weight of moment."}},
        {{"id":"1-16","img":"Photorealistic oil painting. [Night scene with fire or torches]. Dramatic. Dangerous.","mov":"Fire flickers. Shadows move."}},
        {{"id":"1-17","img":"Photorealistic oil painting. [Map or strategic view]. Overhead. Epic scale.","mov":"Slow zoom out revealing geography."}},
        {{"id":"1-18","img":"Photorealistic oil painting. [Final shot of hook - most dramatic]. Iconic. Powerful. Memorable.","mov":"Slow dramatic reveal. Epic finale."}}
      ]
    }},
    {{
      "id": 2,
      "title": "THE WORLD",
      "narration": "90 words. Paint the world vividly. Show the stakes. What made this unique?",
      "shots": [
        {{"id":"2-01","img":"Photorealistic oil painting. [World/civilization establishing shot for {topic}]. Epic scale. Authentic.","mov":"Slow push forward. Grand reveal."}},
        {{"id":"2-02","img":"Photorealistic oil painting. [Daily life in this era]. People. Market or street. Authentic.","mov":"Pan revealing daily life."}},
        {{"id":"2-03","img":"Photorealistic oil painting. [Power structure - palace or court]. Authority. Grand. Authentic.","mov":"Camera rises. Grand interior."}},
        {{"id":"2-04","img":"Photorealistic oil painting. [Main character in their environment]. Young or early life. Authentic.","mov":"Slow zoom on character."}},
        {{"id":"2-05","img":"Photorealistic oil painting. [Landscape of the era]. Geography. Nature. Epic sky.","mov":"Wide slow pan. Epic landscape."}},
        {{"id":"2-06","img":"Photorealistic oil painting. [Technology or weapons of the time]. Authentic detail.","mov":"Slow orbit. Detail revealed."}},
        {{"id":"2-07","img":"Photorealistic oil painting. [Religious or cultural ceremony]. Authentic. Grand. Epic.","mov":"Camera moves through ceremony."}},
        {{"id":"2-08","img":"Photorealistic oil painting. [Market or trade scene]. Life. Energy. Authentic period.","mov":"Pan across the busy scene."}},
        {{"id":"2-09","img":"Photorealistic oil painting. [Military force of the era]. Power. Authentic uniforms.","mov":"Sweeping view of military power."}},
        {{"id":"2-10","img":"Photorealistic oil painting. [Noble or royal court]. Politics. Intrigue. Authentic.","mov":"Slow push into court scene."}},
        {{"id":"2-11","img":"Photorealistic oil painting. [Architecture of civilization]. Grand buildings. Authentic.","mov":"Camera rises along architecture."}},
        {{"id":"2-12","img":"Photorealistic oil painting. [People gathering for event]. Crowd. Energy. Authentic.","mov":"Pan across gathered people."}},
        {{"id":"2-13","img":"Photorealistic oil painting. [Threat or enemy force]. Danger. Power. Authentic.","mov":"Slow reveal of threat."}},
        {{"id":"2-14","img":"Photorealistic oil painting. [Character receiving news or mission]. Dramatic. Authentic.","mov":"Push in on character reaction."}},
        {{"id":"2-15","img":"Photorealistic oil painting. [Strategic location - city or fortress]. Epic. Authentic.","mov":"Wide reveal of location."}},
        {{"id":"2-16","img":"Photorealistic oil painting. [Sunset over the civilization]. Atmospheric. Beautiful.","mov":"Slow drift as sun sets."}},
        {{"id":"2-17","img":"Photorealistic oil painting. [Symbol of the era's power]. Authentic artifact.","mov":"Slow zoom on symbol."}},
        {{"id":"2-18","img":"Photorealistic oil painting. [Ominous foreshadowing shot]. Dark clouds. Tension.","mov":"Dark clouds gather. Ominous."}}
      ]
    }},
    {{
      "id": 3,
      "title": "THE RISE",
      "narration": "90 words. The turning point. Rising tension. Cliffhanger ending.",
      "shots": [
        {{"id":"3-01","img":"Photorealistic oil painting. [First major turning point in {topic}]. Dramatic. Authentic.","mov":"Dramatic push forward."}},
        {{"id":"3-02","img":"Photorealistic oil painting. [Character making crucial decision]. Resolve. Determination.","mov":"Slow zoom on decisive face."}},
        {{"id":"3-03","img":"Photorealistic oil painting. [Gathering of forces]. Army or alliance. Epic scale.","mov":"Sweeping pan of gathering forces."}},
        {{"id":"3-04","img":"Photorealistic oil painting. [Strategic planning scene]. Maps. Leaders. Torchlit room.","mov":"Push into planning scene."}},
        {{"id":"3-05","img":"Photorealistic oil painting. [March or movement]. Army on the move. Epic landscape.","mov":"Pan following movement."}},
        {{"id":"3-06","img":"Photorealistic oil painting. [First victory or setback]. Reaction. Emotion. Authentic.","mov":"Zoom on emotional moment."}},
        {{"id":"3-07","img":"Photorealistic oil painting. [Enemy reaction]. Fear or defiance. Authentic.","mov":"Push toward enemy."}},
        {{"id":"3-08","img":"Photorealistic oil painting. [Dramatic weather or nature]. Storm. Epic atmosphere.","mov":"Storm builds dramatically."}},
        {{"id":"3-09","img":"Photorealistic oil painting. [Key ally or betrayal]. Relationship. Tension.","mov":"Slow push between figures."}},
        {{"id":"3-10","img":"Photorealistic oil painting. [Siege or approach]. Fortress or city. Epic.","mov":"Slow approach to fortress."}},
        {{"id":"3-11","img":"Photorealistic oil painting. [Crowd reaction]. People watching events. Authentic.","mov":"Pan across watching crowd."}},
        {{"id":"3-12","img":"Photorealistic oil painting. [Night preparations]. Torches. Tension. Authentic.","mov":"Fire and shadows move."}},
        {{"id":"3-13","img":"Photorealistic oil painting. [Dawn before major event]. Sunrise. Anticipation.","mov":"Sun rises slowly. New day."}},
        {{"id":"3-14","img":"Photorealistic oil painting. [Weapons and armor being prepared]. Detail. Authentic.","mov":"Slow detail reveal."}},
        {{"id":"3-15","img":"Photorealistic oil painting. [Character alone contemplating]. Solitude. Dramatic.","mov":"Slow orbit around figure."}},
        {{"id":"3-16","img":"Photorealistic oil painting. [Message or signal sent]. Communication. Urgent.","mov":"Fast dramatic movement."}},
        {{"id":"3-17","img":"Photorealistic oil painting. [Forces aligned ready]. Epic panorama. Authentic.","mov":"Epic sweeping panorama."}},
        {{"id":"3-18","img":"Photorealistic oil painting. [Cliffhanger moment]. Most dramatic instant. Iconic.","mov":"Freeze on iconic moment."}}
      ]
    }},
    {{
      "id": 4,
      "title": "THE CONFLICT",
      "narration": "90 words. Maximum drama. The great battle or betrayal. Visceral and emotional.",
      "shots": [
        {{"id":"4-01","img":"Photorealistic oil painting. [Battle begins - chaos erupts in {topic}]. Epic. Authentic.","mov":"Dramatic fast push into chaos."}},
        {{"id":"4-02","img":"Photorealistic oil painting. [Close combat]. Warriors. Authentic weapons. Intense.","mov":"Dynamic combat movement."}},
        {{"id":"4-03","img":"Photorealistic oil painting. [Strategic overview of battle]. Birds eye. Epic scale.","mov":"Rise to reveal full battle."}},
        {{"id":"4-04","img":"Photorealistic oil painting. [Leader in battle]. Heroic or desperate. Authentic armor.","mov":"Push toward heroic leader."}},
        {{"id":"4-05","img":"Photorealistic oil painting. [Turning point of battle]. Moment of change. Dramatic.","mov":"Dramatic slow zoom."}},
        {{"id":"4-06","img":"Photorealistic oil painting. [Betrayal scene]. Shocked faces. Betrayal moment.","mov":"Slow reveal of betrayal."}},
        {{"id":"4-07","img":"Photorealistic oil painting. [Casualties and suffering]. Real human cost. Somber.","mov":"Slow pull back. Human cost."}},
        {{"id":"4-08","img":"Photorealistic oil painting. [Fire and destruction]. City or fortress burning. Epic.","mov":"Fire spreads dramatically."}},
        {{"id":"4-09","img":"Photorealistic oil painting. [Individual heroism]. One person. Defining moment.","mov":"Push in on heroic moment."}},
        {{"id":"4-10","img":"Photorealistic oil painting. [Enemy commander]. Opposition. Authentic. Powerful.","mov":"Slow reveal of enemy."}},
        {{"id":"4-11","img":"Photorealistic oil painting. [Chaos of battle]. Confusion. Noise. Authentic.","mov":"Chaotic but controlled camera."}},
        {{"id":"4-12","img":"Photorealistic oil painting. [Decisive weapon or tactic]. Key element. Authentic.","mov":"Dramatic reveal of tactic."}},
        {{"id":"4-13","img":"Photorealistic oil painting. [Victory or defeat moment]. Raw emotion. Real.","mov":"Slow zoom on decisive moment."}},
        {{"id":"4-14","img":"Photorealistic oil painting. [Aftermath of main conflict]. Survivors. Somber. Real.","mov":"Slow wide reveal of aftermath."}},
        {{"id":"4-15","img":"Photorealistic oil painting. [Symbol of victory or defeat]. Powerful image.","mov":"Slow orbit around symbol."}},
        {{"id":"4-16","img":"Photorealistic oil painting. [Night after battle]. Fires. Silence. Survivors.","mov":"Slow drift through silence."}},
        {{"id":"4-17","img":"Photorealistic oil painting. [Leader processing victory or defeat]. Alone. Human.","mov":"Slow push toward solitary figure."}},
        {{"id":"4-18","img":"Photorealistic oil painting. [Iconic final battle image]. Most powerful shot.","mov":"Slow dramatic pull back."}}
      ]
    }},
    {{
      "id": 5,
      "title": "THE CLIMAX",
      "narration": "90 words. Peak moment. Decision that changed history forever. Maximum emotional impact.",
      "shots": [
        {{"id":"5-01","img":"Photorealistic oil painting. [Peak climax moment of {topic}]. Most dramatic scene.","mov":"Intense dramatic push forward."}},
        {{"id":"5-02","img":"Photorealistic oil painting. [Character at moment of truth]. Choice. Destiny. Authentic.","mov":"Slow zoom on decisive face."}},
        {{"id":"5-03","img":"Photorealistic oil painting. [The decisive action]. What changed everything.","mov":"Dramatic reveal of action."}},
        {{"id":"5-04","img":"Photorealistic oil painting. [Witness reactions]. People watching history made.","mov":"Pan across witnesses."}},
        {{"id":"5-05","img":"Photorealistic oil painting. [Symbol of the change]. What was won or lost.","mov":"Slow orbit around symbol."}},
        {{"id":"5-06","img":"Photorealistic oil painting. [Emotional human moment]. Real feeling. Authentic.","mov":"Push in on human emotion."}},
        {{"id":"5-07","img":"Photorealistic oil painting. [Scale of consequence]. How much changed.","mov":"Wide reveal of consequence."}},
        {{"id":"5-08","img":"Photorealistic oil painting. [Celebration or mourning]. Response to climax.","mov":"Pan across response."}},
        {{"id":"5-09","img":"Photorealistic oil painting. [Winner takes power]. Throne or crown or victory.","mov":"Slow push toward power."}},
        {{"id":"5-10","img":"Photorealistic oil painting. [Loser or victim]. Human cost. Somber. Real.","mov":"Slow pull back. Dignity."}},
        {{"id":"5-11","img":"Photorealistic oil painting. [Historic announcement]. Proclamation. Crowd.","mov":"Camera rises on announcement."}},
        {{"id":"5-12","img":"Photorealistic oil painting. [Art or monument of the era]. What was created.","mov":"Slow reveal of monument."}},
        {{"id":"5-13","img":"Photorealistic oil painting. [Final confrontation]. Face to face. Tension.","mov":"Push between the figures."}},
        {{"id":"5-14","img":"Photorealistic oil painting. [Death or triumph]. The final moment. Authentic.","mov":"Dramatic slow motion reveal."}},
        {{"id":"5-15","img":"Photorealistic oil painting. [Crowd witnessing]. Masses. History made.","mov":"Wide pan of crowd."}},
        {{"id":"5-16","img":"Photorealistic oil painting. [Sunset after climax]. End of an era. Atmospheric.","mov":"Slow drift as sun sets."}},
        {{"id":"5-17","img":"Photorealistic oil painting. [New order established]. What replaced the old.","mov":"Slow reveal of new world."}},
        {{"id":"5-18","img":"Photorealistic oil painting. [Most iconic image of this entire story]. Unforgettable.","mov":"Slow dramatic final reveal."}}
      ]
    }},
    {{
      "id": 6,
      "title": "THE LEGACY",
      "narration": "90 words. What happened next. Why this matters TODAY. End with powerful question that makes viewers comment. Subscribe call to action.",
      "shots": [
        {{"id":"6-01","img":"Photorealistic oil painting. [Legacy of {topic} - what remained]. Timeless. Epic.","mov":"Slow reverent push forward."}},
        {{"id":"6-02","img":"Photorealistic oil painting. [Influence on later history]. Cause and effect.","mov":"Wide pan of legacy."}},
        {{"id":"6-03","img":"Photorealistic oil painting. [Monument or memorial]. What was built to remember.","mov":"Slow rise along monument."}},
        {{"id":"6-04","img":"Photorealistic oil painting. [Modern echo of ancient event]. Connection to today.","mov":"Contemplative slow orbit."}},
        {{"id":"6-05","img":"Photorealistic oil painting. [Final portrait of main figure]. Iconic. Powerful.","mov":"Slow zoom to iconic face."}},
        {{"id":"6-06","img":"Photorealistic oil painting. [What was lost]. Tragedy or sacrifice. Human.","mov":"Somber slow pull back."}},
        {{"id":"6-07","img":"Photorealistic oil painting. [What was gained]. Progress or change. Hopeful.","mov":"Hopeful slow reveal."}},
        {{"id":"6-08","img":"Photorealistic oil painting. [The world after]. Changed forever. Epic.","mov":"Wide reveal of changed world."}},
        {{"id":"6-09","img":"Photorealistic oil painting. [Symbol that survived]. Artifact or idea. Real.","mov":"Slow orbit around survivor."}},
        {{"id":"6-10","img":"Photorealistic oil painting. [People who came after]. Next generation.","mov":"Pan across next generation."}},
        {{"id":"6-11","img":"Photorealistic oil painting. [Book or record of events]. Knowledge preserved.","mov":"Slow reveal of records."}},
        {{"id":"6-12","img":"Photorealistic oil painting. [Map showing impact]. Geography of change.","mov":"Slow zoom out on map."}},
        {{"id":"6-13","img":"Photorealistic oil painting. [Similar event in later history]. Pattern.","mov":"Connecting pan movement."}},
        {{"id":"6-14","img":"Photorealistic oil painting. [Modern world influenced by this]. Today.","mov":"Bridge between eras."}},
        {{"id":"6-15","img":"Photorealistic oil painting. [Question visualized]. What if different choice made.","mov":"Contemplative slow movement."}},
        {{"id":"6-16","img":"Photorealistic oil painting. [Sunset over historical site]. End of story. Beautiful.","mov":"Golden hour slow drift."}},
        {{"id":"6-17","img":"Photorealistic oil painting. [Stars over ancient landscape]. Time passing.","mov":"Slow rise to stars."}},
        {{"id":"6-18","img":"Photorealistic oil painting. [Final iconic image - most memorable of whole video]. Grand.","mov":"Epic slow pull back to wide."}}
      ]
    }}
  ]
}}

CRITICAL: Replace ALL [...] placeholders with SPECIFIC content about "{topic}".
Every shot must be unique and different from all others.
Return ONLY the JSON. No markdown. No explanation."""

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
    total = sum(len(s.get("shots", [])) for s in script["scenes"])
    print(f"   ✅ Script: '{script['title']}'")
    print(f"   Total shots: {total}")
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

# ─── STEP 2: GENERATE IMAGE ────────────────────────────────────────────────────
def generate_image(prompt, filename):
    enhanced = f"Photorealistic historical oil painting masterpiece. {prompt} Rembrandt chiaroscuro lighting. Museum quality. Ultra detailed authentic period costumes and architecture. NOT cartoon. NOT CGI. NOT modern. NOT AI-looking."

    payload = {
        "model": "kling-v2-1",
        "prompt": enhanced,
        "negative_prompt": "cartoon, anime, CGI, modern, watermark, text, blurry, distorted, AI-looking, plastic",
        "aspect_ratio": "16:9",
        "n": 1
    }

    resp = requests.post(
        "https://api.klingai.com/v1/images/generations",
        headers=kling_headers(), json=payload
    )

    if resp.status_code != 200:
        print(f"      ⚠️ Image API error {resp.status_code}, using Pexels")
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

# ─── STEP 3: IMAGE TO VIDEO ────────────────────────────────────────────────────
def image_to_video(image_path, motion_prompt, output_path):
    with open(image_path, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        "model_name": "kling-v2-master",
        "image": img_b64,
        "prompt": f"{motion_prompt} Cinematic. Historically authentic. No modern elements.",
        "negative_prompt": "shaky, fast motion, modern, text, watermark, distortion, flash",
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

# ─── STEP 4: GENERATE NARRATION ────────────────────────────────────────────────
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
        print(f"      ✅ Narration saved")
        return True
    print(f"      ❌ ElevenLabs: {resp.status_code} - {resp.text[:100]}")
    return False

# ─── STEP 5: GET DURATION ──────────────────────────────────────────────────────
def get_duration(path):
    r = subprocess.run([
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', str(path)
    ], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0

# ─── STEP 6: CONCAT SHOT VIDEOS (NO AUDIO) ────────────────────────────────────
def concat_shots(video_paths, output_path):
    concat_file = OUTPUT_DIR / f"concat_{int(time.time())}.txt"
    with open(concat_file, 'w') as f:
        for vp in video_paths:
            f.write(f"file '{Path(vp).absolute()}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(concat_file),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-an',
        str(output_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    concat_file.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"      ❌ Concat error: {r.stderr[-100:]}")
    return r.returncode == 0

# ─── STEP 7: ADD AUDIO TO SCENE VIDEO ─────────────────────────────────────────
def add_audio_to_scene(video_path, audio_path, output_path):
    vid_dur = get_duration(video_path)
    aud_dur = get_duration(audio_path)
    print(f"      Video: {vid_dur:.1f}s | Audio: {aud_dur:.1f}s")

    if vid_dur <= 0 or aud_dur <= 0:
        print(f"      ❌ Invalid duration")
        return False

    if vid_dur >= aud_dur:
        # Video longer or equal — just trim and add audio
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-t', str(aud_dur),
            str(output_path)
        ]
    else:
        # Video shorter — loop video to match audio
        print(f"      ⚠️ Video shorter than audio by {aud_dur-vid_dur:.1f}s — looping last shot")
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1', '-i', str(video_path),
            '-i', str(audio_path),
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            '-t', str(aud_dur),
            str(output_path)
        ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"      ✅ Audio added successfully")
        return True
    print(f"      ❌ Audio merge error: {r.stderr[-150:]}")
    return False

# ─── STEP 8: THUMBNAIL ─────────────────────────────────────────────────────────
def create_thumbnail(script, bg_path):
    print("🖼️ Creating thumbnail...")
    W, H = 1280, 720
    img = Image.new('RGB', (W, H), (5, 5, 15))

    try:
        bg = Image.open(bg_path).convert('RGB')
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

    main = script.get('thumbnail_text', script['title'][:30]).upper()
    sub  = script.get('thumbnail_subtext', 'THE UNTOLD STORY').upper()

    words = main.split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if len(' '.join(cur)) > 14:
            lines.append(' '.join(cur[:-1]))
            cur = [w]
    if cur: lines.append(' '.join(cur))

    y = H//2 - (len(lines)*105)//2
    for i, line in enumerate(lines):
        for sx, sy in [(4,4),(3,3),(2,2)]:
            draw.text((28+sx, y+sy), line, font=fxl, fill=(0,0,0))
        draw.text((28, y), line, font=fxl, fill=(255,220,30) if i==0 else (255,255,255))
        y += 105

    draw.text((30, y+13), sub, font=flg, fill=(0,0,0))
    draw.text((28, y+10), sub, font=flg, fill=(220,25,25))
    draw.rectangle([20, H-58, 280, H-15], fill=(180,15,15))
    draw.text((30, H-50), "▶ HISTORICOVE TV", font=fsm, fill=(255,255,255))

    path = OUTPUT_DIR / "thumbnail.jpg"
    img.save(path, "JPEG", quality=95)
    print("   ✅ Thumbnail created")
    return path

# ─── STEP 9: TITLE CARD ────────────────────────────────────────────────────────
def create_title_card(title):
    W, H = 1920, 1080
    img = Image.new('RGB', (W, H), (5,5,15))
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
        if len(' '.join(cur)) > 26:
            lines.append(' '.join(cur[:-1]))
            cur = [w]
    if cur: lines.append(' '.join(cur))

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
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', str(ti),
        '-t', '4', '-vf', 'fade=in:0:25,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-r', '25', '-an', str(tv)
    ], capture_output=True)
    return tv

# ─── STEP 10: MERGE ALL SCENES ─────────────────────────────────────────────────
def merge_final(scene_videos, output_path):
    print(f"🎬 Merging {len(scene_videos)} scenes into final video...")
    concat_file = OUTPUT_DIR / "final_concat.txt"
    with open(concat_file, 'w') as f:
        for vp in scene_videos:
            f.write(f"file '{Path(vp).absolute()}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', str(concat_file),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        str(output_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        size = Path(output_path).stat().st_size / (1024*1024)
        print(f"   ✅ Final video: {size:.1f} MB")
        return True
    print(f"   ❌ Final merge failed: {r.stderr[-200:]}")
    return False

# ─── STEP 11: UPLOAD TO YOUTUBE ────────────────────────────────────────────────
def upload_youtube(video_path, thumb_path, script):
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
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"   Upload: {int(status.progress()*100)}%")

    vid_id = response["id"]
    print(f"   ✅ https://youtu.be/{vid_id}")

    try:
        youtube.thumbnails().set(
            videoId=vid_id,
            media_body=MediaFileUpload(str(thumb_path), mimetype="image/jpeg")
        ).execute()
        print("   ✅ Thumbnail set")
    except Exception as e:
        print(f"   ⚠️ Thumbnail: {e}")

    return vid_id

# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("🎬  HistoriCove TV — Professional Pipeline v5")
    print(f"    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    18 shots/scene × 5s = 90s video = NO REPEAT")
    print("=" * 65)

    # 1. Generate script
    script = generate_script()

    all_scene_videos = []
    first_image = None

    # 2. Title card (no audio)
    title_vid = create_title_card(script["title"])
    all_scene_videos.append(title_vid)

    # 3. Process each scene
    for scene in script["scenes"]:
        print(f"\n{'═'*55}")
        print(f"🎭 Scene {scene['id']}/6: {scene['title']}")
        print(f"{'═'*55}")

        shots = scene.get("shots", [])
        print(f"   Shots: {len(shots)}")

        # 3a. Generate narration FIRST
        audio_path = OUTPUT_DIR / f"narration_{scene['id']:02d}.mp3"
        print(f"\n🎙️ Generating narration for scene {scene['id']}...")
        audio_ok = generate_narration(scene["narration"], audio_path)
        if not audio_ok:
            print(f"   ❌ No narration — skipping scene")
            continue

        # 3b. Generate image + video for each shot
        shot_videos = []
        for j, shot in enumerate(shots):
            shot_id = shot.get("id", f"{scene['id']}-{j+1:02d}")
            img_path = OUTPUT_DIR / f"img_{shot_id.replace('-','_')}.jpg"
            vid_path = OUTPUT_DIR / f"vid_{shot_id.replace('-','_')}.mp4"

            print(f"\n   📸 Shot {shot_id} ({j+1}/{len(shots)})")

            # Generate image
            img_ok = generate_image(shot["img"], img_path)
            if not img_ok:
                print(f"      ⚠️ No image for shot {shot_id}")
                continue

            if first_image is None:
                first_image = img_path

            # Generate video
            print(f"      🎬 Converting to video...")
            vid_ok = image_to_video(img_path, shot["mov"], vid_path)
            if vid_ok:
                shot_videos.append(vid_path)
                print(f"      ✅ Shot {shot_id} done")
            else:
                print(f"      ⚠️ Video failed for {shot_id}")

        if not shot_videos:
            print(f"   ❌ No shot videos for scene {scene['id']}")
            continue

        # 3c. Concatenate all shot videos (no audio)
        scene_raw = OUTPUT_DIR / f"scene_{scene['id']:02d}_raw.mp4"
        print(f"\n   🔗 Joining {len(shot_videos)} shots...")
        if not concat_shots(shot_videos, scene_raw):
            print(f"   ❌ Concat failed for scene {scene['id']}")
            continue

        # 3d. Add narration audio to scene video
        scene_final = OUTPUT_DIR / f"scene_{scene['id']:02d}_final.mp4"
        print(f"   🔊 Adding audio...")
        if add_audio_to_scene(scene_raw, audio_path, scene_final):
            all_scene_videos.append(scene_final)
            print(f"   ✅ Scene {scene['id']} COMPLETE!")
        else:
            print(f"   ❌ Audio failed for scene {scene['id']}")

    if len(all_scene_videos) < 2:
        print("\n❌ Not enough scenes. Aborting.")
        return

    # 4. Thumbnail
    bg = first_image or OUTPUT_DIR / "img_1_01.jpg"
    thumbnail = create_thumbnail(script, bg)

    # 5. Merge all scenes
    final_video = OUTPUT_DIR / "final_video.mp4"
    if not merge_final(all_scene_videos, final_video):
        print("❌ Final merge failed.")
        return

    # 6. Upload
    vid_id = upload_youtube(final_video, thumbnail, script)

    print("\n" + "=" * 65)
    if vid_id:
        print(f"🎉  SUCCESS!")
        print(f"    https://youtu.be/{vid_id}")
        print(f"    Title: {script['title']}")
    else:
        print("⚠️  Video created but upload failed")
    print("=" * 65)

if __name__ == "__main__":
    main()
