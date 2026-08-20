# Vestel Agentic Appliance Insights

Beyaz esya kullanim verisi uzerinde dogal dilde soru sorulabilen bir agent:
kullanici "son bir haftada en cok hangi camasir makinesi programi kullanildi?"
gibi sorular sorar, Vertex AI Gemini bu soruyu tanimli tool'lar araciligiyla
BigQuery sorgusuna cevirir, sonuc dogal dilde ve yapilandirilmis veri olarak doner.

**Durum: iskelet asamasi.** Mentorden gercek BigQuery verisi gelene kadar
`infrastructure/` katmanindaki sorgular/agent entegrasyonu bilerek `NotImplementedError`
birakildi -- mimari onceden kurulup test edildi, veri gelince sadece bu katman doldurulacak.

## Neden bu yapida (Clean Architecture)

- `domain/` — hicbir framework'e bagimli olmayan saf is nesneleri (Appliance, UsageRecord, AgentAnswer).
- `application/` — use case'ler + port (soyut arayuz) tanimlari. Somut Vertex AI/BigQuery koduna burada referans yok.
- `infrastructure/` — port'larin gercek implementasyonlari (`VertexGeminiAgentAdapter`, `BigQueryApplianceRepository`). Yarin model/veri kaynagi degisirse sadece burasi degisir.
- `presentation/` — FastAPI HTTP katmani; sadece istek/cevap donusumu ve dependency wiring yapar.

Bagimlilik yonu hep ice dogru: `infrastructure` ve `presentation`, `application`'daki
port'lara bagimli; `application` ve `domain` ise disaridaki hicbir seyi bilmez.
Bu sayede `tests/application/test_answer_user_query.py`'de gordugun gibi, use case'ler
gercek GCP servislerine dokunmadan sahte (fake) implementasyonlarla test edilebiliyor.

## Proje yapisi

```
app/
  domain/            # entities.py, exceptions.py
  application/        # ports.py (arayuzler), use_cases/
  infrastructure/
    llm/               # VertexGeminiAgentAdapter (Gemini function calling)
    data/              # BigQueryApplianceRepository
  presentation/
    api/               # FastAPI (main.py)
tests/
  application/         # use case testleri (mock/fake ile, GCP'ye dokunmuyor)
  infrastructure/       # ileride: gercek BigQuery/Vertex AI entegrasyon testleri
scripts/               # gcloud/bq kurulum script'leri (henuz bos)
ui/                    # sohbet arayuzu (henuz bos, ayri asamada eklenecek)
```

## Su ana kadar netlesen kapsam

- Ornek sorular: "son bir haftada en cok hangi program kullanildi", "Mart 2024'te en cok tercih edilen beyaz esya hangisi" — yani agregasyon/analitik tipi sorular (COUNT, GROUP BY, tarih filtresi).
- Baslangicta demo/pilot olarak calisacak, ihtiyaca gore erisime aciliabilir — bu yuzden auth katmani simdilik yok, ileride `presentation/` katmanina eklenebilecek sekilde birakildi.
- Genel clean architecture prensiplerine uyum yeterli, belirli bir referans yapi zorunlulugu yok.

## Calistirmak icin (gercek veri/entegrasyon tamamlaninca)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GCP_PROJECT=<proje-id>
export BQ_DATASET=<dataset>
export BQ_TABLE=<tablo>

python -m uvicorn app.presentation.api.main:app --reload --host 0.0.0.0 --port 8080
```

## Sonraki adimlar

1. Mock veriyle Vertex AI Gemini function-calling akisini uctan uca denemek (`VertexGeminiAgentAdapter` icini doldurmak).
2. Mentorden gercek BigQuery semasi gelince `BigQueryApplianceRepository`'deki sorgulari yazmak.
3. `ui/` altinda basit bir sohbet arayuzu eklemek.
