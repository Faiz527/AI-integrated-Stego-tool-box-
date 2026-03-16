# Key Component Interactions & Data Flows

## 1. ENCODING WORKFLOW (from streamlit_app.py)

User Upload Image → show_encode_section()
    ↓
UI receives: image, message, method (LSB/DCT/DWT), optional encryption password
    ↓
OPTIONAL: Encrypt message
    from src.encryption.encryption import encrypt_message
    encrypted_msg = encrypt_message(message, password)  → Base64 string
    ↓
ENCODE using selected method:
    from src.stego import encode_image, encode_dct, encode_dwt
    
    if method == "LSB":
        encoded_img = encode_image(img, encrypted_msg or message, filter_type)
    elif method == "Hybrid DCT":
        encoded_img = encode_dct(img, encrypted_msg or message)
    elif method == "Hybrid DWT":
        encoded_img = encode_dwt(img, encrypted_msg or message)
    ↓
LOG to database:
    from src.db.db_utils import log_operation, log_activity
    log_operation(user_id, method, input_file, output_file, len(message))
    log_activity(user_id, "encode", f"Encoded {len(message)} bytes via {method}")
    ↓
RETURN: Encoded PIL.Image + download link

## 2. DECODING WORKFLOW

User Upload Encoded Image → show_decode_section()
    ↓
OPTIONAL: Auto-detect method
    from src.stego.method_detection import detect_encoding_method
    detected_method = detect_encoding_method(image)  → Returns 'LSB'/'DCT'/'DWT'
    ↓
DECODE using method:
    from src.stego import decode_image, decode_dct, decode_dwt
    
    if method == "LSB":
        decoded_bytes = decode_image(img)
    elif method == "DCT":
        decoded_bytes = decode_dct(img)
    elif method == "DWT":
        decoded_bytes = decode_dwt(img)
    ↓
OPTIONAL: Decrypt if encrypted
    from src.encryption.encryption import decrypt_message
    decoded_msg = decrypt_message(decoded_bytes, password_provided)
    ↓
DISPLAY: Decoded message text
    ↓
LOG: log_operation(...), log_activity(...)

## 3. BATCH PROCESSING WORKFLOW

User Uploads ZIP → show_batch_processing_section()
    ↓
extract_zip(zip_file_path) [batch_processing/zip_handler.py]
    ↓
Selected mode: UNIFORM or PACKETIZED
    ↓
[UNIFORM MODE]:
    batch_encode_images(
        image_paths=[img1, img2, ...],
        secret_message=message,
        methods=['LSB', 'DCT', 'DWT'],
        batch_mode="uniform"
    )
    → Returns dict with results dict['LSB'] = [(img1_out, status), (img2_out, status), ...]
    
[PACKETIZED MODE]:
    from src.batch_processing.packet_handler import packetize_message
    packets = packetize_message(message, num_images)  → len(num_images) packet strings
    
    For each packet + image:
        encode_image(image, packet_data, method)
    
    Returns packet_map dict for reconstruction clue

    ↓
generate_batch_report(results)
    ↓
RETURN: ZIP of encoded images + HTML report + CSV summary

## 4. ML STEGANALYSIS WORKFLOW

User Upload Image + Sensitivity Slider → show_steg_detector_section()
    ↓
from src.detect_stego.ml_detector import analyze_image_for_steganography
analyze_image_for_steganography(img_array, sensitivity=1-10)
    ↓
INSIDE analyze_image_for_steganography():
    detector = get_detector()  [singleton - loads "stego_detector_rf.pkl"]
        ↓
        if model not trained:
            return "⚠️ Model not trained" message
        ↓
    prediction, confidence = detector.predict(img_array, return_confidence=True)
        ↓
        INSIDE predict():
            features = detector.extract_features(img_array)  [9 features]
            feat_scaled = scaler.transform(features)
            pred_class = model.predict(feat_scaled)  [0=clean, 1=stego]
            prob = model.predict_proba(feat_scaled)[1]  [stego probability]
    ↓
    Adjust score by sensitivity:
        final_score = confidence * (sensitivity / 5.0)
        final_score = clip(final_score, 0, 100)
    ↓
    Determine verdict:
        if final_score >= 70: "STEGO DETECTED ⚠️"
        elif final_score >= 40: "SUSPICIOUS 🟡"
        else: "CLEAN IMAGE ✅"
    ↓
RETURN: (final_score, analysis_data_table)

## 5. ML MODEL TRAINING WORKFLOW

User Clicks "Train Model" Tab → _show_training_section()
    ↓
User selects:
    - n_samples (default: 200)
    - image_sizes [(256,256), (512,512), ...]
    - methods to include ['LSB', 'DCT', 'DWT']
    - validation_split (default: 0.2)
    ↓
CLICK "Train" button → _run_model_training(...)
    ↓
from src.detect_stego.train_ml_detector import train_detector
train_detector(n_samples=200, image_size=(256,256), save_path=None)
    ↓
INSIDE train_detector():
    cover_images = generate_training_data(n_samples)[0]  [synthetic clean images]
    stego_images = generate_training_data(n_samples)[1]  [synthetic with embedding]
        ↓
        For each:
            generate_random_image(size, seed) → numpy RGB array
            generate_stego_image(cover_img, method) → embedded version
    ↓
    detector.train(cover_images, stego_images, validation_split)
        ↓
        INSIDE StegoDetectorML.train():
            Extract features from all images [feature_extraction.py]
            Split: X_train, X_val (80/20)
            Fit StandardScaler on X_train
            Train RandomForestClassifier (200 trees)
            Evaluate: train/val accuracy, precision, recall, F1, confusion matrix
            Save: model → "models/stego_detector_rf.pkl"
                  scaler → "models/stego_detector_rf_scaler.pkl"
    ↓
    Return metrics dict: {'train_accuracy': 0.95, 'val_accuracy': 0.92, ...}
    ↓
DISPLAY: Training metrics table + confusion matrix

## 6. AUTHENTICATION & USER TRACKING

User Visits streamlit_app → render_sidebar()
    ↓
Check st.session_state.logged_in
    ↓
NOT logged in → show_auth_section()
    ↓
[REGISTER panel]:
    User enters: username, password, confirm_password
    ↓
    CLICK "Register":
        from src.db.db_utils import add_user
        add_user(username, password)
            ↓
            Hash password: bcrypt.hashpw(password, salt)
            INSERT INTO users (username, password_hash)
            Return: success/error
    ↓
[LOGIN panel]:
    User enters: username, password
    ↓
    CLICK "Login":
        from src.db.db_utils import verify_user
        result = verify_user(username, password)
            ↓
            Check rate limit (5 attempts/5 min)
            Retrieve password_hash from DB
            bcrypt.checkpw(password, hash) → boolean
            Return: { 'success': bool, 'user_id': int, 'username': str }
    ↓
    If success:
        st.session_state.logged_in = True
        st.session_state.user_id = result['user_id']
        ↓
    Each operation: log_activity(user_id, action, details)

## 7. ANALYTICS & STATISTICS FLOW

User Visits "Analytics" Tab → show_analytics_section()
    ↓
Load user stats:
    from src.analytics.stats import get_statistics_summary
    stats = get_statistics_summary(user_id)
        ↓
        Fetches:
            - Operation count
            - Method distribution
            - Encode/decode counts
            - Message size stats
            - Timeline data (per day)
    ↓
Display Summary Metrics:
    - Total operations
    - Methods used (pie chart)
    - Encode vs Decode (bar chart)
    - Timeline (line chart)
    ↓
Display Activity Charts:
    - Hourly heatmap (hour vs day-of-week)
    - Performance trend (rolling stats)
    - Size distribution (histogram)
    ↓
Display Activity Log:
    from src.analytics.stats import get_user_activity_log
    df = get_user_activity_log(user_id, limit=50)
    Display as Streamlit dataframe

## 8. Image Array Format
- Shape: (height, width, 3) for RGB
- Dtype: uint8 (0-255 range)
- Channels order: RGB (PIL) or BGR (OpenCV - watch for mismatch!)

## 9. Encrypted Message Format (Base64)
salt(16B) || IV(16B) || ciphertext(NB) || HMAC(32B)
    ↓
All packed as binary, then base64 encoded

## 10. Packet Format (Packetized Mode)
|||PACKET_HEADER|||{ "packet_id": 0, "total_packets": 3, "payload_length": 100, "checksum": "abc123" }|||PAYLOAD|||actual_data_here