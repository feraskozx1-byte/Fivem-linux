# إعادة التحقق

من `/home/feras/Projects/FiveM-PR4050-Test`:

```bash
# مقارنة metadata الأصلية المحفوظة؛ لا تشغيل للعميل أو TLS:
python3 Diagnostics/2026-11-07-Export-Bounds/audit-export-contract.py

# تحليل القياس النهائي، بما فيه العدد وDR7 عند AV:
python3 Diagnostics/2026-11-07-Export-Bounds/analyze-observation.py \
  --tag fullhost-fault-audit --output fault-audit-evidence.json

python3 Diagnostics/2026-11-07-Export-Bounds/verify-preservation.py
```

الأدلة الأصلية: `private/fullhost-fault-audit/export-resolver-observer.txt` وCitizenFX log بجواره، مع manifest بناء الأداة المطابقة في `observer-build-validation.json`. نتائج التحكم في `private/observer-fault-audit-control/export-fixture.txt` وسجل الأداة بجواره.

عند الحاجة إلى قياس جديد، استخدم tags غير موجودة:

```bash
bash Diagnostics/2026-11-07-Export-Bounds/build.sh
python3 Diagnostics/2026-11-07-Export-Bounds/run-observer.py \
  --fixture --direct-wine --tag control-retest
python3 Diagnostics/2026-11-07-Export-Bounds/validate-observer.py \
  --tag control-retest

# بعد نجاح التحكم المطابق فقط:
python3 Diagnostics/2026-11-07-Export-Bounds/run-observer.py \
  --direct-wine --tag bounds-retest
python3 Diagnostics/2026-11-07-Export-Bounds/analyze-observation.py \
  --tag bounds-retest --output bounds-retest.json
```

العينة مستقلة وليست بديلًا للحماية. تشغيلها عبر observer يختبر أيضًا التتبع المتداخل وread/write watchpoint؛ ملف التحكم ينجح في8تحققات. لا يُحسب اكتمال observer نجاحًا لـAdhesive، ولا يُحسب انتهاء مهلة قبل lookup قياسًا سلبيًا للواجهات أو الحقل.

المراقبة مقتصرة على الخيط الرئيسي أثناء PROCESS_ATTACH، وبنقاط عتادية ظاهرة؛ AV يُمرر NOT_HANDLED. لا كتابة إلى كود/ذاكرة الطفل ولا تغيير لنتائج API. يتم تعطيل الشبكة واستخدام prefix تشخيصي منفصل، مع cleanup لهذا prefix فقط واستعادة ربطS. لا تعمل على prefix الحساب الرئيسي.

كل التعديلات في مجلد التشخيص هذا. لا Wine/FiveM patch للتركيب أو التراجع عنه، ولا DLL أصلية استُبدلت. احتُفظ بنسخ مصادر observer السابقة بـ`.bak` لتوثيق تصحيح الأداة. ملفات source/PE والـlogs صغيرة؛ لا توجد نسخة مجلد FiveM جديدة.
