import os
import asyncio
import threading
from flask import Flask
import telebot
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips

# --- Flask Server (Render Free Web Service ke liye taaki bot active rahe) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube Automation Bot is Running 24/7!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# --- Telegram Bot Setup ---
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

print("Bot successfully cloud par start ho raha hai...")

async def generate_voice(text_prompt):
    voice = "en-US-ChristopherNeural"
    output_audio = "final_voiceover.mp3"
    communicate = edge_tts.Communicate(text_prompt, voice)
    await communicate.save(output_audio)
    return output_audio

def generate_thumbnail(title_text):
    output_thumb = "thumbnail.jpg"
    img = Image.new('RGB', (1280, 720), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.rectangle([(40, 40), (1240, 680)], outline=(255, 215, 0), width=4)
    draw.text((80, 240), title_text.upper()[:30], fill=(255, 255, 255), font=font_title)
    draw.text((80, 350), "Fully Automated Production", fill=(255, 215, 0), font=font_sub)
    img.save(output_thumb)
    return output_thumb

def generate_final_video(audio_path, title_text):
    output_video = "final_upload_ready_video.mp4"
    frame_path = "temp_frame.jpg"
    
    frame_img = Image.new('RGB', (1280, 720), color=(10, 10, 15))
    d = ImageDraw.Draw(frame_img)
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
    except:
        fnt = ImageFont.load_default()
        
    d.text((80, 280), f"Topic: {title_text}\nReady for Upload", fill=(255, 255, 255), font=fnt)
    frame_img.save(frame_path)
    
    voice_clip = AudioFileClip(audio_path)
    duration = voice_clip.duration
    
    bgm_path = "bgm.mp3"
    if os.path.exists(bgm_path):
        bgm_clip = AudioFileClip(bgm_path).volumex(0.15)
        if bgm_clip.duration < duration:
            loops = int(duration / bgm_clip.duration) + 1
            bgm_clip = concatenate_audioclips([bgm_clip] * loops)
        bgm_clip = bgm_clip.set_duration(duration)
        final_audio = CompositeAudioClip([voice_clip, bgm_clip])
    else:
        final_audio = voice_clip
        
    video_clip = ImageClip(frame_path).set_duration(duration).set_audio(final_audio)
    video_clip.write_videofile(output_video, fps=24, codec='libx264', audio_codec='aac')
    return output_video

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Namaste! Mujhe koi bhi topic bhejo, main voiceover, thumbnail aur video taiyar karke bhej raha hoon!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    bot.reply_to(message, "⏳ Video aur thumbnail process ho rahe hain, thoda wait karo...")
    
    try:
        script = f"Complete details about: {user_text}. Fully automated production ready for YouTube."
        audio_file = asyncio.run(generate_voice(script))
        thumb_file = generate_thumbnail(user_text)
        video_file = generate_final_video(audio_file, user_text)
        
        bot.send_message(message.chat.id, "✅ Lo bhai, sab kuch taiyar hai!")
        
        with open(thumb_file, 'rb') as thumb:
            bot.send_photo(message.chat.id, thumb, caption="🖼️ YouTube Thumbnail")
            
        with open(video_file, 'rb') as vid:
            bot.send_video(message.chat.id, vid, caption="🎬 Final Upload-Ready Video")
            
    except Exception as g_err:
        bot.reply_to(message, f"❌ Error: {str(g_err)}")

if __name__ == "__main__":
    # Flask server ko background thread mein chala rahe hain
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Telegram bot polling
    bot.infinity_polling()
  
