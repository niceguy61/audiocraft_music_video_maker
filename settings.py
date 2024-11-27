# 장르별 기본 설정
city_pop_settings = {
    "bpm": 82,
    "duration": 30,
    "temperature": 0.3,
    "top_k": 50,
    "top_p": 0.8,
    "cfg_coef": 5.0,
    "genre": "city_pop"
}

lofi_settings = {
    "bpm": 75,
    "duration": 30,
    "temperature": 0.3,
    "top_k": 50,
    "top_p": 0.8,
    "cfg_coef": 5.0,
    "genre": "lofi"
}

future_bass_settings = {
    "bpm": 150,
    "duration": 30,
    "temperature": 0.4,
    "top_k": 60,
    "top_p": 0.9,
    "cfg_coef": 4.0,
    "genre": "future_bass"
}

house_settings = {
    "bpm": 128,
    "duration": 30,
    "temperature": 0.35,
    "top_k": 55,
    "top_p": 0.85,
    "cfg_coef": 4.5,
    "genre": "house"
}

trap_settings = {
    "bpm": 140,
    "duration": 30,
    "temperature": 0.45,
    "top_k": 65,
    "top_p": 0.9,
    "cfg_coef": 4.0,
    "genre": "trap"
}

ambient_settings = {
    "bpm": 70,
    "duration": 30,
    "temperature": 0.25,
    "top_k": 45,
    "top_p": 0.75,
    "cfg_coef": 5.5,
    "genre": "ambient"
}

dnb_settings = {
    "bpm": 174,
    "duration": 30,
    "temperature": 0.4,
    "top_k": 60,
    "top_p": 0.85,
    "cfg_coef": 4.5,
    "genre": "dnb"
}

trance_settings = {
    "bpm": 138,
    "duration": 30,
    "temperature": 0.35,
    "top_k": 55,
    "top_p": 0.85,
    "cfg_coef": 4.5,
    "genre": "trance"
}

# 장르별 프롬프트 템플릿
genre_prompts = {
    "City Pop": [
        "japanese city pop with clear song structure and consistent rhythm, "
        "warm electric piano rhodes, funky bass guitar, clean electric guitars, "
        "vintage drum machines maintaining steady beat throughout, "
        "essential structure requirements: "
        "intro 8 bars with distinctive atmospheric opening keeping minimal drums for beat recognition, "
        "clear transition into main sections with multiples of 8 bars, "
        "verses and choruses maintaining steady groove and clear progression, "
        "distinct outro 8 bars with recognizable ending phrase keeping minimal drums"
    ],
    
    "Lo-Fi": [
        "lo-fi hip hop with structured arrangement, "
        "warm vinyl crackles, mellow piano, smooth jazz samples, "
        "steady boom bap drums, deep bass, "
        "essential structure requirements: "
        "intro 8 bars with characteristic lo-fi atmosphere and minimal drums, "
        "main sections in 8 bar multiples with relaxed progression, "
        "clear verse and chorus segments, "
        "outro 8 bars with gentle fade maintaining beat"
    ],
    
    "Future Bass": [
        "future bass with modern production and clear arrangement, "
        "heavy sidechained synths, powerful supersaws, crisp drums, "
        "deep sub bass, bright leads, "
        "essential structure requirements: "
        "intro 8 bars with building energy and minimal percussion, "
        "main sections in 8 bar multiples with dynamic progression, "
        "intense drops with clear rhythmic structure, "
        "outro 8 bars with distinctive ending maintaining energy"
    ],
    
    "House": [
        "house music with classic four-on-the-floor rhythm, "
        "punchy kicks, crisp hi-hats, driving percussion, "
        "uplifting chord progressions, groovy basslines, "
        "essential structure requirements: "
        "intro 8 bars with building drums and minimal elements, "
        "main sections in 8 bar multiples with steady progression, "
        "clear breakdown and build-up segments, "
        "outro 8 bars with rhythmic fade maintaining groove"
    ],
    
    "Trap": [
        "trap music with heavy 808s and clear structure, "
        "rolling hi-hats, punchy snares, deep sub bass, "
        "atmospheric pads, dark melodies, "
        "essential structure requirements: "
        "intro 8 bars with minimal drums and atmosphere, "
        "main sections in 8 bar multiples with strong 808 patterns, "
        "clear hook sections with full percussion, "
        "outro 8 bars with distinctive trap ending"
    ],
    
    "Ambient": [
        "ambient music with clear structural progression, "
        "ethereal pads, subtle textures, gentle percussion, "
        "atmospheric soundscapes, minimal beats, "
        "essential structure requirements: "
        "intro 8 bars with subtle rhythm and atmospheric elements, "
        "main sections in 8 bar multiples with gentle evolution, "
        "clear textural development, "
        "outro 8 bars with soft fade maintaining minimal beat"
    ],
    
    "DnB": [
        "drum and bass with precise breakbeat patterns, "
        "heavy reese bass, sharp drums, energetic rhythm, "
        "atmospheric pads, rolling percussion, "
        "essential structure requirements: "
        "intro 8 bars with building breaks and minimal elements, "
        "main sections in 8 bar multiples with full dnb rhythm, "
        "clear drop sections with intense breaks, "
        "outro 8 bars with distinctive dnb ending"
    ],
    
    "Trance": [
        "trance music with euphoric progression, "
        "driving bassline, uplifting leads, energetic arps, "
        "powerful kicks, crisp percussion, "
        "essential structure requirements: "
        "intro 8 bars with building energy and minimal beats, "
        "main sections in 8 bar multiples with clear progression, "
        "emotional breakdown and build-up sections, "
        "outro 8 bars with characteristic trance ending"
    ]
}

# 프롬프트 검증 함수
def validate_prompt(prompt):
    """
    프롬프트가 필수 구조적 요구사항을 포함하는지 확인
    """
    required_elements = [
        "intro 8 bars",
        "outro 8 bars",
        "essential structure requirements"
    ]
    
    return all(element in prompt.lower() for element in required_elements)

# 장르별 기본 프롬프트 가져오기
def get_default_prompt(genre):
    """
    특정 장르의 기본 프롬프트 반환
    """
    if genre in genre_prompts:
        return genre_prompts[genre][0]
    return ""

# 장르별 설정 가져오기
def get_genre_settings(genre):
    """
    장르명으로 해당 장르의 설정 반환
    """
    settings_map = {
        "City Pop": city_pop_settings,
        "Lo-Fi": lofi_settings,
        "Future Bass": future_bass_settings,
        "House": house_settings,
        "Trap": trap_settings,
        "Ambient": ambient_settings,
        "DnB": dnb_settings,
        "Trance": trance_settings
    }
    
    return settings_map.get(genre, city_pop_settings)  # 기본값으로 city_pop 설정 반환