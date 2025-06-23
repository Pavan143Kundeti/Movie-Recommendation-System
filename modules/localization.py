import streamlit as st

# Default to English if no language is set
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Dictionary for translations
TRANSLATIONS = {
    "English": {
        "page_title": "Movie Recommendation System",
        "welcome_message": "Welcome, {username}! Explore our collection of movies and series.",
        "recommended_for_you": "✨ Recommended for You",
        "because_you_watched": "Because you watched **{movie_title}**:",
        "search_and_filter": "🔍 Search & Filter",
        "search_placeholder": "Search movie title, cast, or description...",
        "genre_filter_label": "Filter by genre",
        "audio_language_filter_label": "Filter by Audio Language",
        "browse_all": "📺 Browse All Movies & Series ({count} found)",
        "watchlist_add": "➕ Watchlist",
        "watchlist_remove": "➖ Watchlist",
        "watched": "✔️ Watched",
        "details_reviews": "Details & Reviews",
        "no_reviews": "No reviews yet",
        "logout": "🚪 Logout",
        "logged_in_as": "👤 Logged in as {username}",
        "all_genres": "All",
    },
    "Hindi": {
        "page_title": "मूवी अनुशंसा प्रणाली",
        "welcome_message": "नमस्ते, {username}! हमारे फिल्मों और श्रृंखलाओं के संग्रह का अन्वेषण करें।",
        "recommended_for_you": "✨ आपके लिए अनुशंसित",
        "because_you_watched": "क्योंकि आपने **{movie_title}** देखी:",
        "search_and_filter": "🔍 खोजें और फ़िल्टर करें",
        "search_placeholder": "फिल्म का शीर्षक, कलाकार, या विवरण खोजें...",
        "genre_filter_label": "शैली के अनुसार फ़िल्ter करें",
        "audio_language_filter_label": "ऑडियो भाषा के अनुसार फ़िल्टर करें",
        "browse_all": "📺 सभी फिल्में और श्रृंखलाएं ब्राउज़ करें ({count} मिलीं)",
        "watchlist_add": "➕ वॉचलिस्ट",
        "watchlist_remove": "➖ वॉचलिस्ट",
        "watched": "✔️ देखा गया",
        "details_reviews": "विवरण और समीक्षाएं",
        "no_reviews": "अभी तक कोई समीक्षा नहीं",
        "logout": "🚪 लॉग आउट",
        "logged_in_as": "👤 {username} के रूप में लॉग इन",
        "all_genres": "सभी",
    },
    "Telugu": {
        "page_title": "సినిమా సిఫార్సు వ్యవస్థ",
        "welcome_message": "స్వాగతం, {username}! మా సినిమాలు మరియు సిరీస్‌ల సేకరణను అన్వేషించండి.",
        "recommended_for_you": "✨ మీ కోసం సిఫార్సు చేయబడినవి",
        "because_you_watched": "మీరు **{movie_title}** చూసినందున:",
        "search_and_filter": "🔍 శోధించండి మరియు ఫిల్టర్ చేయండి",
        "search_placeholder": "సినిమా పేరు, నటీనటులు లేదా వివరణను శోధించండి...",
        "genre_filter_label": "శైలి ఆధారంగా ఫిల్టర్ చేయండి",
        "audio_language_filter_label": "ఆడియో భాష ఆధారంగా ఫిల్టర్ చేయండి",
        "browse_all": "📺 అన్ని సినిమాలు & సిరీస్‌లను బ్రౌజ్ చేయండి ({count} కనుగొనబడ్డాయి)",
        "watchlist_add": "➕ వాచ్‌లిస్ట్",
        "watchlist_remove": "➖ వాచ్‌లిస్ట్",
        "watched": "✔️ చూశారు",
        "details_reviews": "వివరాలు & సమీక్షలు",
        "no_reviews": "ఇంకా సమీక్షలు లేవు",
        "logout": "🚪 లాగ్ అవుట్",
        "logged_in_as": "👤 {username}గా లాగిన్ అయ్యారు",
        "all_genres": "అన్నీ",
    },
    "Tamil": {
        "page_title": "திரைப்பட பரிந்துரை அமைப்பு",
        "welcome_message": "வணக்கம், {username}! எங்கள் திரைப்படங்கள் மற்றும் தொடர்களின் தொகுப்பை ஆராயுங்கள்.",
        "recommended_for_you": "✨ உங்களுக்காகப் பரிந்துரைக்கப்பட்டவை",
        "because_you_watched": "**{movie_title}** பார்த்ததால்:",
        "search_and_filter": "🔍 தேடவும் மற்றும் வடிகட்டவும்",
        "search_placeholder": "திரைப்படத் தலைப்பு, நடிகர்கள் அல்லது വിവరణத்தைத் தேடுங்கள்...",
        "genre_filter_label": "வகை மூலம் வடிகட்டவும்",
        "audio_language_filter_label": "ஆடியோ மொழி மூலம் வடிகட்டவும்",
        "browse_all": "📺 அனைத்து திரைப்படங்களையும் தொடர்களையும் உலாவுக ({count} கண்டறியப்பட்டது)",
        "watchlist_add": "➕ கண்காணிப்பு பட்டியல்",
        "watchlist_remove": "➖ கண்காணிப்பு பட்டியல்",
        "watched": "✔️ பார்க்கப்பட்டது",
        "details_reviews": "விவரங்கள் & விமர்சனங்கள்",
        "no_reviews": "இன்னும் விமர்சனங்கள் இல்லை",
        "logout": "🚪 வெளியேறு",
        "logged_in_as": "👤 {username} ஆக உள்நுழைந்துள்ளீர்கள்",
        "all_genres": "அனைத்தும்",
    }
}

def get_text(key):
    """
    Returns the translated text for a given key in the current language.
    Falls back to English if the key is not found in the current language.
    """
    language = st.session_state.get('language', 'English')
    return TRANSLATIONS.get(language, {}).get(key, TRANSLATIONS.get('English', {}).get(key, key)) 