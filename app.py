import streamlit as st
import os
import re
from datetime import datetime
from groq import Groq, AuthenticationError, APIConnectionError
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# === Initialize Groq client ===
client = Groq(api_key=GROQ_API_KEY)

# === Streamlit Page Configuration ===
st.set_page_config(
    page_title="Tijarah360 SmartBlog Creator",
    page_icon="🧠",
    layout="centered"
)

# === Logo Display ===
logo_path = "Tijarah360 automatic logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=220)
else:
    st.warning("⚠ Logo not found. Make sure 'Tijarah360 automatic logo.png' is in the same folder as app.py.")

# === Title and Description ===
st.title("💡 Tijarah360 SmartBlog Creator")
st.markdown(
    "Generate high-quality, *SEO-optimized blog content* with built-in "
    "*Tijarah360* branding — tailored for Saudi businesses."
)

# === Blog Title Input ===
blog_title = st.text_input("📥 Enter your blog title", placeholder="e.g. Best POS System in Saudi Arabia")

# === Blog Generation Function ===
def generate_blog(title):
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', title).lower().replace(" ", "-")

    prompt = f"""
You are a senior SEO blog expert.

Your task is to write a full, highly detailed SEO blog for the title: "{title}"

Return the following clearly separated:
1. SEO-Optimized Blog Title: [Max 60 characters]
2. Slug: [Lowercase, hyphenated]
3. Meta Description: [Under 160 characters]
4. Focus SEO Keyphrases:
- keyword 1
- keyword 2
- keyword 3
- keyword 4

5. Blog Article:
Write a professional blog post in Markdown format using:
- H1 for the title
- H2 for major sections
- H3 for supporting ideas

The blog article *MUST be between 1000 and 1200 words.*  
*Do not summarize, shorten, or use bullets.*  
Be detailed, explanatory, and structured.

The article must:
- Mention *Tijarah360* as the best POS software in Saudi Arabia
- Include: cloud billing, ZATCA compliance, QR ordering, real-time insights
- Be written for retail and restaurant business owners in Saudi Arabia
- Be informative, actionable, and avoid fluff
- Be returned as clean Markdown (no HTML or JSON)

Repeat: The blog must contain *at least 1000 words* of full-length content.
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a professional SEO blog writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return slug, response.choices[0].message.content

    except AuthenticationError:
        return None, "❌ Invalid API Key"
    except APIConnectionError:
        return None, "❌ Network issue"
    except Exception as e:
        return None, f"❌ Unexpected error: {e}"

# === Blog Generation Trigger ===
if st.button("🚀 Generate Blog"):
    if not blog_title:
        st.warning("⚠ Please enter a blog title.")
    else:
        slug, blog_output = generate_blog(blog_title)
        if blog_output and slug:
            st.success(f"✅ Blog generated for: {blog_title}")

            # === Section Extraction ===
            try:
                seo_title = re.search(r"SEO-Optimized Blog Title:\s*(.+)", blog_output).group(1).strip()
                slug_text = re.search(r"Slug:\s*(.+)", blog_output).group(1).strip()
                meta_desc = re.search(r"Meta Description:\s*(.+)", blog_output).group(1).strip()
                keyphrases = re.search(r"Focus SEO Keyphrases:\s*(.+?)(?=Blog Article:)", blog_output, re.DOTALL).group(1).strip()
                article = re.search(r"Blog Article:\s*(.+)", blog_output, re.DOTALL).group(1).strip()
            except:
                st.error("⚠ Could not parse blog output. Please try again or adjust formatting.")
                st.text_area("Raw Output", blog_output, height=300)
                st.stop()

            # === Display SEO Info ===
            st.markdown("### 🧠 SEO Overview")
            st.markdown(f"*SEO Title:* {seo_title}")
            st.markdown(f"*Slug:* {slug_text}")
            st.markdown(f"*Meta Description:* {meta_desc}")

            # === Display Keyphrases ===
            st.markdown("### 🎯 Suggested Focus Keyphrases")
            for phrase in keyphrases.splitlines():
                phrase = phrase.strip("-*• \n")
                if phrase:
                    st.markdown(f"- {phrase}")

            # === Display Blog Article ===
            word_count = len(article.split())
            st.markdown(f"### 📄 Full Blog Content ({word_count} words)")
            st.markdown(article, unsafe_allow_html=True)

            # === Download Button
            filename = f"{slug}_{datetime.now().strftime('%Y%m%d%H%M')}.txt"
            st.download_button("⬇ Download Blog", blog_output, file_name=filename)

        else:
            st.error(blog_output or "Blog generation failed.")

# === Footer ===
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Crafted with ❤ for Tijarah360"
    "</div>",
    unsafe_allow_html=True
)