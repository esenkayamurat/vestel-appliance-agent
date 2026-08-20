"""ApplianceDataRepositoryPort'un BigQuery implementasyonu.

Gercek tablo/kolon isimleri mentorden veri gelene kadar bilinmiyor -- bu yuzden
sorgular simdilik yazilmadi. Iskeletin geri kalani (dependency injection, port'a
bagimlilik) degismeyecek; sadece asagidaki SQL'lerin ic kismi doldurulacak.
"""

from google.cloud import bigquery

from app.application.ports import ApplianceDataRepositoryPort
from app.domain.entities import ApplianceUsageResult, DateRange, ProgramUsageResult


class BigQueryApplianceRepository(ApplianceDataRepositoryPort):
    def __init__(self, project: str, dataset: str, table: str):
        self._client = bigquery.Client(project=project)
        self._table_ref = f"{project}.{dataset}.{table}"

    def most_used_program(
        self, appliance_type: str, date_range: DateRange
    ) -> list[ProgramUsageResult]:
        # TODO: gercek sema gelince parametrized SQL yaz (LIMIT + tarih filtresi zorunlu).
        raise NotImplementedError("Gercek BigQuery semasi bekleniyor.")

    def most_preferred_appliance(self, date_range: DateRange) -> list[ApplianceUsageResult]:
        # TODO: gercek sema gelince parametrized SQL yaz (LIMIT + tarih filtresi zorunlu).
        raise NotImplementedError("Gercek BigQuery semasi bekleniyor.")
