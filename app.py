import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image

# --- Page setup ---
st.set_page_config(page_title="Aircraft Damage Inspector", layout="centered")
st.title("✈️ Aircraft Damage Classification & Captioning")
st.write("Upload an image of aircraft damage to classify it (dent/crack) and generate a caption.")

# --- Load classification model (cached so it only loads once) ---
@st.cache_resource
def load_classification_model():
    return load_model("aircraft_damage_model.h5")

# --- Load BLIP model for captioning (cached so it only loads once) ---
@st.cache_resource
def load_blip():
    from transformers import BlipProcessor, BlipForConditionalGeneration
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, blip_model

model = load_classification_model()
processor, blip_model = load_blip()

# --- Upload image ---
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded Image", use_container_width=True)

    if st.button("Analyze Image"):
        with st.spinner("Analyzing..."):
            # --- Classification ---
            img_resized = img.resize((224, 224))
            img_array = keras_image.img_to_array(img_resized) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            prediction = model.predict(img_array)[0][0]
            label = "dent" if prediction <= 0.5 else "crack"
            confidence = 1 - prediction if label == "dent" else prediction

            st.subheader("🔍 Classification Result")
            st.write(f"**Prediction:** {label}")
            st.write(f"**Confidence:** {confidence:.2%}")

            # --- Captioning with BLIP ---
            inputs = processor(images=img, text="This is a picture of", return_tensors="pt")
            output = blip_model.generate(**inputs)
            caption = processor.decode(output[0], skip_special_tokens=True)

            st.subheader("📝 Generated Caption")
            st.write(caption)
