from dataclasses import dataclass

from .schemas import VisionResponse
from .service import VisionService


@dataclass(frozen=True)
class IndustrialFinding:
    """Structured finding extracted from an industrial image."""

    category: str
    observation: str
    severity: str = "unknown"


@dataclass(frozen=True)
class IndustrialAnalysis:
    """High-level industrial image analysis result."""

    image_path: str
    model: str
    content: str
    findings: list[IndustrialFinding]

    def is_empty(self) -> bool:
        return not self.content.strip()

    def finding_count(self) -> int:
        return len(self.findings)


class VisionAnalyzer:
    """
    KARYA industrial vision analysis layer.

    This class converts generic vision inference into
    domain-specific industrial inspection operations.
    """

    def __init__(self, service: VisionService | None = None):
        self.service = service or VisionService()

    def analyze(
        self,
        image_path: str,
        prompt: str,
        model: str | None = None,
    ) -> IndustrialAnalysis:
        """
        Perform a generic industrial image analysis.
        """

        response = self.service.analyze(
            prompt=prompt,
            image_path=image_path,
            model=model,
        )

        return self._build_analysis(
            image_path=image_path,
            response=response,
        )

    def inspect_equipment(
        self,
        image_path: str,
        model: str | None = None,
    ) -> IndustrialAnalysis:
        """
        Inspect industrial equipment for visible condition issues.
        """

        prompt = """
You are KARYA, a sovereign industrial equipment inspection AI.

Inspect the provided image carefully.

Analyze:

1. Equipment type
2. Equipment identification markings if visible
3. Physical condition
4. Corrosion
5. Cracks
6. Leaks
7. Deformation
8. Missing or damaged components
9. Signs of overheating
10. Smoke or unusual emissions
11. Visible safety hazards
12. Possible maintenance concerns

For every observation:

- Describe only what is visually supported.
- Do not invent measurements.
- Do not assume hidden conditions.
- Clearly distinguish observation from interpretation.

End with:

OVERALL CONDITION:
IMMEDIATE ACTION:
RECOMMENDED INSPECTION:
CONFIDENCE:
""".strip()

        return self.analyze(
            image_path=image_path,
            prompt=prompt,
            model=model,
        )

    def inspect_safety(
        self,
        image_path: str,
        model: str | None = None,
    ) -> IndustrialAnalysis:
        """
        Inspect an industrial scene for visible safety hazards.
        """

        prompt = """
You are KARYA, an industrial safety inspection AI.

Analyze the provided image for visible workplace and equipment
safety hazards.

Look for:

1. Missing PPE
2. Unsafe worker positioning
3. Exposed electrical components
4. Open or unguarded machinery
5. Leaks or spills
6. Fire hazards
7. Blocked access or emergency routes
8. Damaged safety barriers
9. Unsafe storage
10. Warning signs or labels
11. Structural hazards
12. Other clearly visible safety risks

For each finding provide:

- What is visible
- Why it may be a safety concern
- Severity: LOW / MEDIUM / HIGH / CRITICAL
- Recommended immediate action

Do not claim a hazard exists when the image does not provide
enough visual evidence.

End with:

SAFETY STATUS:
CRITICAL FINDINGS:
RECOMMENDED ACTION:
CONFIDENCE:
""".strip()

        return self.analyze(
            image_path=image_path,
            prompt=prompt,
            model=model,
        )

    def inspect_damage(
        self,
        image_path: str,
        model: str | None = None,
    ) -> IndustrialAnalysis:
        """
        Analyze an image specifically for visible physical damage.
        """

        prompt = """
Analyze this industrial image specifically for physical damage.

Look for:

- cracks
- corrosion
- dents
- deformation
- broken components
- damaged insulation
- damaged piping
- damaged valves
- damaged cables
- leaks
- unusual discoloration
- burn marks
- structural damage

For each detected issue:

1. Identify the affected component if visible.
2. Describe the visible evidence.
3. Classify severity as LOW, MEDIUM, HIGH, or CRITICAL.
4. Suggest the next inspection or maintenance action.

Do not invent details that cannot be seen.

Clearly state when no visible damage can be confirmed.

End with:

DAMAGE STATUS:
MOST IMPORTANT FINDING:
RECOMMENDED ACTION:
CONFIDENCE:
""".strip()

        return self.analyze(
            image_path=image_path,
            prompt=prompt,
            model=model,
        )

    def analyze_drawing(
        self,
        image_path: str,
        model: str | None = None,
    ) -> IndustrialAnalysis:
        """
        Analyze an engineering drawing, diagram, chart, or schematic.
        """

        prompt = """
You are KARYA, an industrial engineering document analysis AI.

Analyze the provided engineering drawing, diagram, schematic,
chart, or technical image.

Extract only information that is visibly readable.

Identify where possible:

1. Equipment names
2. Equipment tags
3. Component labels
4. Pipes or connections
5. Flow direction
6. Valves
7. Instruments
8. Measurements
9. Warnings
10. Tables
11. Important annotations
12. Relationships between visible components

Preserve exact identifiers and numbers when readable.

If text is unclear, explicitly state that it is unclear.

Do not hallucinate missing labels or values.

Return the analysis in a structured engineering-oriented format.

End with:

KEY COMPONENTS:
IMPORTANT VALUES:
IMPORTANT RELATIONSHIPS:
UNCLEAR INFORMATION:
CONFIDENCE:
""".strip()

        return self.analyze(
            image_path=image_path,
            prompt=prompt,
            model=model,
        )

    def _build_analysis(
        self,
        image_path: str,
        response: VisionResponse,
    ) -> IndustrialAnalysis:
        """
        Convert raw VisionResponse into the structured
        IndustrialAnalysis representation.
        """

        return IndustrialAnalysis(
            image_path=image_path,
            model=response.model,
            content=response.content.strip(),
            findings=[],
        )