from models.metadata import ModelMetadata
from models.registry import ModelRegistry


registry = ModelRegistry()

model = ModelMetadata(
    name="llama3.2",
    provider="ollama",
    model_type="text",
    description="Local general-purpose language model.",
    context_window=8192,
    supports_tools=False,
    supports_vision=False,
    supports_streaming=True,
)

registry.register(model)

print("MODEL REGISTERED:")
print(model.name)

print("\nMODEL EXISTS:")
print(registry.exists("llama3.2"))

print("\nMODEL DETAILS:")
print(registry.get("llama3.2"))

print("\nALL REGISTERED MODELS:")
for item in registry.list_models():
    print("-", item.name)
