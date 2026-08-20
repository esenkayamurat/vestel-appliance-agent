"""Domain katmani: hicbir framework'e (FastAPI, Vertex AI, BigQuery) bagimli olmayan
saf is nesneleri. Gercek veri semasi gelince alanlar netlesecek, iskelet simdilik
ornek sorulardan (en cok kullanilan program / en cok tercih edilen cihaz) turetildi.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date


@dataclass(frozen=True)
class ProgramUsageResult:
    appliance_type: str
    program_name: str
    usage_count: int


@dataclass(frozen=True)
class ApplianceUsageResult:
    appliance_type: str
    usage_count: int


@dataclass(frozen=True)
class AgentAnswer:
    """Agent'in kullaniciya donecek nihai cevabi: dogal dil aciklama +
    varsa UI'da tablo/grafik olarak gosterilebilecek yapilandirilmis veri."""

    natural_language_answer: str
    structured_data: list[dict] | None = None
