"""
Steganography Detection UI Section
===================================
Streamlit UI component for the Detect Stego tab.
Professional SaaS-style layout with animations.
"""

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import logging

from src.ui.reusable_components import (
    create_file_uploader,
    show_error,
    show_success,
    show_warning,
    show_info,
    show_lottie_animation,
    create_metric_cards,
    show_processing_spinner,
    render_step,
    store_processed_image,
    cache_result,
    get_cached_result
)
from .detector import analyze_image_for_steganography

logger = logging.getLogger(__name__)


def show_info_box(title, description, use_cases):
    """Display a consistent info box explaining a feature."""
    with st.expander(f"ℹ️ {title}", expanded=False):
        st.markdown(description)
        st.markdown("**Use Cases:**")
        for use_case in use_cases:
            st.markdown(f"• {use_case}")


def show_steg_detector_section():
    """Display steganography detection analysis with professional UI."""
    
    # Header with animation
    st.markdown("""
        <div class="animate-fade-in-down">
            <h2>🔍 Steganography Detector</h2>
            <p style="color: #8B949E;">Analyze images to detect hidden messages using advanced statistical methods.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main content with tabs
    tab_analyze, tab_results, tab_help = st.tabs(["🔬 Analyze", "📊 Results", "❓ Help"])
    
    # =========================================================================
    # TAB 1: ANALYZE
    # =========================================================================
    with tab_analyze:
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            # Step 1: Upload
            render_step(1, "Upload Image to Analyze")
            
            st.markdown("""
                <div class="card animate-fade-in">
                    <div class="card-header">📤 Image Upload</div>
                </div>
            """, unsafe_allow_html=True)
            
            suspicious_file = create_file_uploader(file_type="images", key="suspicious_img_detect")
            
            if suspicious_file:
                try:
                    suspicious_image = Image.open(suspicious_file)
                    
                    # Store in session state
                    st.session_state.detection_image = suspicious_image
                    
                    # Display image info
                    st.image(suspicious_image, caption="Image to Analyze", use_container_width=True)
                    
                    # Image metadata
                    st.markdown(f"""
                        <div class="card card-info" style="margin-top: 1rem;">
                            <strong>Image Info:</strong><br>
                            📐 Size: {suspicious_image.size[0]} × {suspicious_image.size[1]} px<br>
                            🎨 Mode: {suspicious_image.mode}<br>
                            📁 Format: {suspicious_image.format or 'Unknown'}
                        </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    show_error(f"Failed to load image: {str(e)}")
            else:
                # Show upload animation placeholder
                st.markdown("""
                    <div class="card" style="text-align: center; padding: 2rem;">
                        <p style="color: #8B949E; font-size: 1.1rem;">
                            📤 Drag and drop an image or click to browse
                        </p>
                        <p style="color: #6E7681; font-size: 0.9rem;">
                            Supported formats: PNG, JPG, BMP
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Step 2: Settings
            render_step(2, "Detection Settings")
            
            st.markdown("""
                <div class="card animate-fade-in stagger-1">
                    <div class="card-header">⚙️ Configuration</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Sensitivity slider
            sensitivity = st.slider(
                "Detection Sensitivity",
                min_value=1,
                max_value=10,
                value=5,
                help="Higher values detect more subtle patterns but may have more false positives"
            )
            
            # Sensitivity indicator
            if sensitivity < 4:
                sensitivity_label = "🟢 Low (fewer false positives)"
                sensitivity_color = "#238636"
            elif sensitivity < 7:
                sensitivity_label = "🟡 Balanced (recommended)"
                sensitivity_color = "#D29922"
            else:
                sensitivity_label = "🔴 High (strict detection)"
                sensitivity_color = "#F85149"
            
            st.markdown(f"""
                <div style="padding: 0.5rem; background: rgba(0,0,0,0.2); border-radius: 6px; margin-top: 0.5rem;">
                    <span style="color: {sensitivity_color}; font-weight: 600;">{sensitivity_label}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Detection methods info
            with st.expander("🔬 Detection Methods Used"):
                st.markdown("""
                **This analyzer checks for:**
                
                1. **LSB Terminator** - Looks for encoding stop markers
                2. **DCT Analysis** - Checks Y-channel for DCT patterns  
                3. **Chi-Square Attack** - Statistical pixel pair analysis
                4. **Bit Ratio Analysis** - 0/1 distribution in LSB
                5. **Autocorrelation** - Adjacent pixel randomness
                6. **ASCII Pattern** - Text characters in hidden data
                """)
            
            st.divider()
            
            # Analyze button
            analyze_btn = st.button(
                "🔎 Analyze Image",
                use_container_width=True,
                type="primary",
                disabled=not suspicious_file
            )
            
            if analyze_btn and suspicious_file:
                _run_analysis(suspicious_image, sensitivity)
    
    # =========================================================================
    # TAB 2: RESULTS
    # =========================================================================
    with tab_results:
        if "detection_results" in st.session_state and st.session_state.detection_results:
            _display_results(st.session_state.detection_results)
        else:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 3rem;">
                    <p style="font-size: 3rem; margin-bottom: 1rem;">📊</p>
                    <p style="color: #8B949E; font-size: 1.1rem;">
                        No analysis results yet
                    </p>
                    <p style="color: #6E7681; font-size: 0.9rem;">
                        Upload an image and click "Analyze" to see detection results
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 3: HELP
    # =========================================================================
    with tab_help:
        st.markdown("""
            <div class="card animate-fade-in">
                <div class="card-header">📖 How Detection Works</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### Understanding Steganography Detection
        
        This tool analyzes images to determine if they contain hidden data. 
        It uses multiple detection methods to identify patterns left by common 
        steganography techniques.
        
        ---
        
        ### Detection Methods Explained
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔍 LSB Analysis**
            - Examines least significant bits
            - Looks for terminator patterns
            - Detects sequential embedding
            
            **📊 Statistical Analysis**
            - Chi-square test on pixel pairs
            - Entropy measurements
            - Bit plane randomness
            """)
        
        with col2:
            st.markdown("""
            **🔬 DCT Analysis**
            - Checks Y-channel coefficients
            - Frequency domain patterns
            - JPEG-compatible detection
            
            **🔐 Pattern Recognition**
            - ASCII text detection
            - Correlation analysis
            - Terminator sequences
            """)
        
        st.divider()
        
        st.markdown("""
        ### Interpreting Results
        
        | Score | Verdict | Meaning |
        |-------|---------|---------|
        | 0-25% | 🟢 Clean | No hidden data detected |
        | 25-50% | 🟡 Uncertain | Possible anomalies |
        | 50-100% | 🔴 Suspicious | Likely contains hidden data |
        
        ---
        
        ### Tips for Best Results
        
        1. **Use original images** - Compression may remove hidden data
        2. **PNG format preferred** - Lossless format preserves data
        3. **Adjust sensitivity** - Higher for subtle detection
        4. **Multiple tests** - Analyze at different sensitivity levels
        """)


def _run_analysis(image: Image.Image, sensitivity: int):
    """Run the steganography detection analysis."""
    try:
        with st.spinner("🔬 Analyzing image for hidden content..."):
            # Progress indicator
            progress_bar = st.progress(0)
            status = st.empty()
            
            status.text("Converting image...")
            progress_bar.progress(20)
            
            arr = np.array(image.convert("RGB"))
            
            status.text("Running detection algorithms...")
            progress_bar.progress(50)
            
            detection_score, analysis_data = analyze_image_for_steganography(arr, sensitivity)
            
            status.text("Generating report...")
            progress_bar.progress(80)
            
            # Store results in session state
            st.session_state.detection_results = {
                "score": detection_score,
                "data": analysis_data,
                "sensitivity": sensitivity,
                "image_size": image.size
            }
            
            progress_bar.progress(100)
            status.text("Analysis complete!")
            
            # Clear progress after short delay
            import time
            time.sleep(0.5)
            progress_bar.empty()
            status.empty()
            
            # Show quick result
            if detection_score < 25:
                show_success("Analysis complete! Image appears clean.")
            elif detection_score < 50:
                show_warning("Analysis complete! Some anomalies detected.")
            else:
                show_error("Analysis complete! Hidden data likely present!")
            
            st.info("📊 Switch to the **Results** tab for detailed analysis.")
            
    except Exception as e:
        show_error(f"Detection error: {str(e)}")
        logger.error(f"Detection error: {str(e)}")


def _display_results(results: dict):
    """Display the detection results with visualizations."""
    score = results["score"]
    data = results["data"]
    sensitivity = results["sensitivity"]
    
    # Determine verdict
    if score < 25:
        emoji = "🟢"
        verdict = "Clean Image"
        verdict_color = "#238636"
        explanation = "This image shows natural patterns consistent with unmodified images. No steganographic content detected."
    elif score < 50:
        emoji = "🟡"
        verdict = "Uncertain"
        verdict_color = "#D29922"
        explanation = "Image shows some statistical anomalies that could indicate hidden data, but could also be due to image processing or compression."
    else:
        emoji = "🔴"
        verdict = "Suspicious - Hidden Data Likely"
        verdict_color = "#F85149"
        explanation = "Image shows strong indicators of steganographic embedding. Hidden message likely present."
    
    # Main score display
    st.markdown(f"""
        <div class="result-container animate-scale-in" style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem;">{emoji}</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {verdict_color};">{score:.1f}%</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #C9D1D9; margin-top: 0.5rem;">{verdict}</div>
            <p style="color: #8B949E; margin-top: 1rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                {explanation}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Detailed metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="card">
                <div class="card-header">📊 Detection Metrics</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Create DataFrame for display
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <div class="card-header">📈 Score Breakdown</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Visual score breakdown
        for item in data:
            metric_name = item.get("Metric", "Unknown")
            metric_value = item.get("Value", "N/A")
            
            # Determine if this metric contributed to detection
            if "FOUND" in str(metric_value) or "SUSPICIOUS" in str(metric_value) or "TEXT" in str(metric_value):
                indicator = "🔴"
            elif "borderline" in str(metric_value).lower():
                indicator = "🟡"
            else:
                indicator = "🟢"
            
            st.markdown(f"{indicator} **{metric_name}:** {metric_value}")
    
    st.divider()
    
    # Analysis summary
    st.markdown("""
        <div class="card card-info">
            <div class="card-header">📋 Analysis Summary</div>
        </div>
    """, unsafe_allow_html=True)
    
    metrics = {
        "Detection Score": f"{score:.1f}%",
        "Sensitivity": f"{sensitivity}/10",
        "Methods Checked": len(data)
    }
    create_metric_cards(metrics)
    
    # Export options
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        # Export as JSON
        import json
        report_json = json.dumps({
            "score": score,
            "verdict": verdict,
            "sensitivity": sensitivity,
            "metrics": data
        }, indent=2)
        
        st.download_button(
            label="📥 Download Report (JSON)",
            data=report_json,
            file_name="detection_report.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export as CSV
        df = pd.DataFrame(data)
        csv_data = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Metrics (CSV)",
            data=csv_data,
            file_name="detection_metrics.csv",
            mime="text/csv",
            use_container_width=True
        )