import speech_recognition as sr
import tempfile
from gtts import gTTS
import os
import pygame
import streamlit as st

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self._audio_available = False
        self._mic_available = False
        
        # Check audio output availability
        try:
            pygame.mixer.init()
            pygame.mixer.quit()
            self._audio_available = True
        except Exception:
            self._audio_available = False
            
        # Check microphone availability
        try:
            with sr.Microphone() as source:
                self._mic_available = True
        except Exception:
            self._mic_available = False
    
    def text_to_speech(self, text):
        """Convert text to speech and save it"""
        tts = gTTS(text=text, lang='en')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name

    def play_audio(self, file_path):
        """Play audio file using pygame with fallback behavior"""
        try:
            if not self._audio_available:
                st.warning("Audio playback not available. Question text is displayed above.")
                return

            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            pygame.mixer.quit()
        except Exception as e:
            st.warning("Audio playback not available. Question text is displayed above.")
            self._audio_available = False
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def record_audio(self):
        """Record audio from microphone or get text input as fallback"""
        if self._mic_available:
            try:
                with sr.Microphone() as source:
                    st.write("Listening... Speak now!")
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                    
                try:
                    text = self.recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    st.error("Could not understand audio. Please try speaking again or use text input below.")
                    return self._get_text_input()
                except sr.RequestError as e:
                    st.error(f"Could not request results from speech recognition service. Using text input instead.")
                    return self._get_text_input()
            except Exception as e:
                st.error(f"Error recording audio. Using text input instead.")
                return self._get_text_input()
        else:
            st.info("No microphone detected. Please type your answer below.")
            return self._get_text_input()
            
    def _get_text_input(self):
        """Get answer via text input"""
        text_input = st.text_area("Type your answer here:", key="text_answer")
        if st.button("Submit Answer", key="submit_text"):
            return text_input
        return None