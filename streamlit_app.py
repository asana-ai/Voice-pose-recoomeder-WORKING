import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import os
import numpy as np

# Configuration
SAMPLE_RATE = 16000
DURATION = 5
FILENAME = "output.wav"

# Pain to poses mapping
pain_to_poses = {
    "lower back": ["Cat-Cow", "Child's Pose", "Cobra Pose", "Bridge Pose", "Knees-to-Chest"],
    "back": ["Cat-Cow", "Child's Pose", "Cobra Pose", "Bridge Pose", "Knees-to-Chest"],
    "shoulder": ["Thread the Needle", "Eagle Arms", "Cow Face Pose", "Reverse Prayer", "Shoulder Rolls"],
    "neck": ["Neck Rolls", "Chin Tucks", "Ear-to-Shoulder", "Thread the Needle", "Cat-Cow"],
    "knee": ["Hero Pose", "Bridge Pose", "Wall Sit", "Chair Pose", "Low Lunge"],
    "wrist": ["Wrist Flexor Stretch", "Wrist Circles", "Prayer Stretch", "Table Top", "Downward Dog"],
    "hip": ["Pigeon Pose", "Garland Pose", "Lizard Pose", "Butterfly Pose", "Bridge Pose"],
    "ankle": ["Seated Ankle Stretch", "Downward Dog", "Standing Calf Stretch", "Hero Pose", "Toe Squat"]
}

default_poses = ["Mountain Pose", "Tree Pose", "Corpse Pose", "Butterfly Pose", "Legs Up the Wall"]

def record_audio(duration=DURATION, filename=FILENAME):
    try:
        recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sd.wait()
        write(filename, SAMPLE_RATE, recording)
        return True
    except Exception as e:
        st.error(f"Recording error: {e}")
        return False

def transcribe_audio(filename=FILENAME):
    recognizer = sr.Recognizer()
    try:
        if not os.path.exists(filename):
            st.error("Audio file not found")
            return None
            
        with sr.AudioFile(filename) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)
        
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("Could not understand the audio. Please speak more clearly.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None

def identify_pain_area_and_poses(text: str) -> tuple:
    text = text.lower()
    for pain_area in pain_to_poses:
        if pain_area in text:
            return pain_area, pain_to_poses[pain_area].copy()
    return "general", default_poses.copy()

# Streamlit UI
st.set_page_config(
    page_title="Yoga Pose Suggester",
    page_icon="🧘‍♀️",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #ffd700;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    .stApp {
        background-color: #1a2533;
        color: #ffd700;
    }
    .pose-container {
        background-color: #2c3e50;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ffd700;
    }
    .pain-area-header {
        background-color: #34495e;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: #ffd700;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main UI
st.markdown('<h1 class="main-header">🧘‍♀️ Yoga Pose Suggester</h1>', unsafe_allow_html=True)

st.markdown("### Click the button below and describe your pain area")
st.markdown("*(e.g., 'My lower back hurts' or 'I have shoulder pain')*")

# Initialize session state
if 'poses' not in st.session_state:
    st.session_state.poses = []
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'pain_area' not in st.session_state:
    st.session_state.pain_area = ""

# Record button
if st.button("🎤 Start Recording (5 seconds)", type="primary"):
    with st.spinner("Recording... Please speak now!"):
        success = record_audio()
    
    if success:
        with st.spinner("Processing your audio..."):
            text = transcribe_audio()
            
            if text:
                st.session_state.transcribed_text = text
                pain_area, poses = identify_pain_area_and_poses(text)
                st.session_state.pain_area = pain_area
                st.session_state.poses = poses
                st.success("Audio processed successfully!")
            else:
                st.error("Sorry, could not understand your speech. Please try again.")
    else:
        st.error("Failed to record audio. Please check your microphone.")

# Display results
if st.session_state.transcribed_text:
    st.markdown(f"### 📝 You said: *'{st.session_state.transcribed_text}'*")
    
    # Display detected pain area
    if st.session_state.pain_area != "general":
        st.markdown(f'<div class="pain-area-header">🎯 Detected Pain Area: {st.session_state.pain_area.title()}</div>', unsafe_allow_html=True)
        st.markdown(f"### 🧘‍♀️ Your Complete {st.session_state.pain_area.title()} Workout Routine:")
    else:
        st.markdown('<div class="pain-area-header">🧘‍♀️ General Yoga Routine</div>', unsafe_allow_html=True)
        st.markdown("### 🧘‍♀️ Your General Yoga Routine:")
    
    # Pose reordering section
    st.markdown("#### 🔄 Customize Your Routine Order:")
    st.markdown("*Use the buttons below to reorder poses*")
    
    # Display poses with reorder buttons
    for i, pose in enumerate(st.session_state.poses):
        col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
        
        with col1:
            if os.path.exists("images/test.jpg"):
                st.image("images/test.jpg", width=100)
            else:
                st.markdown("🧘‍♀️")
        
        with col2:
            st.markdown(f'<div class="pose-container"><h4>{i + 1}. {pose}</h4></div>', unsafe_allow_html=True)
        
        with col3:
            if i > 0:  # Can move up if not first
                if st.button("⬆️", key=f"up_{i}"):
                    # Swap with previous pose
                    st.session_state.poses[i], st.session_state.poses[i-1] = st.session_state.poses[i-1], st.session_state.poses[i]
                    st.rerun()
        
        with col4:
            if i < len(st.session_state.poses) - 1:  # Can move down if not last
                if st.button("⬇️", key=f"down_{i}"):
                    # Swap with next pose
                    st.session_state.poses[i], st.session_state.poses[i+1] = st.session_state.poses[i+1], st.session_state.poses[i]
                    st.rerun()
    
    # Reset routine button
    if st.button("🔄 Reset to Original Order", type="secondary"):
        if st.session_state.pain_area != "general":
            st.session_state.poses = pain_to_poses[st.session_state.pain_area].copy()
        else:
            st.session_state.poses = default_poses.copy()
        st.rerun()
    
    # Workout summary
    st.markdown("---")
    st.markdown("### 📋 Your Workout Summary:")
    workout_text = " → ".join([f"{i+1}. {pose}" for i, pose in enumerate(st.session_state.poses)])
    st.markdown(f"**Routine:** {workout_text}")
    
    # Export routine
    if st.button("📋 Copy Routine to Clipboard"):
        routine_list = "\n".join([f"{i+1}. {pose}" for i, pose in enumerate(st.session_state.poses)])
        st.code(routine_list, language="text")
        st.success("Routine displayed above - you can copy it manually!")

# Instructions
st.markdown("---")
st.markdown("### 📋 Instructions:")
st.markdown("""
1. **Record:** Click the recording button and describe your pain area
2. **Review:** See all poses for your specific pain area
3. **Customize:** Use ⬆️ and ⬇️ buttons to reorder poses
4. **Practice:** Follow your personalized routine
5. **Reset:** Use the reset button to return to original order
""")

# Supported pain areas
st.markdown("### 🎯 Supported Pain Areas:")
pain_areas = list(pain_to_poses.keys())
st.markdown(", ".join([area.title() for area in pain_areas]))