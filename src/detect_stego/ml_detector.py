"""
Machine Learning-based Steganography Detector
==============================================
Uses Logistic Regression to detect hidden messages in images.
Single source of truth for ML detection.
"""

import numpy as np
import logging
import pickle
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from scipy.fftpack import dct
from PIL import Image

logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "stego_detector_lr.pkl"
SCALER_PATH = MODEL_DIR / "stego_detector_scaler.pkl"

# Global detector instance
_detector_instance = None


def get_detector():
    """Get or initialize the detector instance (singleton pattern)."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = StegoDetectorML()
        if not _detector_instance.load_model():
            logger.warning("Pre-trained model not found. Run: python train_ml_detector.py")
    return _detector_instance


def analyze_image_for_steganography(img_array, sensitivity):
    """
    Analyze image for steganography using ML model.
    
    Args:
        img_array: numpy array of image (RGB)
        sensitivity: Detection sensitivity (1-10)
    
    Returns:
        tuple: (detection_score, analysis_data)
    """
    try:
        detector = get_detector()
        
        if not detector.is_trained:
            return 0, [{"Metric": "Error", "Value": "Model not trained. Run: python train_ml_detector.py"}]
        
        # Make prediction
        prediction, confidence = detector.predict(img_array, return_confidence=True)
        
        # Adjust score based on sensitivity
        base_score = confidence if prediction == 1 else (100 - confidence)
        sensitivity_factor = sensitivity / 5.0
        final_score = base_score * sensitivity_factor
        final_score = np.clip(final_score, 0, 100)
        
        # Generate analysis data
        analysis_data = [
            {
                "Metric": "ML Prediction",
                "Value": "STEGO DETECTED" if prediction == 1 else "COVER IMAGE"
            },
            {
                "Metric": "Confidence",
                "Value": f"{confidence:.1f}%"
            },
            {
                "Metric": "Detection Score",
                "Value": f"{final_score:.1f}/100"
            },
            {
                "Metric": "Sensitivity",
                "Value": f"{sensitivity}/10"
            }
        ]
        
        # Add feature analysis
        features = detector.extract_features(img_array)
        feature_names = [
            "LSB Entropy",
            "LSB Ratio",
            "LSB Autocorr",
            "ASCII Ratio",
            "Chi-Square",
            "DCT Mean",
            "DCT Variance",
            "High-Freq Energy",
            "Histogram Var"
        ]
        
        features_scaled = detector.scaler.transform(features)[0]
        
        for name, value in zip(feature_names, features_scaled):
            analysis_data.append({
                "Metric": f"Feature: {name}",
                "Value": f"{value:.4f}"
            })
        
        return final_score, analysis_data
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return 0, [{"Metric": "Error", "Value": str(e)}]


class StegoDetectorML:
    """Machine Learning-based steganography detector using Logistic Regression."""
    
    def __init__(self):
        """Initialize the detector."""
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, img_array):
        """
        Extract features from image for ML model.
        
        Features extracted:
        1. LSB plane entropy
        2. LSB 0/1 ratio
        3. LSB autocorrelation
        4. ASCII ratio in LSB extraction
        5. Chi-square statistic
        6. DCT coefficient distribution
        7. High-frequency component energy
        8. Histogram variance
        
        Args:
            img_array: numpy array of the image (RGB)
        
        Returns:
            numpy array: Feature vector (1D)
        """
        features = []
        
        try:
            # Ensure RGB
            if len(img_array.shape) == 2:
                img_array = np.stack([img_array]*3, axis=-1)
            elif img_array.shape[2] == 4:
                img_array = img_array[:, :, :3]
            
            # Feature 1: LSB Entropy
            lsb_plane = (img_array & 1).flatten()
            unique, counts = np.unique(lsb_plane, return_counts=True)
            probs = counts / len(lsb_plane)
            lsb_entropy = -np.sum(probs * np.log2(probs + 1e-10))
            features.append(lsb_entropy)
            
            # Feature 2: LSB 0/1 Ratio
            ones_count = np.sum(lsb_plane)
            lsb_ratio = ones_count / len(lsb_plane)
            features.append(abs(lsb_ratio - 0.5))
            
            # Feature 3: LSB Autocorrelation
            if len(lsb_plane) > 1000:
                autocorr = np.corrcoef(lsb_plane[:-1], lsb_plane[1:])[0, 1]
                features.append(abs(autocorr))
            else:
                features.append(0)
            
            # Feature 4: ASCII Characters in LSB Extraction
            binary_data = ''
            flat_array = img_array.reshape(-1, 3)
            for pixel in flat_array[:5000]:
                for channel in range(3):
                    binary_data += str(pixel[channel] & 1)
            
            ascii_count = 0
            total_bytes = 0
            for i in range(0, min(len(binary_data) - 8, 40000), 8):
                byte_val = int(binary_data[i:i+8], 2)
                total_bytes += 1
                if 32 <= byte_val <= 126 or byte_val in [10, 13, 9]:
                    ascii_count += 1
            
            ascii_ratio = ascii_count / total_bytes if total_bytes > 0 else 0
            features.append(ascii_ratio)
            
            # Feature 5: Chi-Square Statistic
            hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
            chi_sum = 0
            for i in range(0, 256, 2):
                expected = (hist[i] + hist[i+1]) / 2 + 0.1
                chi_sum += ((hist[i] - expected) ** 2 + (hist[i+1] - expected) ** 2) / expected
            chi_normalized = chi_sum / 128
            features.append(chi_normalized)
            
            # Feature 6 & 7: DCT Coefficient Distribution
            try:
                if img_array.shape[0] >= 8 and img_array.shape[1] >= 8:
                    sample_block = img_array[:8, :8, 0].astype(np.float32)
                    dct_block = dct(dct(sample_block.T, norm='ortho').T, norm='ortho')
                    dct_mean = np.mean(np.abs(dct_block))
                    dct_var = np.var(np.abs(dct_block))
                    features.append(dct_mean)
                    features.append(dct_var)
                else:
                    features.append(0)
                    features.append(0)
            except:
                features.append(0)
                features.append(0)
            
            # Feature 8: High-Frequency Component Energy
            try:
                y_channel = np.mean(img_array, axis=2).astype(np.float32)
                if y_channel.shape[0] >= 8 and y_channel.shape[1] >= 8:
                    dct_y = dct(dct(y_channel[:16, :16].T, norm='ortho').T, norm='ortho')
                    low_freq_energy = np.sum(dct_y[:4, :4] ** 2)
                    high_freq_energy = np.sum(dct_y[4:, 4:] ** 2)
                    freq_ratio = high_freq_energy / (low_freq_energy + 1e-10)
                    features.append(freq_ratio)
                else:
                    features.append(0)
            except:
                features.append(0)
            
            # Feature 9: Histogram Variance
            hist_var = np.var(hist)
            features.append(hist_var)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            return np.zeros((1, 9))
    
    def train(self, cover_images, stego_images, validation_split=0.2):
        """
        Train the Logistic Regression model.
        
        Args:
            cover_images: List of cover image arrays
            stego_images: List of stego image arrays
            validation_split: Fraction of data for validation
        
        Returns:
            dict: Training metrics
        """
        try:
            logger.info("Extracting features from training data...")
            
            cover_features = []
            stego_features = []
            
            # Extract features from cover images
            for i, img in enumerate(cover_images):
                features = self.extract_features(img)
                cover_features.append(features)
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed cover images: {i + 1}")
            
            # Extract features from stego images
            for i, img in enumerate(stego_images):
                features = self.extract_features(img)
                stego_features.append(features)
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed stego images: {i + 1}")
            
            # Combine features and labels
            X = np.vstack(cover_features + stego_features)
            y = np.hstack([
                np.zeros(len(cover_features)),
                np.ones(len(stego_features))
            ])
            
            # Shuffle data
            indices = np.random.permutation(len(X))
            X = X[indices]
            y = y[indices]
            
            # Split into train/validation
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Fit scaler
            logger.info("Training scaler...")
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            
            # Train Logistic Regression
            logger.info("Training Logistic Regression model...")
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                solver='lbfgs',
                class_weight='balanced',
                C=1.0
            )
            self.model.fit(X_train_scaled, y_train)
            self.is_trained = True
            
            # Calculate metrics
            from sklearn.metrics import precision_score, recall_score, f1_score
            
            train_accuracy = self.model.score(X_train_scaled, y_train)
            val_accuracy = self.model.score(X_val_scaled, y_val)
            val_precision = precision_score(y_val, self.model.predict(X_val_scaled))
            val_recall = recall_score(y_val, self.model.predict(X_val_scaled))
            val_f1 = f1_score(y_val, self.model.predict(X_val_scaled))
            
            metrics = {
                'train_accuracy': train_accuracy,
                'val_accuracy': val_accuracy,
                'val_precision': val_precision,
                'val_recall': val_recall,
                'val_f1': val_f1
            }
            
            logger.info(f"Training complete. Validation accuracy: {val_accuracy:.2%}")
            return metrics
            
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            return {"error": str(e)}
    
    def predict(self, img_array, return_confidence=False):
        """
        Predict if image contains steganography.
        
        Args:
            img_array: Image array (RGB)
            return_confidence: If True, return confidence scores
        
        Returns:
            tuple or float: (prediction, confidence) or prediction
        """
        try:
            if self.model is None:
                logger.error("Model not trained. Load or train the model first.")
                return None
            
            features = self.extract_features(img_array)
            features_scaled = self.scaler.transform(features)
            
            prediction = self.model.predict(features_scaled)[0]
            confidence = self.model.predict_proba(features_scaled)[0]
            stego_confidence = confidence[1] * 100
            
            if return_confidence:
                return int(prediction), stego_confidence
            else:
                return int(prediction)
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return None
    
    def save_model(self, path=None):
        """Save the trained model and scaler to disk."""
        try:
            path = path or MODEL_PATH
            
            if self.model is None:
                logger.error("No trained model to save")
                return False
            
            model_dir = Path(path).parent
            model_dir.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
            
            scaler_path = model_dir / (Path(path).stem + '_scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            logger.info(f"Model saved to {path}")
            logger.info(f"Scaler saved to {scaler_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, path=None):
        """Load trained model and scaler from disk."""
        try:
            path = path or MODEL_PATH
            
            if not Path(path).exists():
                logger.warning(f"Model file not found: {path}")
                return False
            
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            
            scaler_path = Path(path).parent / (Path(path).stem + '_scaler.pkl')
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            self.is_trained = True
            logger.info(f"Model loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def get_feature_importance(self):
        """Get feature importance from the model."""
        if self.model is None:
            return {}
        
        feature_names = [
            "LSB Entropy",
            "LSB 0/1 Ratio",
            "LSB Autocorrelation",
            "ASCII Ratio",
            "Chi-Square Stat",
            "DCT Mean",
            "DCT Variance",
            "High-Freq Energy",
            "Histogram Variance"
        ]
        
        importance = np.abs(self.model.coef_[0])
        importance = importance / importance.sum()
        
        return dict(zip(feature_names, importance))