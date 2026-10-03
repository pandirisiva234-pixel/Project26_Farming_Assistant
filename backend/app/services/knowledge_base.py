KNOWLEDGE_BASE = {

    "Crop Advice": {
        "rice": (
            "Rice grows well in warm and humid conditions. "
            "Use healthy seeds, maintain proper water management, "
            "and apply nutrients according to soil requirements."
        ),
        "tomato": (
            "Tomato requires well-drained soil, adequate sunlight, "
            "regular irrigation, and balanced nutrients."
        ),
        "default": (
            "Select crops according to soil type, climate, water availability, "
            "season, and local farming conditions."
        )
    },

    "Fertilizer": {
        "rice": (
            "For rice, fertilizer requirements depend on soil condition "
            "and crop stage. Nitrogen, phosphorus, and potassium should be "
            "applied according to soil-test recommendations."
        ),
        "tomato": (
            "Tomato requires balanced nutrients. Avoid excessive nitrogen "
            "and follow soil-test recommendations for fertilizer application."
        ),
        "default": (
            "Choose fertilizer based on the crop, soil condition, "
            "crop growth stage, and soil-test recommendations."
        )
    },

    "Pest/Disease": {
        "tomato": (
            "Yellow leaves in tomato can have several causes, including "
            "nutrient deficiency, watering problems, pests, or disease. "
            "Inspect the leaves and stems carefully before selecting treatment."
        ),
        "rice": (
            "Rice can be affected by different pests and diseases. "
            "Check the affected plant parts and symptoms before selecting "
            "a control method."
        ),
        "default": (
            "Identify the pest or disease from its symptoms before applying "
            "any treatment. A clear crop or leaf image can help with diagnosis."
        )
    },

    "Irrigation": {
        "rice": (
            "Rice requires careful water management. Irrigation should "
            "depend on crop stage, soil condition, rainfall, and local conditions."
        ),
        "tomato": (
            "Tomato needs consistent soil moisture, but excessive watering "
            "should be avoided. Use well-drained soil and adjust irrigation "
            "according to weather and soil conditions."
        ),
        "default": (
            "Irrigation requirements depend on crop type, soil moisture, "
            "weather, crop stage, and rainfall."
        )
    },

    "Market Price": {
        "default": (
            "Market prices change by crop, location, market, quality, "
            "and date. Check the current local market or mandi price "
            "before making a selling decision."
        )
    },

    "Government Scheme": {
        "default": (
            "Agricultural schemes and subsidies depend on farmer eligibility, "
            "location, crop, and current government programs. "
            "Check the relevant official government portal for current details."
        )
    },

    "General Farming": {
        "default": (
            "For better farming decisions, consider soil condition, "
            "crop type, season, water availability, weather, pests, "
            "and local agricultural recommendations."
        )
    }
}


def get_knowledge_response(intent: str, query: str):

    query_lower = query.lower()

    knowledge = KNOWLEDGE_BASE.get(intent)

    if not knowledge:
        return (
            "I could not find information for this farming question."
        )

    for keyword, response in knowledge.items():

        if keyword != "default" and keyword in query_lower:
            return response

    return knowledge.get(
        "default",
        "Please provide more details about your farming question."
    )