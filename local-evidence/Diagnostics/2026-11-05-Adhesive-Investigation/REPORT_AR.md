# تحقيق Adhesive — 2026-11-05

**النتيجة: فشل التحميل؛ لا يوجد إصلاح توافق مثبت أو نجاح جزئي لتهيئة Adhesive.** بُني اختبار صغير ونُفّذت خمس تجارب فعلية دون شبكة. جميعها وصلت إلى تهيئة المكتبة ثم أعادت 998. لم تُبنَ FiveM بالكامل ولم يُعد بناء CoreRT؛ اختُبرت نسختاه الموجودتان بالفعل.

## Root Cause

السبب المباشر المثبت في الاختبار المستقل هو استثناء قراءة `0xC0000005` داخل المكتبة الرسمية عند `adhesive.dll+0xD9FEC5`، خلال `PROCESS_ATTACH` وسلسلة تهيئة CRT عبر `_initterm`. ترجع عملية التحميل handle صفريًا و`GetLastError=998` بعد فشل التهيئة. التعليمة المسجلة سابقًا تقرأ بايتًا من `r9+rax`.

أضاف اختبار v4 استعلام `VirtualQuery` وقت الاستثناء: العنوان المطلوب في التجارب الخمس ضمن منطقة `MEM_FREE (0x10000)`. هذا يثبت قراءة ذاكرة غير مخصصة وفق ما يعيده Wine. حقول Protect وType وAllocationBase غير معرّفة لهذه الحالة؛ لا نستنتج منها سببًا إضافيًا أو نقترح تغيير صلاحيات الذاكرة. [تعريف Microsoft](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-memory_basic_information).

**أصل المؤشر غير الصالح لم يُحدد.** لا توجد API عامة معينة ثبت أنها أعادت نتيجة خاطئة. لا يثبت المكدس وحده عيب UCRT أو TLS callback أو شرط رفض مقصود أو حاجة إلى kernel driver. تصحيح Wine أو تعديل التعليمات داخل Adhesive دون هذا الدليل سيكون تخمينًا.

هناك حد مهم للدليل: الاختبار يهيئ CoreRT أولًا ثم يحمّل Adhesive، ولا يعيد سياق عميل FiveM كله. سجل العميل التاريخي يثبت 998، لكنه لا يسجل التعليمة المسببة. لذلك **لم تثبت بعد مطابقة RVA الاختبار المعزول مع أول عطل في العميل الكامل**. يلزم tracing معتمد في المضيف الكامل أو تشخيص من Cfx.re.

## المرحلة A — الحالة الحالية

- المصدر على `wine-proton-fix` عند `ba07d9d3d5bd8459b69a81c69eb6065d4e11273c`، مطابق لمرجع `origin/wine-proton-fix` المحلي. التاريخ shallow؛ مقارنة الفرع الأساسي الرسمي كاملة غير متاحة محليًا. حُفظت حالة Git والـdiff الحالي قبل العمل.
- أربعة ملفات معدلة مسبقًا: DllGameComponent وSEHTableHandler وEarlyMode وXBRInit، بإجمالي +38/-16. توجد ملفات بناء مستهدف ونسخة backup غير متتبعة مسبقًا. لم تتغير هذه الحالة في التحقيق.
- تعديل DllGameComponent الموجود يمنع كتابة flag تعتمد على تخطيط Windows الداخلي تحت Wine. تغيير EarlyMode الموجود يزيل استدعاء `WineCompat_InstallHooks`. تغييرات SEH موجودة؛ XBRInit خارج سبب Adhesive المثبت.
- الشيفرة الأساسية ما زالت تحتوي تنفيذ hook لإخفاء Wine في `WineCompat.Win32.cpp`. لا يستدعي الاختبار EarlyMode أو ذلك التنفيذ أو أي component factory. لا نعيد تفعيله.
- `DllGameComponent.Win32.cpp:125` يستدعي `LoadLibrary`. الأسطر 138–147 تحتوي fallback الموجود إلى Sticky عند فشل التحميل. الأسطر 199–207 تستطيع اختيار Sticky مبكرًا عند فشل قراءة manifest؛ لذلك مرحلة pre-gameload وحدها ليست إثباتًا.
- سجل `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T202008.log:3` يثبت محاولة تحميل فاشلة 998 ثم fallback. ملف `adhesive-wine-debug.log` هو سجل wrapper لـHeroic ولا يحتوي stack لعطل Adhesive.
- **`Run-CoreRT-Test/adhesive.dll` غير موجود حاليًا.** السجل `CitizenFX_log_2026-11-05T124119.log:166` يثبت Sticky فقط؛ لا يختبر Adhesive مع CoreRT الجديد. النسختان تحتويان Sticky بالبصمة نفسها. هذا اختلاف ملفات وليس دليلًا على نجاح الحماية.
- CoreRT القديم SHA256: `b38ab16c25c9bf72b537e9e1acfef5411a0939d6289c953f28b4ac2358fc8013`.
- CoreRT الجديد SHA256: `cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64`؛ يطابق القيمة المقدمة لنتيجة CI 42019993897.
- Adhesive في Run-Adhesive-Test يطابق المرجع المحلي `Official-Reference/adhesive-24769.dll`: `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`، الحجم 54,552,672 بايت. لم يُعد تنزيله أو تغييره.
- اختلاف الإعدادات: DefaultBuild في نسخة Adhesive هو 3889 وفي CoreRT هو 3258. سُجل للمقارنة فقط؛ لا يستخدمه اختبار التحميل ولم يُعدل.
- Proton الفعلي `cachyos-11.0-20261015-slr`، Wine `wine-11.0 (CachyOS)`، Heroic Flatpak v2.22.4 على runtime 26.08. جميع المسارات التي حددها المستخدم موجودة.
- فُحصت streams الوحدات والاستثناءات في 20 dump، تمثل 13 بصمة مختلفة. لا يحتوي أي منها Adhesive ضمن الوحدات المحملة؛ لا يلتقط أي منها عطل تهيئته. التفاصيل في `minidump-summary.json`؛ لم تُنشر محتويات الذاكرة.

الدليل المحفوظ: `baseline.json` و`git-status-before.txt` و`existing-source-before.patch` و`evidence-audit.md`. اختبارات المرحلة: قراءة وتحقيق فقط. لم تُعدل ملفات موجودة.

## Tests — المرحلتان B وC

بُني `loader-probe.exe` من C باستخدام clang/LLVM محليًا، دون CRT أو SDK أو تنزيل أدوات. بُني مع `-Wall -Wextra -Werror`. يستورد Kernel32 فقط، ويحمّل CoreRT المحدد باستخدام loader المعتاد ثم نسخة Adhesive نفسها، دون تشغيل CreateComponent. logger الاستثناءات يرجع دائمًا `CONTINUE_SEARCH` ولا يعدل السياق أو الذاكرة.

استخدمت التجارب prefix تشخيصًا قائمًا بلا حسابات تحت `Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix`؛ لم يُنسخ prefix الرئيسي. شُغلت عبر UMU الموجود في Heroic وProton-CachyOS، مع `flatpak --unshare=network` ومنح مجلدي التشغيل read-only. حُددت مهلة 55 ثانية وسقف الملف 8 MiB. لم تقع مهلة أو يصل سجل إلى السقف؛ كل سجل نحو 2.3–2.5 MB، ونحو 17 ألف سطر، وليس مئات الآلاف. الملخصات المنقحة تحفظ الجزء المرتبط بالعطل فقط.

| التجربة | CoreRT | C++ runtime | عنوان القراءة | النتيجة |
| --- | --- | --- | --- | --- |
| old-builtin-1 | القديم | Wine | `0xA5D1CA` | 998، AV عند `+0xD9FEC5` |
| new-builtin-1 | الجديد | Wine | `0xA5BEFA` | 998، AV عند `+0xD9FEC5` |
| new-native-vc-1 | الجديد | Microsoft MSVCP/VCRUNTIME؛ Wine UCRT | `0xA4D50A` | 998، AV عند `+0xD9FEC5` |
| new-builtin-repeat | الجديد | Wine بعد استعادة الملفات | `0xA5BEFA` | 998، AV عند `+0xD9FEC5` |
| new-native-vc-ucrt-1 | الجديد | Microsoft MSVCP/VCRUNTIME وUCRT | `0xA4FB1A` | 998، AV عند `+0xD9FEC5` |

CoreRT preload نجح في الخمس، دون استثناءات مرصودة. أثبت كل اختبار مسار CoreRT المحمل فعليًا. اختلاف العنوان المطلق للمكتبة بين العمليات لا يغير RVA الفشل. جميع مناطق القراءة `MEM_FREE`، وجميع اختبارات probe اكتملت بخروج 10 الذي يعرّفه البرنامج لفشل تحميل Adhesive.

وجد الفحص ثمانية **data exports** مفقودة في MSVCP140 الخاص بـWine، تخص `std::locale::id` لفئات money_get/money_put/moneypunct. يضع Wine stubs بدلها؛ صفر استثناءات أثناء preload لا يثبت سلامتها. استُخدمت نسخة Microsoft الموجودة في prefix المستخدم، إصدار 14.44.35211.0، مع vcruntime140 وvcruntime140_1 المطابقين، داخل prefix التشخيص فقط. أزيلت تحذيرات الاستيرادات الثمانية فعليًا وبقي العطل نفسه. **توفير هذه الاستيرادات وحده لم يحل العطل؛ لا نزعم أن جميع واجهات Wine سليمة.**

أضيفت تجربة UCRT منفصلة، باستخدام النسخة الموجودة محليًا إصدار 10.0.10586.15. تحميلها native مثبت بالسجل؛ تغير إطار `_initterm` من Wine `+0x3560A` إلى native `+0x51AF` (`_initterm+0x4F`)، وبقيت إزاحة العطل داخل Adhesive نفسها. ظهور `_initterm` يصف تشغيل initializers وفق [توثيق Microsoft](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/initterm-initterm-e?view=msvc-170)، ولا يحدد أصل المؤشر.

فُحصت التواقيع محليًا: نجح OpenSSL في التحقق من التوقيع باستخدام الشهادة المضمنة، وطابقت SHA256 لصورة PE الـdigest في المحتوى الموقّع، للمكتبة المرجعية وأربع مكتبات Microsoft. **لم تُفحص سلسلة الثقة أو الإلغاء أو مصدر التنزيل التاريخي.** التفاصيل والقيود في `signature-checks.json` و`verify-local-signatures.py`؛ الفحص أوسع من قراءة أسماء الشهادات فقط.

## Fixes — المرحلة D

**لا يوجد patch تشغيلي مثبت لإصلاح Adhesive، ولم نطبق واحدًا.** لم يُعد بناء Wine أو CoreRT بلا سبب؛ بُني المكون التشخيصي المتأثر فقط. الشيفرة الجديدة تضيف مقارنة CoreRT وVirtualQuery وتسجيل نتيجة التحميل، ولا تمس منطق الحماية أو شروطها.

تجربتا Microsoft runtime كانتا تغيير توافق مؤقتًا لقياس احتمال اعتماد عام. نُقلت ملفات prefix التشخيص الأصلية إلى backup قبل الاستبدال، ثم أُعيدت في `finally`. ملفات `private/runtime-backup-*/restoration.json` تؤكد تطابق بصمات ما قبل وبعد. لم ينقل أو يبدل أي ملف في prefix الرئيسي.

كل الملفات الدائمة الجديدة داخل هذا المجلد فقط: مصدر الاختبار وبناؤه، runners، diff v3→v4، baseline، النتائج والأدلة والتقارير. `loader-probe-v3-v4.diff` يراجع تغيير الاختبار؛ `existing-source-before.patch` يسجل تعديلات المصدر السابقة ولا يمثل إصلاحًا جديدًا.

التراجع: لا توجد تغييرات منتج تحتاج التراجع. احتفظ بالتقارير أو احذف مجلد التحقيق الجديد لاحقًا إن أردت. لا تحذف prefix التشخيص القديم لأنه يحتوي أدلة سابقة. الاستعادة التلقائية للـruntime تمت؛ إذا قُطعت تجربة مستقبلية بـSIGKILL أو انقطاع طاقة قبل الاستعادة، أعد كل DLL من `private/runtime-backup-<tag>/` إلى system32 في **prefix التشخيص** فقط، طبقًا لـbefore.json، قبل تشغيل تجربة أخرى.

## Evidence — المرحلة E

- `trace-excerpts.txt`: مقتطفات منقحة ذات أرقام الأسطر الأصلية لكل تجربة.
- `results.json`: ملخص المقارنة القابل للقراءة آليًا.
- `private/<run>/probe-result.txt` و`summary.json`: CoreRT الفعلي، الاستثناء، VirtualQuery، نتيجة التحميل.
- `private/<run>/wine.log`: السجلات الكاملة المحلية؛ لا ترسلها تلقائيًا.
- `minidump-summary.json`: تصنيف dumps التاريخية.
- `preservation-check.json`: لا تغيير في الملفات ذات البصمات الأساسية، وحالة Git وdiff محفوظان كما كانا.
- `CFX_REPORT.md`: تقرير تقني إنجليزي معد للإرسال، **لم يُرسل أو يُرفع**.

شروط النجاح المطلوبة لم تتحقق: handle Adhesive صفر في كل اختبار، التهيئة لم تكتمل، الخطأ 998 ما زال قابلًا للتكرار، ولم تُختبر الوظائف الأمنية بعد التهيئة. الاختبار المستقل لا يحتوي fallback إلى Sticky؛ لذلك لا يمكنه إخفاء فشل التحميل ببديل. السجل التاريخي للعميل يحتوي fallback بالفعل. لم نختبر سيرفرًا أو مصادقة أو لعبة.

## Remaining Blockers

يلزم Cfx.re لتحديد وظيفة static initializer عند RVAs المسجلة، وأصل المؤشر المقروء، وتوفير رموز/تشخيص مناسب أو harness معتمد يستوفي سياق المضيف الكامل، أو تأكيد API عامة يمكن عزلها في اختبار Wine. إذا حُددت API عامة، فالخطوة التالية اختبار مستقل لسلوكها مقابل Windows الموثق ثم patch محدود وبناء هدف Wine المتأثر فقط. لن نستبدل المؤشرات أو نبتلع الاستثناء أو نغير نتائج فحوص الحماية.

راجعنا [تعليق Cfx.re على PR4050](https://github.com/citizenfx/fivem/pull/4050#discussion_r4289067271)، الذي يصف موقف دعم Linux للسيرفرات المحمية. هذا سياق دعم فقط؛ **ليس دليلًا على أن الاستثناء المرصود رفض متعمد**، ولا يحدد السبب التقني. لم نطلب أو نختبر اتصالًا بسيرفر.

## أوامر إعادة الاختبار

من جذر المشروع، استخدم tag جديدًا لكل تشغيل. المتطلبات موجودة محليًا، لا تثبيت أو صلاحيات مرتفعة. السكربتات متسلسلة وتستخدم prefix تشخيص واحدًا؛ لا تشغلها بالتوازي. `10` نتيجة فشل التحميل المقصودة، وليست خطأ في runner.

```bash
cd /home/feras/Projects/FiveM-PR4050-Test
bash Diagnostics/2026-11-05-Adhesive-Investigation/build-loader-probe.sh
python3 Diagnostics/2026-11-05-Adhesive-Investigation/run-probe.py old --tag rerun-old-1
python3 Diagnostics/2026-11-05-Adhesive-Investigation/run-probe.py new --tag rerun-new-1
python3 Diagnostics/2026-11-05-Adhesive-Investigation/native-runtime-control.py rerun-native-vc-1
python3 Diagnostics/2026-11-05-Adhesive-Investigation/native-runtime-control.py rerun-native-ucrt-1 --ucrt
python3 Diagnostics/2026-11-05-Adhesive-Investigation/verify-local-signatures.py
```

استدعِ native-runtime-control للتجارب الأصلية؛ تشغيل flag native في run-probe وحده لا يجهز ملفات Microsoft. يتحقق wrapper من بصمات مصادر Microsoft قبل النسخ، وينسخ أقل من 1.8 MB مع UCRT، ويحفظ الملفات الأصلية ويستعيدها. لا تعدل المسارات لتشير إلى prefix الرئيسي. بقيت الأدلة الكاملة محلية ولم تُرفع معلومات أو ملفات إلى GitHub.
