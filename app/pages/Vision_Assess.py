import base64, io, streamlit as st
from PIL import Image
from openai import AzureOpenAI
import os

st.title("🖼️ Damage Assessment (Vision)")
st.caption("Upload a disaster photo (floods, wildfires, earthquakes) to get an instant AI assessment.")

# --- Config ---
AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")
AOAI_API_KEY = os.getenv("AOAI_API_KEY")
VISION_DEPLOY = os.getenv("AOAI_VISION_DEPLOYMENT", "gpt-4o")

if not (AOAI_ENDPOINT and AOAI_API_KEY and VISION_DEPLOY):
    st.error("Missing AOAI_* environment variables. Set AOAI_ENDPOINT, AOAI_API_KEY, AOAI_VISION_DEPLOYMENT.")
    st.stop()

client = AzureOpenAI(api_key=AOAI_API_KEY, api_version="2024-06-01", azure_endpoint=AOAI_ENDPOINT)

uploaded = st.file_uploader("Upload an image", type=["png","jpg","jpeg"])
if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded image", use_column_width=True)

    # Convert to data URL so GPT-4o-vision can see the image
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"

    prompt = st.text_area("Optional context", "Assess visible damage severity and recommend immediate safety actions.")

    if st.button("Analyze", type="primary"):
        with st.spinner("Analyzing image…"):
            msg = [
                {"role": "system", "content": "You are a disaster response analyst. Be concise and actionable."},
                {
                    "role": "user",
                    "content": [
                        {"type":"text","text": f"{prompt}\nReturn a JSON block with fields: damage_types, severity_0_5, summary, recommended_actions."},
                        {"type":"image_url","image_url":{"url": data_url}}
                    ],
                },
            ]
            resp = client.chat.completions.create(model=VISION_DEPLOY, messages=msg, temperature=0.2)
            text = resp.choices[0].message.content

        st.markdown("### Result")
        st.write(text)
        st.caption("Tip: Parse the JSON into fields to show metrics or store in logs.")
