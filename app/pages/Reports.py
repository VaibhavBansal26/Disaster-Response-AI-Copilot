import io, datetime, pandas as pd, streamlit as st
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from app.utils.data import load_events

st.title("📄 Situation Report")
st.caption("Generate a 1-page PDF summary based on current events table.")

df = load_events()
if df.empty:
    st.info("No data in data/events.csv")
else:
    st.dataframe(df.tail(10), use_container_width=True)

    if st.button("Generate PDF"):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=LETTER)
        width, height = LETTER
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height-40, "Situation Report")
        c.setFont("Helvetica", 10)
        c.drawString(40, height-60, f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M}")
        c.drawString(40, height-75, f"Total incidents: {len(df)}")

        y = height-100
        c.setFont("Helvetica", 9)
        for _, row in df.tail(12).iterrows():
            line = f"{row['date']} | {row['disaster_type']} | {row['location_text']}: {row['description'][:80]}"
            c.drawString(40, y, line)
            y -= 12
            if y < 60:
                break
        c.showPage()
        c.save()
        st.download_button("Download PDF", data=buf.getvalue(), file_name="situation_report.pdf", mime="application/pdf")
