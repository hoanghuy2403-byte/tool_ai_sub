# processing/analyzer.py
import json
import os
import importlib.util
from collections import defaultdict
from typing import List, Dict, Any, Set, Optional
import re

# Dictionary to cache NLP models
_nlp_models = {}

def get_nlp(language='en'):
    """
    Load NLP model on demand based on language
    
    Args:
        language: Language code ('en' for English, 'vi' for Vietnamese, etc.)
        
    Returns:
        Loaded NLP model or None if unavailable
    """
    global _nlp_models
    
    # Return cached model if already loaded
    if language in _nlp_models:
        return _nlp_models[language]
    
    # Try to load spaCy
    try:
        import spacy
        
        model_name = None
        if language == 'en':
            # Try to load English models in order of decreasing size
            for model in ['en_core_web_md', 'en_core_web_sm']:
                try:
                    nlp = spacy.load(model)
                    _nlp_models[language] = nlp
                    return nlp
                except OSError:
                    continue
                    
        elif language == 'vi':
            # Try to load Vietnamese models
            try:
                nlp = spacy.load('vi_core_news_md')
                _nlp_models[language] = nlp
                return nlp
            except OSError:
                pass
                
        # If specific language model is not available, load blank model
        nlp = spacy.blank(language)
        _nlp_models[language] = nlp
        return nlp
        
    except ImportError:
        # If spaCy is not installed, use fallback with regex-based analysis
        print("spaCy not available, using fallback analyzer")
        _nlp_models[language] = None
        return None

def load_categories(categories_file=None):
    """
    Load category configuration from JSON file
    
    Args:
        categories_file: Path to categories JSON file (optional)
        
    Returns:
        Dictionary of category configuration
    """
    if categories_file is None:
        # Default path in data directory
        categories_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'categories.json')
    
    # Check if file exists
    if not os.path.exists(categories_file):
        print(f"Categories file not found: {categories_file}")
        # Create default configuration
        default_config = create_default_categories()
        
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(categories_file), exist_ok=True)
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"Created default categories file: {categories_file}")
            return default_config
        except Exception as e:
            print(f"Error creating default categories file: {e}")
            return default_config
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                raise ValueError("Empty categories file")
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error parsing categories JSON: {e}")
        # Return default config if JSON is invalid
        default_config = create_default_categories()
        
        try:
            # Try to overwrite invalid JSON with default
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"Replaced invalid JSON with default configuration")
        except Exception as write_err:
            print(f"Error writing default configuration: {write_err}")
        
        return default_config
    except Exception as e:
        print(f"Error loading categories: {e}")
        # Return default config if file cannot be loaded
        return create_default_categories()

def create_default_categories():
    """
    Create default category configuration
    
    Returns:
        Dictionary with default categories
    """
    return {
        "categories": {
            "person": {
                "keywords": [
                    "person", "people", "friend", "family", "mom", "dad", "parent", "parents",
                    "his", "her", "them", "they", "brother", "sister", "uncle", "aunt",
                    "boy", "girl", "man", "woman", "child", "baby", "guy", "lady",
                    "mother", "father", "son", "daughter", "grandma", "grandpa", "husband", "wife"
                ],
                "color": "#FF5733",
                "font_weight": "bold",
                "icon": "👥",
                "hover_effect": "scale",
                "context_icons": {
                    "person": "🧑", "people": "👥", "friend": "🤝",
                    "family": "👨‍👩‍👧‍👦", "mom": "👩", "mother": "👩",
                    "dad": "👨", "father": "👨", "parent": "👪", "parents": "👪"
                }
            },
            "emotion": {
                "keywords": [
                    "happy", "sad", "angry", "excited", "love", "hate", "fear", "joy",
                    "laugh", "cry", "smile", "worry", "nervous", "proud", "scared",
                    "surprised", "confused", "tired", "bored", "interested"
                ],
                "color": "#FF33A8",
                "font_weight": "normal",
                "icon": "😊",
                "hover_effect": "pulse",
                "context_icons": {
                    "happy": "😊", "sad": "😢", "angry": "😠",
                    "excited": "🤩", "love": "❤️", "hate": "😡",
                    "fear": "😨", "joy": "😃", "laugh": "😂",
                    "cry": "😭", "smile": "😊", "worry": "😟"
                }
            },
            "action": {
                "keywords": [
                    "run", "walk", "jump", "dance", "sing", "eat", "drink", "sleep",
                    "work", "play", "write", "read", "speak", "listen", "watch",
                    "cook", "build", "draw", "swim", "drive", "fly", "teach"
                ],
                "color": "#33FF57",
                "font_weight": "bold",
                "icon": "🏃",
                "hover_effect": "shake",
                "context_icons": {
                    "run": "🏃", "walk": "🚶", "jump": "⬆️",
                    "dance": "💃", "sing": "🎤", "eat": "🍽️",
                    "drink": "🥤", "sleep": "😴", "work": "💼"
                }
            },
            "time": {
                "keywords": [
                    "today", "tomorrow", "yesterday", "now", "later", "soon",
                    "never", "always", "morning", "afternoon", "evening", "night",
                    "year", "month", "week", "day", "hour", "minute", "second"
                ],
                "color": "#3357FF",
                "font_weight": "normal",
                "icon": "⏰",
                "hover_effect": "rotate",
                "context_icons": {
                    "today": "📅", "tomorrow": "📆", "yesterday": "📅",
                    "now": "⌛", "later": "⏳", "soon": "🔜",
                    "never": "❌", "always": "♾️"
                }
            },
            "place": {
                "keywords": [
                    "home", "school", "office", "park", "city", "country",
                    "street", "road", "building", "house", "apartment",
                    "restaurant", "store", "shop", "market", "mall"
                ],
                "color": "#FFDA33",
                "font_weight": "normal",
                "icon": "📍",
                "hover_effect": "bounce",
                "context_icons": {
                    "home": "🏠", "school": "🏫", "office": "🏢",
                    "park": "🏞️", "city": "🌆", "country": "🗺️",
                    "street": "🛣️", "road": "🛣️", "building": "🏛️"
                }
            },
            "object": {
                "keywords": [
                    "phone", "computer", "laptop", "tablet", "book", "pen",
                    "pencil", "paper", "notebook", "desk", "chair", "table",
                    "bed", "door", "window", "car", "bike", "bus", "train"
                ],
                "color": "#A833FF",
                "font_weight": "normal",
                "icon": "📱",
                "hover_effect": "fade",
                "context_icons": {
                    "phone": "📱", "computer": "💻", "laptop": "💻",
                    "tablet": "📱", "book": "📚", "pen": "🖊️",
                    "pencil": "✏️", "paper": "📄", "notebook": "📓"
                }
            }
        },
        "default_style": {
            "color": "#000000",
            "font_weight": "normal",
            "icon": "",
            "hover_effect": "none"
        },
        "important_style": {
            "color": "#FF9900",
            "font_weight": "bold",
            "icon": "⭐",
            "hover_effect": "glow"
        },
        "emphasis_styles": {
            "strong": {
                "color": "#FF0000",
                "font_weight": "bold",
                "text_decoration": "underline",
                "hover_effect": "scale"
            },
            "highlight": {
                "background_color": "#FFFF00",
                "color": "#000000",
                "hover_effect": "glow"
            },
            "special": {
                "color": "#9C27B0",
                "font_style": "italic",
                "text_shadow": "2px 2px 4px rgba(0,0,0,0.2)",
                "hover_effect": "rotate"
            }
        },
        "animations": {
            "scale": "transform: scale(1.1)",
            "pulse": "animation: pulse 1s infinite",
            "shake": "animation: shake 0.5s",
            "rotate": "transform: rotate(5deg)",
            "bounce": "animation: bounce 0.5s",
            "fade": "opacity: 0.8",
            "glow": "box-shadow: 0 0 10px rgba(255,255,0,0.5)",
            "highlight": "background-color: rgba(255,255,0,0.3)",
            "wave": "animation: wave 1s infinite",
            "sparkle": "animation: sparkle 1s infinite"
        }
    }

def analyze_words(words_data: List[Dict[str, Any]], language='en', min_importance=0.5, use_emojis=True) -> List[Dict[str, Any]]:
    """
    Analyze words to identify importance and semantic categories with context awareness
    
    Args:
        words_data: List of word dictionaries from parser
        language: Language code ('en' for English, 'vi' for Vietnamese)
        min_importance: Threshold for word importance (0.0 to 1.0)
        use_emojis: Whether to include emoji icons in the output
        
    Returns:
        Enhanced word list with importance, categories and context-aware icons
    """
    if not words_data:
        return []
    
    # Initialize fields for all words
    for word in words_data:
        word['important'] = False
        word['categories'] = []
        word['context_icons'] = []
        word['primary_icon'] = ""
        word['secondary_icons'] = []
        word['context_info'] = {}  # Add context information
        word['importance_score'] = 0.0
    
    try:
        # Load NLP model and configuration
        nlp = get_nlp(language)
        config = load_categories()
        categories = config.get("categories", {})
        
        # Create full text for analysis
        full_text = " ".join([w.get('word', '') for w in words_data])
        
        # Analysis results
        syntax_info = {}
        context_windows = {}
        important_words = {}
        
        # Use NLP model if available
        if nlp:
            doc = nlp(full_text)
            
            # Build context windows and analyze syntax
            for i, token in enumerate(doc):
                # Get 5 words before and after for better context
                start = max(0, i - 5)
                end = min(len(doc), i + 6)
                context_tokens = doc[start:end]
                
                word_lower = token.text.lower()
                context_windows[word_lower] = {
                    'text': [t.text.lower() for t in context_tokens],
                    'pos': [t.pos_ for t in context_tokens],
                    'dep': [t.dep_ for t in context_tokens],
                    'ent': [t.ent_type_ for t in context_tokens]
                }
                
                # Save syntax information
                syntax_info[word_lower] = {
                    'pos': token.pos_,
                    'dep': token.dep_,
                    'ent': token.ent_type_,
                    'is_stop': token.is_stop
                }
                
                # Calculate importance score based on POS and NER
                importance_score = 0.0
                
                if token.pos_ in ['PROPN', 'NOUN']:
                    importance_score += 0.4
                elif token.pos_ in ['VERB']:
                    importance_score += 0.3
                elif token.pos_ in ['ADJ', 'ADV']:
                    importance_score += 0.2
                
                # Score for non-stop words
                if not token.is_stop:
                    importance_score += 0.3
                
                # Score for named entities
                if token.ent_type_:
                    importance_score += 0.4
                
                # Score for important syntactic positions
                if token.dep_ in ['ROOT', 'nsubj', 'dobj']:
                    importance_score += 0.2
                    
                important_words[word_lower] = max(important_words.get(word_lower, 0), importance_score)
                
        else:
            # Fallback analysis without NLP
            # 1. Build a simple frequency count
            word_freq = defaultdict(int)
            unique_words = set()
            
            for word in words_data:
                word_text = word.get('word', '').lower()
                word_freq[word_text] += 1
                unique_words.add(word_text)
            
            # 2. Calculate a simple importance score based on:
            #    - Word length (longer words often more important)
            #    - Word frequency relative to total (less frequent might be more important)
            #    - Standard stopwords (less important)
            
            # Simple English stopwords list
            stopwords = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by',
                       'of', 'in', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'it', 'its',
                       'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'they', 'we'}
            
            # Simple context windows
            for word in words_data:
                word_text = word.get('word', '').lower()
                word_idx = words_data.index(word)
                
                # Get 5 words before and after for context
                start = max(0, word_idx - 5)
                end = min(len(words_data), word_idx + 6)
                context = [w.get('word', '').lower() for w in words_data[start:end]]
                
                context_windows[word_text] = {
                    'text': context,
                    'pos': [],  # No POS without NLP
                    'dep': [],
                    'ent': []
                }
                
                # Calculate importance
                importance = 0.0
                
                # Length factor (normalized by max word length)
                max_word_len = 20  # Reasonable max length
                length_factor = min(len(word_text) / max_word_len, 1.0) * 0.3
                
                # Frequency factor (less frequent may be more important)
                total_words = len(words_data)
                freq = word_freq[word_text]
                freq_factor = (1 - (freq / total_words)) * 0.3
                
                # Stopword penalty
                stopword_penalty = 0.4 if word_text in stopwords else 0
                
                # Is the word capitalized in original form?
                original_word = word.get('word', '')
                if original_word and original_word[0].isupper() and not word_idx == 0:
                    # Probably a proper noun
                    proper_noun_bonus = 0.3
                else:
                    proper_noun_bonus = 0
                
                # Simple syntax based on punctuation
                syntax_info[word_text] = {
                    'pos': 'PROPN' if proper_noun_bonus > 0 else 'UNKNOWN',
                    'dep': 'ROOT' if word_idx == 0 else 'UNKNOWN',
                    'ent': 'UNKNOWN',
                    'is_stop': word_text in stopwords
                }
                
                # Combined importance score
                importance = length_factor + freq_factor + proper_noun_bonus - stopword_penalty
                importance = max(0, min(importance, 1.0))  # Clip to [0, 1]
                
                important_words[word_text] = importance
        
        # Analyze context and categories for each word
        for word in words_data:
            word_lower = word.get('word', '').lower()
            context = context_windows.get(word_lower, {})
            syntax = syntax_info.get(word_lower, {})
            
            # Calculate importance using either NLP or fallback scores
            importance_score = important_words.get(word_lower, 0.0)
            word['importance_score'] = importance_score
            word['important'] = importance_score >= min_importance
            
            # Collect all potential categories and icons
            potential_categories = []
            potential_icons = []
            
            for category_name, category_info in categories.items():
                keywords = category_info.get("keywords", [])
                context_icons = category_info.get("context_icons", {})
                
                # Check if word is in keywords
                if word_lower in keywords:
                    potential_categories.append(category_name)
                    
                    # Collect icons based on exact context
                    if word_lower in context_icons:
                        potential_icons.append({
                            'icon': context_icons[word_lower],
                            'category': category_name,
                            'priority': 1.0,  # Direct icon
                            'context': 'direct_match'
                        })
                    else:
                        potential_icons.append({
                            'icon': category_info.get("icon", ""),
                            'category': category_name,
                            'priority': 0.7,  # Category icon
                            'context': 'category_default'
                        })
                
                # Analyze surrounding context
                context_text = context.get('text', [])
                
                # Look for related words in context
                for ctx_word in context_text:
                    if ctx_word in keywords and ctx_word != word_lower:
                        # Calculate priority based on relationship
                        priority = 0.5  # Default for context
                            
                        if ctx_word in context_icons:
                            potential_icons.append({
                                'icon': context_icons[ctx_word],
                                'category': category_name,
                                'priority': priority,
                                'context': f'related_context'
                            })
            
            # Sort and filter icons
            sorted_icons = sorted(potential_icons, 
                              key=lambda x: (-x['priority'], x['category'], -len(x['context'])))
            
            # Remove duplicate icons but keep context
            unique_icons = []
            seen_icons = set()
            icon_contexts = {}
            
            for icon_info in sorted_icons:
                icon = icon_info['icon']
                if icon not in seen_icons:
                    unique_icons.append(icon)
                    seen_icons.add(icon)
                    icon_contexts[icon] = icon_info['context']
            
            # Assign results to word
            word['categories'] = list(set(potential_categories))
            
            if use_emojis and unique_icons:
                word['primary_icon'] = unique_icons[0]
                word['secondary_icons'] = unique_icons[1:3]  # Limit to 2 secondary icons
                word['context_icons'] = unique_icons
                word['context_info'] = {
                    'syntax': syntax,
                    'icon_contexts': icon_contexts,
                    'categories': potential_categories
                }
            
    except Exception as e:
        print(f"Error in word analysis: {e}")
        import traceback
        traceback.print_exc()
        
    return words_data

def apply_styling(analyzed_words: List[Dict[str, Any]], use_emojis=True, **style_params) -> List[Dict[str, Any]]:
    """
    Apply styling and icons to words based on importance and categories
    
    Args:
        analyzed_words: List of analyzed word dictionaries
        use_emojis: Whether to include emoji icons
        style_params: Additional styling parameters (e.g. custom colors)
        
    Returns:
        Words with styling information
    """
    if not analyzed_words:
        return []
        
    # Load configuration
    config = load_categories()
    categories = config.get("categories", {})
    default_style = config.get("default_style", {"color": "#000000", "font_weight": "normal", "icon": ""})
    important_style = config.get("important_style", {"color": "#FF9900", "font_weight": "bold", "icon": "⭐"})
    
    # Apply custom colors if provided
    if 'primary_color' in style_params:
        important_style['color'] = style_params['primary_color']
    if 'secondary_color' in style_params:
        for category in categories.values():
            category['color'] = style_params['secondary_color']
    
    # Apply style to each word
    for word in analyzed_words:
        # Ensure required fields exist
        if 'important' not in word:
            word['important'] = False
            
        if 'categories' not in word:
            word['categories'] = []
            
        try:
            # Apply style based on importance and categories
            if word['important'] and word['categories']:
                # Use first category for style
                category = word['categories'][0]
                if category in categories:
                    style = dict(categories[category])
                    if not use_emojis:
                        style['icon'] = ''
                    word['style'] = style
                else:
                    word['style'] = dict(important_style)
                    if not use_emojis:
                        word['style']['icon'] = ''
            elif word['important']:
                # Important but no category
                word['style'] = dict(important_style)
                if not use_emojis:
                    word['style']['icon'] = ''
            else:
                # Default style
                word['style'] = dict(default_style)
                if not use_emojis:
                    word['style']['icon'] = ''
                    
            # Ensure hover effect is set
            if 'hover_effect' not in word['style']:
                word['style']['hover_effect'] = 'none'
                
        except Exception as e:
            print(f"Error applying style to word: {e}")
            # Use default style if error occurs
            word['style'] = dict(default_style)
            if not use_emojis:
                word['style']['icon'] = ''
            
    return analyzed_words