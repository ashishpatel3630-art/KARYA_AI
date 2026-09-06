from models.loader import ModelLoader


loader = ModelLoader()

print("Checking llama3.2 availability...\n")

available = loader.is_available("llama3.2:latest")

if available:
    print("✅ llama3.2:latest is available.")
else:
    print("❌ llama3.2:latest is NOT available.")
