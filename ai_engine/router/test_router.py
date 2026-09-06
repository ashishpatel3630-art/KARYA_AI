from models.manager import ModelManager
from models.metadata import ModelMetadata
from router.router import ModelRouter


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

manager.register_model(model)

router = ModelRouter(model_manager=manager)


test_prompts = [
    "Explain predictive maintenance.",
    "Calculate the total maintenance cost.",
    "Analyze this engineering drawing.",
]


for prompt in test_prompts:
    result = router.route(prompt)

    print("\n" + "=" * 50)
    print("PROMPT:", prompt)
    print("TASK TYPE:", result.task_type)
    print("MODEL TYPE:", result.model_type)
    print("SELECTED MODEL:", result.selected_model)
    print("VISION REQUIRED:", result.requires_vision)
    print("TOOLS REQUIRED:", result.requires_tools)
    print("REASON:", result.reason)