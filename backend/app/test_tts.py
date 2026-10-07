import asyncio

from services.tts_service import text_to_speech


async def main():

    result = await text_to_speech(
        "మీ వరి పంటకు సరైన ఎరువును ఉపయోగించండి.",
        "te",
        "telugu_test.mp3"
    )

    print(result)


asyncio.run(main())