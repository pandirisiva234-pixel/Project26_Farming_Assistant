def classify_intent(text: str):

    text = text.lower().strip()

    # ========================================================
    # WEATHER
    # ========================================================

    weather_keywords = [
        "weather",
        "rain",
        "temperature",
        "forecast",
        "hot",
        "cold",
        "climate",
        "wind"
    ]


    # ========================================================
    # PEST / DISEASE
    # ========================================================

    disease_keywords = [
        "disease",
        "pest",
        "insect",
        "yellow leaves",
        "spots",
        "infection",
        "plant disease",
        "leaf disease"
    ]


    # ========================================================
    # FERTILIZER
    # ========================================================

    fertilizer_keywords = [
        "fertilizer",
        "fertiliser",
        "urea",
        "npk",
        "manure",
        "nutrient",
        "fertilizers",
        "fertilisers"
    ]


    # ========================================================
    # IRRIGATION
    # ========================================================

    irrigation_keywords = [
        "irrigation",
        "watering",
        "water requirement",
        "water requirements",
        "soil moisture",
        "drip irrigation",
        "how much water"
    ]


    # ========================================================
    # MARKET PRICE
    # ========================================================

    market_keywords = [
        "market price",
        "market prices",
        "mandi",
        "selling price",
        "sell price",
        "price of",
        "crop price"
    ]


    # ========================================================
    # GOVERNMENT SCHEME
    # ========================================================

    government_keywords = [
        "government scheme",
        "government schemes",
        "scheme",
        "subsidy",
        "pm kisan",
        "loan",
        "government"
    ]


    # ========================================================
    # CROP ADVICE
    # ========================================================

    crop_keywords = [
        "which crop",
        "what crop",
        "suitable crop",
        "best crop",
        "crop selection",
        "crop cultivation",
        "cultivation",
        "growing crop",
        "grow rice",
        "grow wheat",
        "grow tomato"
    ]


    # ========================================================
    # CHECK INTENTS
    # ========================================================
    #
    # Specific intents are checked before general crop advice.
    # This prevents words such as "crop" from incorrectly
    # classifying fertilizer or disease questions.
    #

    if any(keyword in text for keyword in weather_keywords):
        return "Weather"

    if any(keyword in text for keyword in disease_keywords):
        return "Pest/Disease"

    if any(keyword in text for keyword in fertilizer_keywords):
        return "Fertilizer"

    if any(keyword in text for keyword in irrigation_keywords):
        return "Irrigation"

    if any(keyword in text for keyword in market_keywords):
        return "Market Price"

    if any(keyword in text for keyword in government_keywords):
        return "Government Scheme"

    if any(keyword in text for keyword in crop_keywords):
        return "Crop Advice"

    return "General Farming"