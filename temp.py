from call_analysis import analyze_transcript_with_config
import asyncio

config = {
    "flag1": "flag1",
    "flag2": "flag2",
    "flag3": "flag3",
}

asyncio.run(analyze_transcript_with_config("Hello, how are you?", config))