"""
Watermarking UI Section
=======================
Streamlit UI for the watermarking feature.
"""
import logging
from io import BytesIO
from typing import Optional

import streamlit as st
from PIL import Image

from .watermark import apply_text_watermark, apply_lsb_watermark, apply_alpha_blending_watermark
from src.ui.reusable_components import create_file_uploader, show_error, show_success, render_step

logger = logging.getLogger(__name__)


def render_section_header(icon, title, description):
    """Render a consistent section header."""
    st.markdown(f"""
        <div class="animate-fade-in-down">
            <h2>{icon} {title}</h2>
            <p style="color: #8B949E; margin-bottom: 1rem;">{description}</p>
        </div>
    """, unsafe_allow_html=True)


def show_watermarking_section():
    """Display watermarking with professional styling."""
    
    render_section_header("💧", "Watermarking", "Add visible watermarks to protect your images")
    
    st.divider()
    
    tab_apply, tab_help = st.tabs(["🖼️ Apply Watermark", "❓ Help"])
    
    with tab_apply:
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            render_step(1, "Upload Image")
            
            st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
            image_file = create_file_uploader(file_type="images", key="watermark_img")
            
            if image_file:
                original = Image.open(image_file)
                st.image(original, caption="Original Image", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            render_step(2, "Watermark Settings")
            
            st.markdown('<div class="card animate-fade-in stagger-1">', unsafe_allow_html=True)
            
            watermark_text = st.text_input(
                "Watermark Text",
                value="© Your Name",
                placeholder="Enter watermark text"
            )
            
            font_size = st.slider("Font Size", 10, 100, 30)
            
            position = st.selectbox(
                "Position",
                ["top-left", "center", "bottom-right"],
                index=2
            )
            
            opacity = st.slider("Opacity", 50, 255, 180)
            
            text_color_hex = st.color_picker("Color", "#FFFFFF")
            text_color = tuple(int(text_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if image_file and watermark_text:
                if st.button("💧 Apply Watermark", use_container_width=True, type="primary"):
                    _apply_watermark(image_file, watermark_text, font_size, position, text_color, opacity)
    
    with tab_help:
        st.markdown("""
        ### About Watermarking
        
        Watermarking adds visible text to your images for:
        - Copyright protection
        - Brand identification
        - Ownership marking
        
        **Tips:**
        - Use semi-transparent watermarks
        - Position in corners to be less intrusive
        - Choose contrasting colors for visibility
        """)


def _apply_watermark(image_file, text, font_size, position, color, opacity):
    """Apply watermark to image."""
    try:
        with st.spinner("Applying watermark..."):
            original = Image.open(image_file)
            
            watermarked = apply_text_watermark(
                image=original,
                watermark_text=text,
                font_size=font_size,
                position=position,
                text_color=color,
                opacity=opacity
            )
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("**Original**")
                st.image(original, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card card-success">', unsafe_allow_html=True)
                st.markdown("**Watermarked**")
                st.image(watermarked, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Download button
            buf = BytesIO()
            watermarked.save(buf, format="PNG")
            buf.seek(0)
            
            st.download_button(
                label="⬇️ Download Watermarked Image",
                data=buf.getvalue(),
                file_name="watermarked.png",
                mime="image/png",
                use_container_width=True,
                type="primary"
            )
            
            show_success("Watermark applied!")
            
    except Exception as e:
        show_error(f"Watermark error: {str(e)}")