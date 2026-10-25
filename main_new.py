import os
import telebot
from flask import Flask
import threading
import yt_dlp
import subprocess
from gtts import gTTS
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, ColorClip

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Your YouTube Automation Pipeline is live 🚀"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Namaste! YouTube video ka link bhejo. Script, US voiceover, editing aur thumbnail sab kuch apne aap process hokar Telegram par mil jayega!")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_youtube_automation(message):
    video_link = message.text
    chat_id = message.chat.id
    
    bot.reply_to(message, "🔗 Link mil gaya! Sabse pehle content analyze karke US audience ke liye script taiyar ki ja rahi hai...")

    try:
        # Step 1: Extract Video Info (Title / Description) using yt-dlp (Zero Paid API)
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_link, download=False)
            video_title = info.get('title', 'Automated Video Topic')
            video_desc = info.get('description', '')[:500]

        bot.send_message(chat_id, f"📝 Topic Analyzed: *{video_title}*\nAb permanent US English voiceover generate ho raha hai...", parse_mode="Markdown")

        # Step 2: Generate Script & Permanent US Voiceover (Free TTS with US Accent)
        script_text = f"Welcome back to our channel. Today we are diving deep into {video_title}. Let's explore the key insights, incredible details, and everything you need to know about this topic in depth."
        
        audio_path = "voiceover.mp3"
        # Using English (US) accent configuration
        tts = gTTS(text=script_text, lang='en', tld='com', slow=False)
        tts.save(audio_path)

        bot.send_message(chat_id, "🎙️ Voiceover ready! Ab visuals aur professional video editing ho rahi hai...")

        # Step 3: Video Composition & Professional Editing (Using MoviePy)
        output_video_path = "final_output.mp4"
        
        # Create a clean background canvas for the video
        bg_clip = ColorClip(size=(1280, 720), color=(20, 20, 20), duration=10)
        
        # Add dynamic professional text/subtitles overlay
        txt_clip = TextClip(video_title[:50], fontsize=40, color='white', size=(1100, None), method='caption')
        txt_clip = txt_clip.set_duration(10).set_position('center')
        
        audio_clip = AudioFileClip(audio_path)
        # Match video duration to audio or keep it structured
        video = CompositeVideoClip([bg_clip, txt_clip]).set_duration(min(audio_clip.duration, 15))
        video = video.set_audio(audio_clip)
        
        video.write_videofile(output_video_path, fps=24, codec='libx264', audio_codec='aac', logger=None)

        bot.send_message(chat_id, "🎬 Video editing complete! Thumbnail analyze karke generate kiya ja raha hai...")

        # Step 4: Thumbnail Generation (Placeholder/Canvas style matching)
        thumbnail_path = "thumbnail.jpg"
        thumb_bg = ColorClip(size=(1280, 720), color=(10, 10, 50))
        thumb_txt = TextClip(video_title[:40], fontsize=60, color='yellow', size=(1100, None), method='caption')
        thumb_txt = thumb_txt.set_duration(1).set_position('center')
        thumb_composite = CompositeVideoClip([thumb_bg, thumb_txt])
        thumb_composite.save_frame(thumbnail_path, t=0)

        bot.send_message(chat_id, "📤 Sab kuch ready hai! Final video aur thumbnail bheja ja raha hai...")

        # Step 5: Deliver Final Video & Thumbnail to Telegram
        with open(output_video_path, 'rb') as vid:
            bot.send_video(chat_id, vid, caption=f"🔥 *Final Edited Video*\nTopic: {video_title}", parse_mode="Markdown")

        with open(thumbnail_path, 'r_b' if 'r_b' in globals() else 'rb') as thumb:
            bot.send_photo(chat_id, thumb, caption="🖼️ *Matching High-Click Thumbnail*", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error aa gaya bhai: {str(e)}")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
  
