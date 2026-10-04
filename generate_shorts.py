import os
import sys
import json
import asyncio
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont

def download_image(url, output_path="thumb.jpg"):
    if not url:
        # Create a fallback placeholder
        img = Image.new("RGB", (1080, 1080), color=(30, 30, 30))
        img.save(output_path)
        return output_path
    res = requests.get(url, timeout=15)
    with open(output_path, "wb") as f:
        f.write(res.content)
    return output_path

async def generate_audio(text, output_audio="narration.mp3"):
    # Using Microsoft Edge-TTS with natural Japanese female voice
    cmd = f'edge-tts --voice ja-JP-NanamiNeural --text "{text}" --write-media {output_audio}'
    p = await asyncio.create_subprocess_shell(cmd)
    await p.communicate()

def build_vertical_video(image_path, audio_path, product_name, hook_text, output_mp4="final_short.mp4"):
    # Get audio duration
    probe_cmd = f'ffprobe -i {audio_path} -show_entries format=duration -v quiet -of csv="p=0"'
    duration = float(subprocess.check_output(probe_cmd, shell=True).decode().strip())
    
    # 1. Base vertical canvas with blurred background & centered image
    # 2. Add top catch header & bottom CTA text
    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:10[bg];"
        f"[0:v]scale=960:960:force_original_aspect_ratio=decrease[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2-100[v1];"
        f"[v1]drawtext=text='【話題の神グッズ】':fontcolor=white:fontsize=72:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-text_w)/2:y=250,"
        f"drawtext=text='{hook_text}':fontcolor=yellow:fontsize=52:box=1:boxcolor=black@0.7:boxborderw=15:x=(w-text_w)/2:y=370,"
        f"drawtext=text='▼ 楽天最安値は概要欄＆コメント欄へ ▼':fontcolor=white:fontsize=48:box=1:boxcolor=red@0.8:boxborderw=20:x=(w-text_w)/2:y=1600[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration + 1.0),
        output_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated short video: {output_mp4} ({duration}s)")
    return output_mp4

def main():
    payload_raw = os.environ.get("PAYLOAD", "{}")
    payload = json.loads(payload_raw) if payload_raw else {}
    
    product_name = payload.get("product_name", "話題の神グッズ")
    hook_problem = payload.get("hook_problem", "日々のプチストレスを一瞬で解消！")
    image_url = payload.get("image_url", "")
    
    narration = f"ちょっと待って！まだこれ知らないの？今SNSで大バズり中の、{product_name}！日々の面倒な手間がこれ一台で劇的に解消されます。気になる楽天最安値や詳しい本音レビューは、概要欄とコメント欄のブログを今すぐチェックしてみてね！"
    
    print("1. Downloading image...")
    img = download_image(image_url)
    
    print("2. Generating AI Voice with Edge-TTS...")
    asyncio.run(generate_audio(narration))
    
    print("3. Rendering 1080x1920 Short Video with FFmpeg...")
    short_mp4 = build_vertical_video(img, "narration.mp3", product_name, "生活が激変する便利アイテム！")
    print(f"Video ready: {short_mp4}")

if __name__ == "__main__":
    main()
