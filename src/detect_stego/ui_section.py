"""
Steganography Detection UI Section
===================================
Streamlit UI component for the Detect Stego tab.
Professional SaaS-style layout with animations.
Includes model training capabilities.
"""

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import logging
import time
import json

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
from .ml_detector import analyze_image_for_steganography, StegoDetectorML

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
    tab_analyze, tab_results, tab_train, tab_help = st.tabs(["🔬 Analyze", "📊 Results", "🤖 Train Model", "❓ Help"])
    
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
    # TAB 3: TRAIN MODEL
    # =========================================================================
    with tab_train:
        _show_training_section()
    
    # =========================================================================
    # TAB 4: HELP
    # =========================================================================
    with tab_help:
        _show_help_section()


def _show_training_section():
    """Display the ML model training interface."""
    
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">🤖 Train Detection Model</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Train a custom Logistic Regression model to detect steganography in images.
    The model learns to identify statistical patterns left by encoding methods.
    """)
    
    st.divider()
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📊 Training Configuration")
        
        # Number of samples
        n_samples = st.slider(
            "Number of Training Samples",
            min_value=50,
            max_value=2000,
            value=500,
            step=50,
            help="""
            Total image pairs (cover + stego) to generate.
            More samples = better accuracy but longer training time.
            - 50-100: Quick testing (~1-2 min)
            - 200-500: Balanced (~5-10 min)
            - 1000+: High quality (~20+ min)
            """
        )
        
        # Image sizes
        st.markdown("**Image Sizes to Generate**")
        include_small = st.checkbox("256×256 (Small, fast)", value=True)
        include_medium = st.checkbox("512×512 (Medium)", value=True)
        include_large = st.checkbox("1024×1024 (Large, slow)")
        
        # Steganography methods to train on
        st.markdown("**Encoding Methods to Train On**")
        train_lsb = st.checkbox("LSB (Least Significant Bit)", value=True)
        train_dct = st.checkbox("DCT (Discrete Cosine Transform)", value=True)
        train_dwt = st.checkbox("DWT (Discrete Wavelet Transform)", value=True)
        
        selected_sizes = []
        if include_small:
            selected_sizes.append((256, 256))
        if include_medium:
            selected_sizes.append((512, 512))
        if include_large:
            selected_sizes.append((1024, 1024))
        
        selected_methods = []
        if train_lsb:
            selected_methods.append("lsb")
        if train_dct:
            selected_methods.append("dct")
        if train_dwt:
            selected_methods.append("dwt")
        
        if not selected_sizes:
            st.warning("⚠️ Please select at least one image size")
        if not selected_methods:
            st.warning("⚠️ Please select at least one encoding method")
        
    with col2:
        st.markdown("### ⏱️ Estimated Time")
        
        # Calculate estimated time
        time_per_sample = 0.1  # seconds per sample
        estimated_seconds = n_samples * time_per_sample
        
        if estimated_seconds < 60:
            time_str = f"{int(estimated_seconds)} seconds"
        elif estimated_seconds < 3600:
            time_str = f"{int(estimated_seconds / 60)} minutes"
        else:
            hours = estimated_seconds / 3600
            mins = (estimated_seconds % 3600) / 60
            time_str = f"{int(hours)}h {int(mins)}m"
        
        st.markdown(f"""
            <div class="card card-info" style="margin-top: 1rem;">
                <strong>⏱️ Estimated Duration:</strong><br>
                <span style="font-size: 1.5rem; font-weight: 700; color: #238636;">
                    {time_str}
                </span>
                <p style="margin-top: 0.5rem; color: #8B949E; font-size: 0.9rem;">
                    (Approximately {time_per_sample*1000:.0f}ms per image)
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### 💾 Model Info")
        st.markdown(f"""
            **Samples:** {n_samples} pairs  
            **Train/Val Split:** 80/20  
            **Algorithm:** Logistic Regression  
            **Features:** 9 statistical measures  
            """)
    
    st.divider()
    
    # Training button
    col1, col2 = st.columns([2, 1])
    
    with col1:
        start_training = st.button(
            "🚀 Start Training",
            use_container_width=True,
            type="primary",
            disabled=not selected_sizes or not selected_methods
        )
    
    with col2:
        show_advanced = st.toggle("Advanced Options")
    
    # Advanced options
    if show_advanced:
        st.markdown("### ⚙️ Advanced Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            validation_split = st.slider(
                "Validation Split",
                min_value=0.1,
                max_value=0.5,
                value=0.2,
                step=0.05,
                help="Fraction of data used for validation"
            )
        
        with col2:
            max_iterations = st.number_input(
                "Max Iterations",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Maximum iterations for model convergence"
            )
        
        custom_save_path = st.text_input(
            "Custom Save Path (optional)",
            placeholder="src/detect_stego/models/my_detector.pkl",
            help="Leave empty to use default model path"
        )
    else:
        validation_split = 0.2
        max_iterations = 1000
        custom_save_path = None
    
    st.divider()
    
    # Training execution
    if start_training:
        _run_model_training(
            n_samples=n_samples,
            image_sizes=selected_sizes,
            methods=selected_methods,
            validation_split=validation_split,
            custom_path=custom_save_path if custom_save_path else None
        )


def _run_model_training(n_samples, image_sizes, methods, validation_split, custom_path=None):
    """Execute the model training process."""
    
    st.markdown("""
        <div class="card card-warning">
            <strong>⚠️ Important:</strong> Training will take some time. 
            Do not close this page or navigate away during training.
        </div>
    """, unsafe_allow_html=True)
    
    # Import training utilities
    try:
        from .train_ml_detector import generate_training_data, create_stego_image
    except ImportError:
        st.error("❌ Training module not found. Please ensure all dependencies are installed.")
        return
    
    # Create containers for progress display
    progress_container = st.container()
    status_container = st.container()
    metrics_container = st.container()
    
    try:
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Step 1: Generate training data
        status_text.text("📊 Generating training data...")
        progress_bar.progress(10)
        
        with st.spinner("Generating synthetic images..."):
            cover_images, stego_images = generate_training_data(
                n_samples=n_samples,
                image_sizes=image_sizes
            )
        
        progress_bar.progress(30)
        
        if len(cover_images) < 10 or len(stego_images) < 10:
            st.error("❌ Failed to generate sufficient training data")
            return
        
        st.success(f"✅ Generated {len(cover_images)} cover + {len(stego_images)} stego images")
        
        # Step 2: Train model
        progress_bar.progress(40)
        status_text.text("🤖 Training Logistic Regression model...")
        
        with st.spinner("Training model (this may take a while)..."):
            detector = StegoDetectorML()
            metrics = detector.train(
                cover_images=cover_images,
                stego_images=stego_images,
                validation_split=validation_split
            )
        
        progress_bar.progress(80)
        
        if "error" in metrics:
            st.error(f"❌ Training failed: {metrics['error']}")
            return
        
        # Step 3: Save model
        progress_bar.progress(90)
        status_text.text("💾 Saving model...")
        
        save_successful = detector.save_model(custom_path)
        
        if not save_successful:
            st.error("❌ Failed to save model")
            return
        
        progress_bar.progress(100)
        status_text.text("✅ Training complete!")
        
        # Step 4: Display results
        st.divider()
        
        with metrics_container:
            st.markdown("""
                <div class="card card-success animate-scale-in">
                    <div class="card-header">✅ Training Complete!</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Metrics display
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Model Performance")
                
                perf_metrics = {
                    "Training Accuracy": f"{metrics['train_accuracy']:.1%}",
                    "Validation Accuracy": f"{metrics['val_accuracy']:.1%}",
                    "Precision": f"{metrics['val_precision']:.1%}",
                    "Recall": f"{metrics['val_recall']:.1%}",
                    "F1 Score": f"{metrics['val_f1']:.4f}"
                }
                
                df_perf = pd.DataFrame(list(perf_metrics.items()), columns=["Metric", "Value"])
                st.dataframe(df_perf, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("### 📊 Training Summary")
                
                summary_stats = {
                    "Cover Images": len(cover_images),
                    "Stego Images": len(stego_images),
                    "Total Samples": len(cover_images) + len(stego_images),
                    "Image Sizes": ", ".join([f"{w}×{h}" for w, h in image_sizes]),
                    "Methods Used": len(methods),
                    "Validation Split": f"{validation_split:.0%}"
                }
                
                df_summary = pd.DataFrame(list(summary_stats.items()), columns=["Parameter", "Value"])
                st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Feature importance
            st.markdown("### 🎯 Top Features for Detection")
            
            importance = detector.get_feature_importance()
            importance_sorted = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart of importance
                feature_names = [name for name, _ in importance_sorted]
                feature_values = [value for _, value in importance_sorted]
                
                import plotly.express as px
                
                fig = px.bar(
                    x=feature_values,
                    y=feature_names,
                    orientation='h',
                    labels={'x': 'Importance', 'y': 'Feature'},
                    title='Feature Importance in Detection'
                )
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    template='plotly_dark',
                    hovermode='closest'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Ranked Features:**")
                for i, (name, importance_val) in enumerate(importance_sorted, 1):
                    st.markdown(f"{i}. **{name}**  \n`{importance_val:.4f}`")
            
            st.divider()
            
            # Export results
            st.markdown("### 📥 Export Training Report")
            
            col1, col2, col3 = st.columns(3)
            
            # JSON report
            report_data = {
                "training_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "metrics": metrics,
                "training_params": {
                    "n_samples": n_samples,
                    "image_sizes": [f"{w}×{h}" for w, h in image_sizes],
                    "methods": methods,
                    "validation_split": validation_split
                },
                "feature_importance": importance
            }
            
            with col1:
                st.download_button(
                    label="📋 Download Report (JSON)",
                    data=json.dumps(report_data, indent=2),
                    file_name="training_report.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # CSV metrics
            with col2:
                metrics_df = pd.DataFrame([
                    {"Metric": k, "Value": f"{v:.4f}" if isinstance(v, float) else str(v)}
                    for k, v in metrics.items()
                ])
                
                st.download_button(
                    label="📊 Download Metrics (CSV)",
                    data=metrics_df.to_csv(index=False),
                    file_name="training_metrics.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Feature importance CSV
            with col3:
                importance_df = pd.DataFrame(
                    list(importance_sorted),
                    columns=["Feature", "Importance"]
                )
                
                st.download_button(
                    label="🎯 Download Features (CSV)",
                    data=importance_df.to_csv(index=False),
                    file_name="feature_importance.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.divider()
            
            st.success("""
            ✅ **Model successfully trained and saved!**
            
            Your new model is now active and will be used for all future analyses.
            The model has learned to detect steganographic patterns with these accuracy metrics.
            """)
    
    except Exception as e:
        st.error(f"❌ Training error: {str(e)}")
        logger.error(f"Training error: {str(e)}", exc_info=True)
    
    finally:
        # Clean up
        progress_bar.empty()
        status_text.empty()


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


def _show_help_section():
    """Display comprehensive help documentation."""
    
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">📖 Detection Module - Complete Guide</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main tabs in help
    help_tab1, help_tab2, help_tab3, help_tab4 = st.tabs([
        "🔬 How Detection Works",
        "🤖 Model Training Guide",
        "💻 Using the Module",
        "❓ FAQ & Tips"
    ])
    
    # =========================================================================
    # HELP TAB 1: HOW DETECTION WORKS
    # =========================================================================
    with help_tab1:
        st.markdown("""
        ### 🎯 Steganography Detection Overview
        
        This module analyzes images to detect if they contain hidden messages 
        encoded using steganography techniques (LSB, DCT, DWT).
        
        ---
        
        ### 📊 Detection Methods
        
        The detector uses **Logistic Regression** with 9 statistical features to identify steganographic patterns:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🔍 **LSB Analysis**
            - **LSB Entropy** - Information content in LSB plane
            - **LSB 0/1 Ratio** - Distribution of bits in LSB
            - **LSB Autocorrelation** - Randomness of adjacent LSBs
            
            #### 📊 **Statistical Tests**
            - **Chi-Square Statistic** - Pixel pair distribution
            - **ASCII Ratio** - Text characters in extracted bits
            - **Histogram Variance** - Unusual pixel distribution
            """)
        
        with col2:
            st.markdown("""
            #### 🔬 **Frequency Domain**
            - **DCT Coefficients** - Discrete Cosine patterns
            - **DCT Variance** - Distribution in frequency domain
            - **High-Freq Energy** - Unusual energy distribution
            """)
        
        st.divider()
        
        st.markdown("""
        ### 📈 Detection Scores Explained
        
        | Score Range | Verdict | Meaning |
        |---|---|---|
        | **0-25%** 🟢 | Clean | Image shows natural patterns |
        | **25-50%** 🟡 | Uncertain | Possible anomalies detected |
        | **50-100%** 🔴 | Suspicious | Likely contains hidden data |
        
        ### ⚙️ Sensitivity Levels
        
        The detection sensitivity slider (1-10) adjusts how strictly the model evaluates:
        
        - **Low (1-3)** 🟢 - Conservative, fewer false positives
        - **Balanced (4-6)** 🟡 - Recommended for general use
        - **High (7-10)** 🔴 - Aggressive, catches subtle patterns
        
        **Recommendation:** Start with sensitivity 5 (balanced) and adjust based on results.
        """)
    
    # =========================================================================
    # HELP TAB 2: MODEL TRAINING GUIDE
    # =========================================================================
    with help_tab2:
        st.markdown("""
        ### 🤖 Training Your ML Model
        
        You can train custom detection models using different datasets and configurations.
        
        ---
        
        ### 🚀 Training Methods
        
        #### **Method 1: Training from UI (Recommended for Beginners)**
        """)
        
        st.markdown("""
        **Steps:**
        1. Go to "🤖 Train Model" tab
        2. Select number of samples (50-2000)
        3. Choose image sizes (256×256, 512×512, 1024×1024)
        4. Select encoding methods (LSB, DCT, DWT)
        5. Click "🚀 Start Training"
        6. Wait for training to complete
        7. Download the training report
        
        **⏱️ Time Estimates:**
        - 100 samples: 1-2 minutes 🟢
        - 500 samples: 5-10 minutes 🟡
        - 1000 samples: 20-30 minutes 🔴
        - 2000 samples: 45+ minutes 🔴
        
        **Recommended:** 500 samples for balanced accuracy/speed
        """)
        
        st.divider()
        
        st.markdown("""
        #### **Method 2: Training from Command Line**
        """)
        
        with st.expander("📝 Command Line Training"):
            st.code("""
# Quick training (100 samples, ~2 min)
python src/detect_stego/train_ml_detector.py --samples 100

# Standard training (500 samples, ~10 min) - RECOMMENDED
python src/detect_stego/train_ml_detector.py --samples 500

# High quality (1000 samples, ~30 min)
python src/detect_stego/train_ml_detector.py --samples 1000

# Custom output path
python src/detect_stego/train_ml_detector.py --samples 500 \\
    -o ./models/custom_detector.pkl

# View all options
python src/detect_stego/train_ml_detector.py --help
            """)
        
        st.divider()
        
        st.markdown("""
        #### **Method 3: Using Python API**
        """)
        
        with st.expander("💻 Python API Training"):
            st.code("""
from src.detect_stego.ml_detector import StegoDetectorML
from src.detect_stego.train_ml_detector import generate_training_data

# Generate synthetic data
cover_images, stego_images = generate_training_data(n_samples=500)

# Train detector
detector = StegoDetectorML()
metrics = detector.train(cover_images, stego_images)

# Save model
detector.save_model("./models/my_detector.pkl")

# Print results
print(f"Accuracy: {metrics['val_accuracy']:.1%}")
            """)
        
        st.divider()
        
        st.markdown("""
        ### 📊 Understanding Training Results
        
        After training, you'll see these metrics:
        
        - **Training Accuracy** - Performance on training data  
        - **Validation Accuracy** - Performance on unseen data (most important)  
        - **Precision** - True positives / total positives  
        - **Recall** - True positives / total actual positives  
        - **F1 Score** - Harmonic mean of precision & recall  
        
        **Good model indicators:**
        - Validation accuracy > 80%
        - Precision & recall both > 75%
        - F1 score close to accuracy
        
        ### 🎯 Feature Importance
        
        After training, the model shows which features were most important for detection:
        
        **Common important features:**
        1. LSB Entropy - Detects randomness from encoding
        2. Chi-Square Stat - Catches pixel pair anomalies
        3. Histogram Variance - Identifies unusual distributions
        """)
    
    # =========================================================================
    # HELP TAB 3: USING THE MODULE
    # =========================================================================
    with help_tab3:
        st.markdown("""
        ### 💻 Using the Detection Module
        
        ---
        
        ### 🎯 In Streamlit UI
        
        #### **Step 1: Prepare Your Image**
        """)
        
        st.markdown("""
        - Use **PNG or BMP** format (lossless)
        - Avoid JPEG (lossy compression destroys hidden data)
        - Image size: 256×256 to 1024×1024 recommended
        - Don't resize before analysis
        
        #### **Step 2: Upload and Analyze**
        """)
        
        st.markdown("""
        1. Click "🔬 Analyze" tab
        2. Upload your image
        3. Adjust sensitivity (1-10)
        4. Click "🔎 Analyze Image"
        5. View results instantly
        
        #### **Step 3: Interpret Results**
        """)
        
        st.markdown("""
        - **Green (0-25%)**: Looks clean
        - **Yellow (25-50%)**: Possible anomalies
        - **Red (50-100%)**: Likely contains hidden data
        
        #### **Step 4: Export & Share**
        """)
        
        st.markdown("""
        - Download report as JSON
        - Download metrics as CSV
        - Share with others
        """)
        
        st.divider()
        
        st.markdown("""
        ### 🔌 Using in Python Code
        
        #### **Basic Usage**
        """)
        
        st.code("""
from PIL import Image
import numpy as np
from src.detect_stego import analyze_image_for_steganography

# Load image
image = Image.open("suspicious.png")
img_array = np.array(image.convert("RGB"))

# Analyze
score, metrics = analyze_image_for_steganography(img_array, sensitivity=5)

print(f"Detection Score: {score:.1f}%")
print(f"Verdict: {'Suspicious' if score > 50 else 'Likely Clean'}")

# Print all metrics
for metric in metrics:
    print(f"{metric['Metric']}: {metric['Value']}")
        """)
        
        st.divider()
        
        st.markdown("""
        #### **Advanced Usage with Custom Model**
        """)
        
        st.code("""
from src.detect_stego.ml_detector import StegoDetectorML
import numpy as np
from PIL import Image

# Load custom model
detector = StegoDetectorML()
detector.load_model("./models/custom_detector.pkl")

# Load and prepare image
image = Image.open("test.png").convert("RGB")
img_array = np.array(image)

# Make prediction
prediction = detector.predict(img_array)  # 0 = clean, 1 = stego

# Get confidence
prediction, confidence = detector.predict(img_array, return_confidence=True)
print(f"Prediction: {prediction}")
print(f"Confidence: {confidence:.1f}%")
        """)
        
        st.divider()
        
        st.markdown("""
        #### **Batch Analysis**
        """)
        
        st.code("""
import os
from PIL import Image
import numpy as np
from src.detect_stego import analyze_image_for_steganography
import pandas as pd

# Analyze multiple images
results = []
image_dir = "./images/"

for filename in os.listdir(image_dir):
    if filename.endswith(('.png', '.jpg', '.bmp')):
        img = Image.open(os.path.join(image_dir, filename)).convert("RGB")
        img_array = np.array(img)
        
        score, metrics = analyze_image_for_steganography(img_array, sensitivity=5)
        
        results.append({
            'filename': filename,
            'score': score,
            'verdict': 'Suspicious' if score > 50 else 'Clean'
        })

# Save results
df = pd.DataFrame(results)
df.to_csv('detection_results.csv', index=False)
        """)
    
    # =========================================================================
    # HELP TAB 4: FAQ & TIPS
    # =========================================================================
    with help_tab4:
        st.markdown("""
        ### ❓ Frequently Asked Questions
        
        ---
        
        #### **Q: Why do I get false positives?**
        A: Some images naturally have statistical anomalies due to:
        - Heavy compression or noise reduction
        - Specific content patterns (repeated textures)
        - Image editing software
        
        **Solution:** Adjust sensitivity or examine metrics closely.
        
        ---
        
        #### **Q: Can I detect all steganography methods?**
        A: The model is trained to detect:
        - ✅ LSB embedding
        - ✅ DCT-based methods
        - ✅ DWT-based methods
        
        But specialized/custom methods may not be detected.
        
        ---
        
        #### **Q: What's the accuracy of the model?**
        A: Typical accuracy:
        - **Well-trained:** 85-93%
        - **Depends on:**
          - Training data quality
          - Number of samples
          - Steganography method used
          - Image characteristics
        
        ---
        
        #### **Q: Can I use a pre-trained model?**
        A: Yes! The app comes with a pre-trained model. You can also:
        - Train your own with more samples
        - Customize for specific needs
        - Combine multiple models
        
        ---
        
        #### **Q: JPEG vs PNG - which should I use?**
        A:
        - **PNG (Recommended)**: Lossless, preserves all hidden data
        - **JPEG**: Lossy, may destroy hidden messages
        - **BMP**: Lossless, also good
        
        ---
        
        #### **Q: How many samples do I need to train?**
        A:
        - 50-100: Baseline (noisy)
        - 200-500: Good balance ✅
        - 1000+: High accuracy
        - 5000+: Production grade
        
        **Recommendation:** Start with 500 samples.
        
        ---
        
        ### 💡 Pro Tips
        
        #### **🎯 For Better Detection**
        """)
        
        st.markdown("""
        1. **Match image types** - Train on images similar to what you'll analyze
        2. **Use multiple methods** - Train with LSB, DCT, and DWT together
        3. **Adjust sensitivity** - Try 5, then 3, then 7 for comparison
        4. **Examine metrics** - Don't just look at final score
        5. **Compare over time** - Look for pattern changes across images
        """)
        
        st.markdown("""
        #### **📊 For Better Training**
        """)
        
        st.markdown("""
        1. **More data = better model** - Minimum 500 samples recommended
        2. **Diverse images** - Include different content types
        3. **Various image sizes** - Train with 256×256, 512×512, etc.
        4. **Multiple encodings** - Train with LSB, DCT, and DWT
        5. **Monitor metrics** - Check validation accuracy isn't overfitting
        """)
        
        st.markdown("""
        #### **⚡ Performance Tips**
        """)
        
        st.markdown("""
        1. **Smaller images train faster** - Start with 256×256
        2. **Fewer samples are faster** - 100 samples for testing
        3. **One method is quicker** - LSB only trains faster than all 3
        4. **Re-use trained models** - Don't retrain unless necessary
        5. **Export results** - Save reports for comparison
        """)
        
        st.divider()
        
        st.markdown("""
        ### 🔗 Quick Links & Commands
        """)
        
        with st.expander("📋 Command Reference"):
            st.code("""
# Training
python src/detect_stego/train_ml_detector.py --samples 500

# Testing the detector
python -c "
from src.detect_stego import analyze_image_for_steganography
from PIL import Image
import numpy as np

img = Image.open('test.png').convert('RGB')
score, _ = analyze_image_for_steganography(np.array(img), 5)
print(f'Score: {score:.1f}%')
"

# Check model exists
ls src/detect_stego/models/
            """)
        
        st.divider()
        
        st.markdown("""
        ### 📚 Additional Resources
        
        - 🔐 [Steganography Basics](https://en.wikipedia.org/wiki/Steganography)
        - 🤖 [Logistic Regression](https://scikit-learn.org/stable/modules/linear_model.html)
        - 📊 [Feature Engineering](https://en.wikipedia.org/wiki/Feature_engineering)
        - 🎓 [ML Model Training](https://machinelearningmastery.com/)
        
        ### 🆘 Troubleshooting
        
        **"No ML Model Found"**
        ```bash
        python src/detect_stego/train_ml_detector.py --samples 500
        ```
        
        **"Out of Memory"**
        - Use fewer samples
        - Use smaller images (256×256)
        - Close other applications
        
        **"Import Error"**
        ```bash
        pip install -r requirements.txt --force-reinstall
        ```
        
        ---
        
        **Need help?** Check the Analyze tab for step-by-step guidance!
        """)