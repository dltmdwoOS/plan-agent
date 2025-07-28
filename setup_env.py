fields = [
    ("OPENAI_API_KEY", "Essential: OpenAI API Key", True),
    ("GROQ_API_KEY", "Optional: Groq API Key", False),
    ("TAVILY_API_KEY", "Optional: Tavily API Key", False),
    ("GOOGLE_MAPS_API_KEY", "Optional: Google Maps API Key", False),
]

lines = []
for key, desc, required in fields:
    val = input(f"{desc} ({key}){' [Essential]' if required else ' [Press Enter to omit]'}: ").strip()
    if required and not val:
        print("Required input, please try again.")
        exit(1)
    lines.append(f"{key}={val}")

with open(".env", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(".env file has been created.")