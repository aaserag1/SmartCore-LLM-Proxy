# SmartCore LLM Proxy

بوابة محلية متوافقة مع OpenAI توحّد الوصول إلى نماذج الذكاء الاصطناعي عبر LiteLLM، وتعيد المحاولة عند الأخطاء المؤقتة، ثم تنتقل تلقائيًا من Gemini إلى DeepSeek من دون تغيير إعدادات التطبيق.

> [English documentation](README.md)

## المميزات

- رابط OpenAI موحّد يعمل مع Hermes AI وOpen WebUI والبرامج الخلفية.
- إعادة محاولات وفترة تهدئة وتحويل تلقائي إلى مزود احتياطي.
- قراءة المفاتيح من متغيرات البيئة بدل تخزينها في `config.yaml`.
- حماية البوابة بمفتاح رئيسي وربطها بالجهاز المحلي افتراضيًا.
- تشغيل على Windows وmacOS وLinux أو Docker Compose.
- فحص تلقائي للإعدادات واختبارات عبر GitHub Actions.

المشروع يحسن الاستمرارية لكنه لا يضمن عمل الخدمة بنسبة 100%، لأن التوفر يعتمد أيضًا على الشبكة وحسابات المزودين وحدود الاستخدام.

## تشغيل سريع

### 1. التثبيت

```bash
git clone https://github.com/aaserag1/SmartCore-LLM-Proxy.git
cd SmartCore-LLM-Proxy
python -m venv .venv
```

فعّل البيئة:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

ثم ثبّت الإصدار المحدد من LiteLLM:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. إعداد المفاتيح

انسخ ملف المثال:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

أضف القيم التالية داخل `.env`:

- `GEMINI_API_KEY`: مفتاح Google AI Studio.
- `DEEPSEEK_API_KEY`: مفتاح DeepSeek.
- `LITELLM_MASTER_KEY`: مفتاح خاص بالبوابة يبدأ بـ `sk-`.

يمكن توليد مفتاح قوي للبوابة بالأمر:

```bash
python -c "import secrets; print('sk-' + secrets.token_urlsafe(32))"
```

لا ترفع ملف `.env` أو أي مفتاح حقيقي إلى GitHub.

### 3. الفحص والتشغيل

```bash
python scripts/start_proxy.py --check-only
python scripts/start_proxy.py
```

على Windows يمكنك أيضًا تشغيل:

```powershell
.\Run_LiteLLM.bat
```

وعلى macOS أو Linux:

```bash
./run.sh
```

### 4. ربط Hermes AI

| الإعداد | القيمة |
| --- | --- |
| Base URL | `http://127.0.0.1:4000/v1` |
| API key | قيمة `LITELLM_MASTER_KEY` |
| Model | `smart-core` |

يستخدم `smart-core` نموذج Gemini 2.5 Flash أولًا، ثم ينتقل إلى `deepseek-chat` عند فشل المحاولات القابل لإعادة المحاولة.

## التشغيل عبر Docker

```bash
docker compose up -d
docker compose logs -f smartcore
```

للإيقاف:

```bash
docker compose down
```

## تخصيص النماذج

عدّل `config.yaml`، واجعل أي مفتاح سري مرجعًا بالشكل:

```yaml
api_key: os.environ/MY_PROVIDER_API_KEY
```

النماذج التي تحمل `model_name` نفسه تدخل في مجموعة موازنة تحميل واحدة. ويمكن وضع مجموعة مختلفة ضمن `router_settings.fallbacks` لتعمل كبديل.

بعد كل تعديل شغّل:

```bash
python scripts/check_config.py config.yaml
```

للمساهمة اقرأ [CONTRIBUTING.md](CONTRIBUTING.md)، وللإبلاغ الأمني اقرأ [SECURITY.md](SECURITY.md).

## الترخيص

المشروع متاح تحت [رخصة MIT](LICENSE).

تطوير أحمد عادل (أبو عادل)، والمساهمات المجتمعية مرحب بها.
