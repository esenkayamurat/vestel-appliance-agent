# Vestel Agentic Appliance Insights

GitHub: `https://github.com/esenkayamurat/vestel-appliance-agent`

Beyaz eşyalardan toplanan kullanım verisi üzerinde doğal dilde soru sorulabilen bir agent projesi. Kullanıcı "son bir haftada en çok hangi çamaşır makinesi programı kullanıldı?" gibi bir soru sorduğunda, Vertex AI Gemini bu soruyu önceden tanımlanmış tool'lar aracılığıyla bir BigQuery sorgusuna çevirip çalıştırıyor, sonucu da hem doğal dilde hem yapılandırılmış veri olarak geri döndürüyor.

**Şu anki durum: iskelet aşaması.** Mentörden gerçek BigQuery verisi gelmeden `infrastructure/` katmanındaki sorgular ve Gemini entegrasyonu yazılamayacağı için, bu kısımlar bilerek `NotImplementedError` olarak bırakıldı. Mimari önceden kurulup test edildi; veri geldiğinde tek yapılması gereken bu katmanın içini doldurmak.

## Neden Clean Architecture

Projeyi dört katmana ayırdık, her katmanın tek bir sorumluluğu var:

- **`domain/`** — hiçbir framework'e bağımlı olmayan saf iş nesneleri (`DateRange`, `ProgramUsageResult`, `AgentAnswer` gibi).
- **`application/`** — use case'ler ve bunların dayandığı soyut arayüzler (port'lar). Bu katmanda Vertex AI ya da BigQuery'ye dair tek bir satır kod yok.
- **`infrastructure/`** — port'ların gerçek implementasyonları: `VertexGeminiAgentAdapter` ve `BigQueryApplianceRepository`. Yarın model ya da veri kaynağı değişirse yalnızca burası değişir, geri kalan hiçbir şey etkilenmez.
- **`presentation/`** — FastAPI ile kurulan HTTP katmanı. Sadece istek/cevap dönüşümü ve bağımlılıkların birbirine bağlanması burada, iş mantığı burada değil.

Bağımlılıklar hep içe doğru akıyor: `infrastructure` ve `presentation`, `application`'daki port'lara bağımlı; `application` ve `domain` ise dışarıda ne olup bittiğini bilmiyor. Bunun somut faydasını `tests/application/test_answer_user_query.py` içinde görebilirsin — use case'i gerçek GCP servislerine hiç dokunmadan, sahte (fake) bir agent implementasyonuyla test edebiliyoruz.

## Proje yapısı

```
app/
  domain/              entities.py, exceptions.py
  application/         ports.py (arayüzler), use_cases/
  infrastructure/
    llm/                 VertexGeminiAgentAdapter (Gemini function calling)
    data/                BigQueryApplianceRepository
  presentation/
    api/                 FastAPI giriş noktası (main.py)
tests/
  application/         use case testleri, mock/fake ile GCP'ye dokunmadan çalışır
  infrastructure/      ileride: gerçek BigQuery/Vertex AI entegrasyon testleri
scripts/               gcloud/bq kurulum script'leri (henüz boş)
ui/                    sohbet arayüzü (henüz boş, ayrı bir aşamada eklenecek)
```

## Şu ana kadar netleşen kapsam

Mentörle yaptığımız ilk konuşmadan çıkan birkaç önemli nokta:

- Beklenen sorular ağırlıklı olarak agregasyon/analitik tipte — "son bir haftada en çok hangi program kullanıldı", "Mart 2024'te en çok tercih edilen beyaz eşya hangisi" gibi. Yani karmaşık çok adımlı akıl yürütmeden çok, doğru parametrelerle bir COUNT/GROUP BY/tarih filtresi sorgusuna çevirme işi.
- Proje önce demo/pilot olarak çalışacak, ihtiyaca göre daha geniş erişime açılabilir. Bu yüzden şimdilik bir auth katmanı yok, ama `presentation/` katmanına sonradan kolayca eklenebilecek şekilde bırakıldı.
- Mentör belirli bir referans mimari beklemiyor, genel clean architecture prensiplerine uyum yeterli.

## Nasıl çalıştırılır (gerçek veri/entegrasyon tamamlanınca)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GCP_PROJECT=<proje-id>
export BQ_DATASET=<dataset>
export BQ_TABLE=<tablo>

python -m uvicorn app.presentation.api.main:app --reload --host 0.0.0.0 --port 8080
```

## Sırada ne var

1. Sahte (mock) veriyle Vertex AI Gemini function-calling akışını uçtan uca deneyip `VertexGeminiAgentAdapter`'ın içini doldurmak.
2. Mentörden gerçek BigQuery şeması gelince `BigQueryApplianceRepository`'deki sorguları yazmak.
3. `ui/` altında basit bir sohbet arayüzü eklemek.
