"""Gercek BigQuery semasi gelene kadar, agent'i ve sorgu mantigini test edebilmek
icin yerel bir sahte "cihaz kullanim kaydi" veri seti uretir. Cikti data/mock_usage_data.csv
dosyasina yazilir; hicbir GCP servisine dokunmaz.

Sema, mentorun verdigi iki ornek soruya (son bir hafta en cok kullanilan program,
belirli bir ayda en cok tercih edilen beyaz esya) gore tasarlandi. Gercek sema
gelince alanlar degisebilir, ama InMemoryApplianceRepository'nin sekli benzer kalacak.
"""

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

APPLIANCE_PROGRAMS = {
    "camasir_makinesi": {
        "Pamuklu": 0.40,
        "Sentetik": 0.20,
        "Hizli Yikama": 0.20,
        "Yunluler": 0.10,
        "Eko": 0.10,
    },
    "bulasik_makinesi": {
        "Yogun": 0.30,
        "Normal": 0.40,
        "Hizli": 0.20,
        "Eko": 0.10,
    },
    "buzdolabi": {
        "Ekonomik": 0.50,
        "Super Frizer": 0.20,
        "Tatil Modu": 0.10,
        "Normal": 0.20,
    },
    "firin": {
        "Ust-Alt Ates": 0.35,
        "Izgara": 0.20,
        "Pizza": 0.20,
        "Fan Destekli": 0.25,
    },
    "klima": {
        "Sogutma": 0.55,
        "Isitma": 0.20,
        "Nem Alma": 0.15,
        "Fan": 0.10,
    },
}

APPLIANCE_WEIGHTS = {
    "camasir_makinesi": 0.35,
    "bulasik_makinesi": 0.25,
    "buzdolabi": 0.20,
    "firin": 0.12,
    "klima": 0.08,
}

CITIES = {
    "Istanbul": 0.35,
    "Ankara": 0.20,
    "Izmir": 0.15,
    "Bursa": 0.15,
    "Antalya": 0.15,
}


def weighted_choice(weights: dict[str, float]) -> str:
    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-rows", type=int, default=8000)
    parser.add_argument("--start-date", default="2024-01-01")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output", default=str(Path(__file__).resolve().parent.parent / "data" / "mock_usage_data.csv")
    )
    args = parser.parse_args()

    random.seed(args.seed)

    start = datetime.strptime(args.start_date, "%Y-%m-%d")
    end = datetime.now()
    total_seconds = int((end - start).total_seconds())

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for _ in range(args.num_rows):
        appliance_type = weighted_choice(APPLIANCE_WEIGHTS)
        program_name = weighted_choice(APPLIANCE_PROGRAMS[appliance_type])
        usage_time = start + timedelta(seconds=random.randint(0, total_seconds))

        rows.append(
            {
                "kullanim_id": str(uuid.uuid4()),
                "cihaz_id": f"{appliance_type[:2].upper()}-{random.randint(100000, 999999)}",
                "cihaz_tipi": appliance_type,
                "program_adi": program_name,
                "baslangic_zamani": usage_time.isoformat(),
                "sure_dakika": random.randint(20, 180),
                "enerji_tuketimi_kwh": round(random.uniform(0.3, 2.5), 2),
                "sehir": weighted_choice(CITIES),
            }
        )

    rows.sort(key=lambda r: r["baslangic_zamani"])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Uretilen satir sayisi: {len(rows)}")
    print(f"Tarih araligi: {rows[0]['baslangic_zamani']} -> {rows[-1]['baslangic_zamani']}")
    print(f"Yazildi -> {output_path}")


if __name__ == "__main__":
    main()
