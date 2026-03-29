import streamlit as st
import yt_dlp
import whisper
from deep_translator import GoogleTranslator
import os
import glob

# 🔥 Load model once
model = whisper.load_model("tiny")

st.set_page_config(page_title="YouTube Translator", page_icon="🎥")

LANGUAGES = {
    "Hindi": "hi",
    "English": "en",
    "Gujarati": "gu",
    "French": "fr",
    "Spanish": "es",
    "German": "de"
}

# ---------------- TRANSLATION ----------------
def translate_large_text(text, lang_code):
    try:
        translator = GoogleTranslator(source='auto', target=lang_code)

        chunk_size = 3000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        translated = []
        for chunk in chunks:
            translated.append(translator.translate(chunk))

        return " ".join(translated)

    except Exception:
        return "❌ Translation failed"

# ---------------- CORE ----------------
def process_video(url, lang_code):
    try:
        # ---------- DOWNLOAD ----------
        try:
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': 'audio.%(ext)s',
                'quiet': True,
                'download_sections': '*0-180'
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception:
            raise Exception("❌ Failed to download video (check link or try another video)")

        # ---------- FILE CHECK ----------
        files = glob.glob("audio.*")
        if not files:
            raise Exception("❌ Audio file not found after download")

        audio_file = files[0]

        # ---------- TRANSCRIBE ----------
        try:
            result = model.transcribe(audio_file, fp16=False)
            text = result["text"]

            if not text.strip():
                raise Exception("Empty transcription")

        except Exception:
            raise Exception("❌ Transcription failed (audio issue)")

        # ---------- TRANSLATE ----------
        translated = translate_large_text(text, lang_code)

        return text, translated

    finally:
        # ---------- CLEANUP ----------
        for f in glob.glob("audio.*"):
            if os.path.exists(f):
                os.remove(f)

# ---------------- UI ----------------
st.title("🎥 YouTube → Text Translator")

with st.sidebar:
    st.header("⚙️ Settings")
    url = st.text_input("🔗 Paste YouTube Link")
    lang = st.selectbox("🌍 Language", list(LANGUAGES.keys()))
    btn = st.button("🚀 Convert")

# Show video
if url:
    st.subheader("📺 Video Preview")
    st.video(url)

# Process
if btn:
    if not url:
        st.error("❌ Please enter a YouTube URL")

    elif "youtube.com" not in url and "youtu.be" not in url:
        st.error("❌ Invalid YouTube URL")

    else:
        try:
            with st.spinner("⏳ Processing... Please wait"):
                original, translated = process_video(url, LANGUAGES[lang])

            st.success("✅ Completed!")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📄 Original Text")
                st.text_area("Original", original, height=600)

            with col2:
                st.subheader("🌍 Translated Text")
                st.text_area("Translated", translated, height=600)

        except Exception as e:
            st.error(str(e))