# processing/advanced_analyzer.py
from transformers import pipeline
import torch
from typing import List, Dict, Any
import json
import os

class AdvancedAnalyzer:
    def __init__(self):
        # Khởi tạo các model transformer
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.zero_shot_classifier = pipeline("zero-shot-classification")
        self.feature_extractor = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2")
        
        # Load custom effects và animations
        self.load_effects()
    
    def load_effects(self):
        """Load custom effects và animations từ config"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'effects.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.effects_config = json.load(f)
            else:
                self.effects_config = self.get_default_effects()
                # Tạo file config mặc định
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.effects_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error loading effects config: {e}")
            self.effects_config = self.get_default_effects()

    def get_default_effects(self):
        """Tạo config mặc định cho effects và animations"""
        return {
            "text_effects": {
                "emphasis": {
                    "strong": {
                        "font_weight": "bold",
                        "color": "#FF0000",
                        "text_shadow": "2px 2px 4px rgba(255,0,0,0.2)"
                    },
                    "highlight": {
                        "background": "rgba(255,255,0,0.3)",
                        "border_radius": "3px",
                        "padding": "0 3px"
                    },
                    "special": {
                        "font_style": "italic",
                        "color": "#9C27B0",
                        "letter_spacing": "1px"
                    }
                },
                "emotions": {
                    "positive": {
                        "color": "#4CAF50",
                        "transform": "scale(1.05)",
                        "transition": "all 0.3s ease"
                    },
                    "negative": {
                        "color": "#F44336",
                        "transform": "scale(0.95)",
                        "transition": "all 0.3s ease"
                    },
                    "neutral": {
                        "color": "#2196F3",
                        "transition": "all 0.3s ease"
                    }
                }
            },
            "animations": {
                "hover": {
                    "scale": "transform: scale(1.1)",
                    "glow": "box-shadow: 0 0 10px rgba(255,255,0,0.5)",
                    "shake": "animation: shake 0.5s",
                    "pulse": "animation: pulse 1s infinite",
                    "rotate": "transform: rotate(5deg)",
                    "bounce": "animation: bounce 0.5s",
                    "wave": "animation: wave 1s infinite"
                },
                "keyframes": {
                    "pulse": "@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }",
                    "shake": "@keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }",
                    "bounce": "@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }",
                    "wave": "@keyframes wave { 0% { transform: rotate(0deg); } 25% { transform: rotate(5deg); } 75% { transform: rotate(-5deg); } 100% { transform: rotate(0deg); } }"
                }
            },
            "icon_effects": {
                "size_variations": {
                    "small": "0.8em",
                    "medium": "1em",
                    "large": "1.2em"
                },
                "positions": {
                    "before": "margin-right: 0.3em",
                    "after": "margin-left: 0.3em",
                    "above": "display: block; margin-bottom: 0.2em",
                    "below": "display: block; margin-top: 0.2em"
                }
            }
        }

    def analyze_sentiment_and_context(self, text: str) -> Dict[str, Any]:
        """Phân tích sentiment và context của văn bản"""
        try:
            # Phân tích sentiment
            sentiment = self.sentiment_analyzer(text)[0]
            
            # Phân loại zero-shot với các nhãn tùy chỉnh
            categories = [
                "action", "emotion", "description", "location", 
                "time", "person", "object", "event"
            ]
            classification = self.zero_shot_classifier(text, categories)
            
            # Trích xuất features để phân tích ngữ cảnh
            features = self.feature_extractor(text)
            
            return {
                "sentiment": {
                    "label": sentiment["label"],
                    "score": sentiment["score"]
                },
                "categories": {
                    "labels": classification["labels"],
                    "scores": classification["scores"]
                },
                "features": features
            }
        except Exception as e:
            print(f"Error in sentiment and context analysis: {e}")
            return {}

    def enhance_word_analysis(self, word_data: Dict[str, Any], context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Nâng cao phân tích từ với thông tin sentiment và context"""
        try:
            # Lấy thông tin cơ bản
            word = word_data.get("word", "").lower()
            
            # Áp dụng effects dựa trên sentiment
            sentiment = context_analysis.get("sentiment", {})
            if sentiment:
                if sentiment["label"] == "POSITIVE":
                    word_data["effects"] = self.effects_config["text_effects"]["emotions"]["positive"]
                elif sentiment["label"] == "NEGATIVE":
                    word_data["effects"] = self.effects_config["text_effects"]["emotions"]["negative"]
                else:
                    word_data["effects"] = self.effects_config["text_effects"]["emotions"]["neutral"]
            
            # Áp dụng animations dựa trên category
            categories = context_analysis.get("categories", {})
            if categories:
                top_category = categories["labels"][0]
                category_score = categories["scores"][0]
                
                if category_score > 0.5:
                    if top_category == "action":
                        word_data["animation"] = self.effects_config["animations"]["hover"]["shake"]
                    elif top_category == "emotion":
                        word_data["animation"] = self.effects_config["animations"]["hover"]["pulse"]
                    elif top_category == "event":
                        word_data["animation"] = self.effects_config["animations"]["hover"]["bounce"]
                    else:
                        word_data["animation"] = self.effects_config["animations"]["hover"]["scale"]
            
            # Tùy chỉnh icon effects
            if word_data.get("primary_icon"):
                icon_size = "medium"
                if word_data.get("importance_score", 0) > 0.7:
                    icon_size = "large"
                elif word_data.get("importance_score", 0) < 0.3:
                    icon_size = "small"
                
                word_data["icon_style"] = {
                    "size": self.effects_config["icon_effects"]["size_variations"][icon_size],
                    "position": self.effects_config["icon_effects"]["positions"]["before"]
                }
            
            return word_data
        except Exception as e:
            print(f"Error enhancing word analysis: {e}")
            return word_data

    def process_subtitle(self, subtitle_text: str, words_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Xử lý phụ đề với phân tích nâng cao"""
        try:
            # Phân tích sentiment và context cho toàn bộ phụ đề
            context_analysis = self.analyze_sentiment_and_context(subtitle_text)
            
            # Nâng cao phân tích cho từng từ
            enhanced_words = []
            for word_data in words_data:
                enhanced_word = self.enhance_word_analysis(word_data, context_analysis)
                enhanced_words.append(enhanced_word)
            
            return enhanced_words
        except Exception as e:
            print(f"Error processing subtitle: {e}")
            return words_data

    def generate_css(self) -> str:
        """Tạo CSS cho các effects và animations"""
        css = []
        
        # Thêm keyframes cho animations
        for name, keyframe in self.effects_config["animations"]["keyframes"].items():
            css.append(keyframe)
        
        # Thêm các class cho text effects
        for category, effects in self.effects_config["text_effects"].items():
            for effect_name, style in effects.items():
                css_properties = []
                for prop, value in style.items():
                    css_prop = prop.replace("_", "-")
                    css_properties.append(f"{css_prop}: {value}")
                css.append(f".text-effect-{category}-{effect_name} {{ {'; '.join(css_properties)} }}")
        
        # Thêm hover effects
        for name, effect in self.effects_config["animations"]["hover"].items():
            css.append(f".hover-effect-{name}:hover {{ {effect} }}")
        
        # Thêm icon effects
        for size, value in self.effects_config["icon_effects"]["size_variations"].items():
            css.append(f".icon-size-{size} {{ font-size: {value} }}")
        
        for position, style in self.effects_config["icon_effects"]["positions"].items():
            css.append(f".icon-position-{position} {{ {style} }}")
        
        return "\n".join(css)