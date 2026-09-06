from models.manager import ModelManager
from models.metadata import ModelMetadata


manager = ModelManager()

model = ModelMetadata(
    name="llama3.2:latest",
    provider="ollama",
    model_type="text",
    description="Local general-purpose language model.",
    context_window=8192,
    supports_tools=False,
    supports_vision=False,
    supports_streaming=True,
)

print("Registering model...\n")

manager.register_model(model)

print("MODEL:")
print(manager.get_model("llama3.2:latest"))

print("\nREGISTERED MODELS:")
for item in manager.list_models():
    print("-", item.name)

print("\nCHECKING LOCAL AVAILABILITY...")

if manager.is_available("llama3.2:latest"):
    print("✅ Model is registered AND available locally.")
else:
    print("❌ Model is not available locally.")