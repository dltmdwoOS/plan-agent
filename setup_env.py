applicable_locale = ['us']
fields = [
    ("LOCALE", f"LOCALE (Acceptable: {applicable_locale})", True),
    ("OPENAI_API_KEY", "OpenAI API Key", True),
    ("GROQ_API_KEY", "Groq API Key", False),
    ("TAVILY_API_KEY", "Tavily API Key", False),
    ("GOOGLE_MAPS_API_KEY", "Google Maps API Key", False),
]

lines = []
for key, desc, required in fields:
    val = input(f"{desc} ({key}){' [Essential]' if required else ' [Press Enter to omit]'}: ").strip()
    if key=='LOCALE' and val not in applicable_locale:
        print(f"Wrong locale. It must in acceptable locale list: {applicable_locale}")
        exit(1)
    if required and not val:
        print("Required input, please try again.")
        exit(1)
    lines.append(f"{key}={val}")

with open(".env", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(".env file has been created.")