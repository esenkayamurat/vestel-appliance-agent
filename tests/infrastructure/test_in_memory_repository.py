import csv
from datetime import date

from app.domain.entities import DateRange
from app.infrastructure.data.in_memory_repository import InMemoryApplianceRepository


def _write_csv(path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _sample_rows():
    return [
        {"cihaz_tipi": "camasir_makinesi", "program_adi": "Pamuklu", "baslangic_zamani": "2024-03-05T10:00:00"},
        {"cihaz_tipi": "camasir_makinesi", "program_adi": "Pamuklu", "baslangic_zamani": "2024-03-06T10:00:00"},
        {"cihaz_tipi": "camasir_makinesi", "program_adi": "Eko", "baslangic_zamani": "2024-03-06T10:00:00"},
        {"cihaz_tipi": "camasir_makinesi", "program_adi": "Pamuklu", "baslangic_zamani": "2024-05-01T10:00:00"},
        {"cihaz_tipi": "bulasik_makinesi", "program_adi": "Yogun", "baslangic_zamani": "2024-03-06T10:00:00"},
    ]


def test_most_used_program_filters_by_type_and_date_range(tmp_path):
    csv_path = tmp_path / "mock.csv"
    _write_csv(csv_path, _sample_rows())
    repo = InMemoryApplianceRepository(csv_path)

    results = repo.most_used_program(
        "camasir_makinesi", DateRange(start=date(2024, 3, 1), end=date(2024, 3, 31))
    )

    assert results[0].program_name == "Pamuklu"
    assert results[0].usage_count == 2
    assert sum(r.usage_count for r in results) == 3  # Mayis'taki kayit disarida kalmali


def test_most_preferred_appliance_counts_across_types(tmp_path):
    csv_path = tmp_path / "mock.csv"
    _write_csv(csv_path, _sample_rows())
    repo = InMemoryApplianceRepository(csv_path)

    results = repo.most_preferred_appliance(DateRange(start=date(2024, 3, 1), end=date(2024, 3, 31)))

    assert results[0].appliance_type == "camasir_makinesi"
    assert results[0].usage_count == 3
