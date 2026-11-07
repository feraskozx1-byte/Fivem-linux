# إعادة التحقق والتراجع

كل الأوامر من `/home/feras/Projects/FiveM-PR4050-Test`. لا حاجة إلى نسخ مجلد تشغيل أو بناء FiveM.

## الأدلة المحفوظة، دون تشغيل Wine

```bash
python3 Diagnostics/2026-11-07-TLS-Causality/verify-results.py
python3 Diagnostics/2026-11-07-TLS-Causality/compare-causality.py
```

يتحقق الأول من ملفات Windows نفسها وبصماتها ونتائج29فحصًا والتحكم دون TLS والاستعادة. يعيد الثاني حساب المقارنة السببية من السجلين المكتملين. تفاصيل Windows native في `private/reference-{2022,2025}/native`، ومصادرها ووصفة CI في هذا المجلد وcommit المحدد في FINDINGS.

## إعادة بناء النموذج والعينة المستقلة

```bash
# يحرس بصمة نسخة Wine والتعليمة الأصلية، ويرفض استبدال ناتج مختلف.
python3 Diagnostics/2026-11-07-TLS-Causality/build-wine-prototype.py

# استخدم tag جديدًا إذا أعدت التجربة. تشغّل الملفات المرجعية نفسها.
python3 Diagnostics/2026-11-07-TLS-Causality/run-wine.py \
  --direct-wine --wine-prototype --tag tls-prototype-retest \
  --bin Diagnostics/2026-11-07-TLS-Causality/private/reference-2022/bin \
  --baseline Diagnostics/2026-11-07-TLS-Causality/private/reference-2022/native/tls-result.txt
```

المتوقع: RESULT=PASS و29تحققًا، و`public_API_returns_match_native=true` و`intended_prototype_behavior_observed=true`. نجاح TLS observations وحده لا يثبت دخول التصحيح؛ لذلك فحص الإرجاعات منفصل. إعادة بناء عيناتنا المحلية ممكنة بـ`build-local.sh`، لكنها ليست بديلًا عن مقارنة PE نفسها مع المرجع الأصلي.

## إعادة تجربة السببية، فقط عند الحاجة

```bash
bash Diagnostics/2026-11-07-TLS-Causality/build-observer.sh
python3 Diagnostics/2026-11-07-TLS-Causality/run-api-observer.py \
  --fixture --direct-wine --tag tls-observer-retest
python3 Diagnostics/2026-11-07-TLS-Causality/validate-api-observer.py \
  --tag tls-observer-retest

python3 Diagnostics/2026-11-07-TLS-Causality/run-api-observer.py \
  --direct-wine --tag tls-before-retest
python3 Diagnostics/2026-11-07-TLS-Causality/run-api-observer.py \
  --direct-wine --wine-prototype --tag tls-after-retest
python3 Diagnostics/2026-11-07-TLS-Causality/compare-causality.py \
  --before tls-before-retest --after tls-after-retest \
  --output causality-retest.json
```

المتوقع في traces المكتملة: الفرع داخل NTDLL يتغير من2674إلى0774، تزول إرجاعات الخطأ المرصودة، ويبقى AV عندD9FEC5 وتسلسل الفهارس نفسه و998 في CitizenFX. نجاح observer يعني اكتمال القياس؛ **لا يعني نجاح Adhesive**. قد ينهي runner عملية Wine بعد اكتمال observer لتنظيف عمليات launcher؛ لذلك لا يُستخدم exitcode الخاص بـrunner معيارًا لتحميل المكتبة.

المصحح ظاهر، ولا يكتب ذاكرة العملية ولا يغير قيم API عند العودة. كل التشغيل مع `--unshare=network`، وprefix تشخيصي فقط، وحد55ثانية وحد للسجل. لا تستخدم main prefix أو تشغيلًا غير معزول لهذه التجربة.

## التراجع

لا تعديل دائم يحتاج إلى تركيب DLL قديمة. تنتهي read-only mounts بخروج عمليات التجربة. يحفظ runner ربطS ويعيده ويوقف wineserver الخاص بـprefix التشخيصي فقط. بصمة NTDLL المثبتة ونسخة prefix بعد التجربة هي الأصلية `af292382429047a793ced19c8740a08ee1a8b95711cfec2eda4b5fb5dcc762c5`؛ راجع `verification.json`.

لا تطبق `loader-static-tls.patch` على نسخة Proton الرئيسية لعلاج Adhesive؛ الاختبار نفى هذه العلاقة. يحتفظ المجلد بالـpatch والنموذج والأدلة لدراسة توافق الواجهة العامة. اختبارنا نموذج ثنائي محدود مع patch مصدر؛ ليس بناء Wine من المصدر ولا اجتياز حزمة اختبارات Wine الشاملة.
