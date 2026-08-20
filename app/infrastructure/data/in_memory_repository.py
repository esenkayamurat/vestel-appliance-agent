"""ApplianceDataRepositoryPort'un CSV tabanli implementasyonu. GCP'ye hic dokunmaz;
scripts/generate_mock_usage_data.py ile uretilen sahte veriyi okuyup agent'i
gercek BigQuery semasi gelmeden test edebilmemizi sagliyor."""

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

from app.application.ports import ApplianceDataRepositoryPort
from app.domain.entities import ApplianceUsageResult, DateRange, ProgramUsageResult


class InMemoryApplianceRepository(ApplianceDataRepositoryPort):
    def __init__(self, csv_path: str | Path):
        with open(csv_path, encoding="utf-8") as f:
            self._rows = list(csv.DictReader(f))

    def most_used_program(
        self, appliance_type: str, date_range: DateRange
    ) -> list[ProgramUsageResult]:
        counts = Counter(
            row["program_adi"]
            for row in self._rows
            if row["cihaz_tipi"] == appliance_type and self._in_range(row, date_range)
        )
        return [
            ProgramUsageResult(appliance_type=appliance_type, program_name=name, usage_count=count)
            for name, count in counts.most_common()
        ]

    def most_preferred_appliance(self, date_range: DateRange) -> list[ApplianceUsageResult]:
        counts = Counter(
            row["cihaz_tipi"] for row in self._rows if self._in_range(row, date_range)
        )
        return [
            ApplianceUsageResult(appliance_type=name, usage_count=count)
            for name, count in counts.most_common()
        ]

    @staticmethod
    def _in_range(row: dict, date_range: DateRange) -> bool:
        row_date = datetime.fromisoformat(row["baslangic_zamani"]).date()
        return date_range.start <= row_date <= date_range.end
