# التجربة المباشرة: تعديل CoreRT وبناؤه وتشغيل Adhesive

**نُفذ تعديل محدود في نسخة مصدر معزولة، وبُني CoreRT جديد، واختُبر داخل FiveM الحقيقي مع Adhesive الرسمي. بقي الفشل عند RVA نفسه، ثم أُعيدت روابط التشغيل السابقة. لا يوجد إصلاح تشغيل ناجح حتى الآن.**

## 1. التعديل المنفذ

الملف: `source/DllGameComponent.Win32.cpp`، والمراجعة الدقيقة في `experiment-only.patch`.

الفرضية: طبقة `HardErrorScope` المفتوحة تضيف hooks تشخيصية إلى `RtlRaiseException` و`ZwQueryDebugFilterState` قبل تحميل المكونات. النسخة التجريبية لا تثبت هذه hooks على Wine، وتترك وظائف NTDLL الأصلية وسلوكها ظاهرين. مسار Windows بقي كما كان. لم تتغير مكتبة الحماية أو factory أو اختيار المكونات أو fallback أو نتيجة أي فحص أمني.

هذه فرضية تدخل المحمّل، وليست سببًا مثبتًا؛ الاختبار المستقل السابق كان يفشل أيضًا دون HardErrorScope، ولذلك كان احتمال النتيجة السلبية قائمًا. لم نسمِّ التعديل إصلاحًا ناجحًا قبل اختباره.

لم نغير SEH الخاص بالصورة المحملة يدويًا. تهيئة MinHook العامة ما زالت قائمة في `SEHTableHandler.Win32.cpp` عبر InitMHWrapper، ولم نعتمد على HardErrorScope لتهيئتها. كذلك راجعنا ReadManifest: يحتوي أصلًا على FreeLibrary، فلم ننشئ patch لتسرب مفترض غير موجود.

المصدر الأصلي لم يُعدل في مكانه؛ نُسخته السابقة محفوظة في `DllGameComponent.before.bak`. `build.patch` يجمع التعديلات الأربع السابقة مع التجربة، مقابل commit المثبت ba07d9d. جرى apply-check ومقارنة البايتات في شجرة مؤقتة صغيرة.

## 2. البناء الفعلي

- الفرع المنفصل: `codex/adhesive-loader-diag-20261105`؛ لا merge إلى الفرع الأساسي.
- commit وصفة البناء: `c93deb2e9ad6d59526648705b0ddcf4592e66093`.
- [CI ناجح42079514558](https://github.com/feraskozx1-byte/fivem-pr4050-build/actions/runs/42079514558).
- الهدف CitiCore واعتمادياته الثمانية فقط، دون CEF أو Node أو launcher أو بقية FiveM. أُعيد استخدام وصفة البناء المستهدف السابقة.
- اجتاز DLL/PDB validation واختبار تحميل CoreRT الطبيعي على Windows. هذا ليس اختبار Adhesive على Windows.
- SHA256 للـCoreRT التجريبي: `33767cc534ce6bf06f8ae54d8b539c46eefd0f07c4d63863ac04cf61825e51cf`.
- تطابق source hash للملف المعدل مع الملف الذي دخل البناء مثبت في `artifact/validation.json`؛ PDB GUID/age مطابقان. معلومات البناء محفوظة في `build-result.json`.

المرفوع إلى مستودع البناء كان recipe/patch المصدر العام فقط؛ لم تُرفع Adhesive أو السجلات الخاصة أو prefix أو بيانات حسابات.

## 3. اختبار FiveM الحقيقي والنتيجة

استُخدم تخطيط Phase2 التشخيصي الموجود، دون نسخ مجلد التشغيل. بدّل `test-core-artifact.py` رابطَي CoreRT وPDB داخل **مجلد التشخيص فقط**، ثم أعادهما في finally. مصادر التشغيل والـartifact mounted read-only، والشبكة معطلة، والتشغيل يوقف بعد نتيجة تحميل Adhesive.

| القياس | CoreRT السابق | CoreRT التجريبي |
| --- | --- | --- |
| تشغيل المسار المعدل | غير موجود | مثبت برسالتي trace، قبل legitimacy وAdhesive |
| Adhesive SHA256 | `3ba9e52b…58556b` | نفسه دون تعديل |
| PROCESS_ATTACH | فشل | فشل، return0 |
| أول AV داخل تهيئة Adhesive | `+0xD9FEC5` | `+0xD9FEC5` |
| رسالة العميل | 998 ثم fallback الموجود | 998 ثم fallback الموجود |
| عدد بايتات قراءة ntdll | 1,296,644 | نفسه |
| عدد بايتات قراءة win32u | 393,400 | نفسه |

الدليل: `comparison.json`، وملفا `*-exception-excerpt.txt`، و`private/fullhost-core-experiment/summary.json`. وجود نسخة DLL جديدة وحده لم يُعتمد؛ السجل يثبت تنفيذ constructor المعدل. ظهرت رسائل DBG_PRINT التشخيصية المتوقعة بعد ترك الوظائف الأصلية، ولم يُرصد عطل fatal جديد قبل AV نفسه. هذا لا يختبر المراحل التي لم يصل إليها العميل.

**الاستنتاج:** تجاوز تدخل HardErrorScope التشخيصي لا يحل فشل التهيئة المرصود. لم نعتمد هذا الـDLL كإصدار تشغيل. استعادة الرابطين والبصمات مثبتة في `artifact-link-restoration.json`؛ CoreRT المعاد اختياره يعود للبصمة السابقة `cd9f91d5…b4d64`.

## 4. الانتقال إلى فرضية أخرى: I/O الفعلي قبل الانهيار

بدل تكرار تجربة الخطأ فقط، أضاف runner قناة Wine `+file`. هذه القناة تسجل أسماء الملفات وعداد NtReadFile الفعلي، وهي معلومات لم تكن في relay السابق:

| الملف الفعلي في prefix | طلب القراءة | NtReadFile الفعلي | EndOfFile في الاختبار المحدد | AllocationSize |
| --- | ---: | ---: | ---: | ---: |
| ntdll.dll | `0x13D000` | `0x13C904` | `0x13C904` | `0x13D000` |
| win32u.dll | `0x61000` | `0x600B8` | `0x600B8` | `0x61000` |

`file-origin-excerpt.txt` يسجل الفتح والقراءة داخل PROCESS_ATTACH في PID/TID المحدد؛ نفس النتائج تظهر مع CoreRT التجريبي. مسار pfx في سجل Proton هو symlink إلى prefix التشخيص نفسه، وليس prefix مختلفًا.

بُني **file-probe.exe** جديد من `file-probe.c`، مقتصر على الملفين الحقيقيين، وبمعاملات NtOpenFile المرصودة: access0x100001، share7، options0x24، OBJ_CASE_INSENSITIVE، ثم FileStandardInformation24بايت، وNtReadFile بالطلب المرصود وoffset=NULL. لا يحمل هذا البرنامج FiveM أو Adhesive.

النتيجة: **15 تحققًا ناجحًا، صفر فشل** عبر UMU/Proton. عدد البايتات يطابق EOF والعدد المسجل داخل FiveM، وبصمتا FNV1a64 للبايتات المقروءة تطابقان الملفات الأصلية. FNV هنا fingerprint للمقارنة وليس تحققًا تشفيريًا؛ SHA256 للملفين محفوظ أيضًا. الذيل غير المقروء لم يكتب عليه NtReadFile، وفق canary الخاص بالاختبار. انظر `observed-file-io-validation.json` و`private/observed-file-io/results.txt`.

**الاستنتاج:** لا يظهر خطأ count/size أو اختلاف بيانات في إعادة تشغيل عمليتي I/O على الملفين الفعليين. هذا لا يكشف معنى buffer الخاص ولا يفترض أن ترتيب القراءة وحده يثبت مصدر r9. فُك جزء من العائق السابق: لم نعد نحتاج Cfx لمعرفة اسمي الملفين أو العدد الفعلي لهذه القراءات.

## 5. فرضية بنية PE للمدخلين

بعد استبعاد تدخل التشخيص وقياس I/O، فحص `check-system-pe.py` المدخلين نفسيهما دون تشغيلهما أو تعديلهما: AMD64/PE32+، حدود sections داخل الملف والصورة، جداول export، حدود ordinal indexes16-bit، أسماء ASCII المنتهية والمرتبة، RVAs والـforwarders. لم يفسر أي تعليمات في Adhesive.

اجتاز الملفان الفحوص المنفذة:1468 export مسمى في ntdll و1540 في win32u. `system-pe-validation.json` يحتوي النتائج وحدودها؛ هذا ليس تصديقًا لكل حقول PE أو لتوافق التهيئة الخاصة مع كل بنية نظام. مرجع الصيغة: [Microsoft PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format).

## 6. المعلومة التي بقيت ناقصة

البيانات العامة التي قسناها لم تكشف مخالفة يمكن تصحيحها في Wine. المتبقي المحدد هو **عقد buffer/index داخل initializer عند D9FEC5**: ما المدخل/الجدول الذي ينبغي أن ينتج ذلك index، وما الطول المقبول له بالنسبة إلى البيانات المأخوذة من ntdll/win32u؟ نحتاج Cfx لتسمية هذا العقد أو توفير diagnostic build يخرج الأطوال وهوية المدخل دون أسرار، وتأكيد مجموعة host/component ABI المناسبة للبصمة الرسمية.

إصلاح ذلك من خارج المكتبة لا يمكن اشتقاقه من STATUS_SUCCESS أو من أرقام الإصدارات وحدها. لم ننشئ تعديل Wine تخمينيًا، ولم نغير حدود تخصيص العملية أو نتجاهل AV.

## إعادة الاختبار والتراجع

```bash
# الاختبار المحدد للملفين؛ يحتاج tag جديدًا:
bash Diagnostics/2026-11-05-Adhesive-Direct-Repair/build-file-probe.sh
python3 Diagnostics/2026-11-05-Adhesive-Direct-Repair/run-file-probe.py --tag repeat-observed-file-io
python3 Diagnostics/2026-11-05-Adhesive-Direct-Repair/check-system-pe.py
```

إعادة اختبار الـartifact تتطلب حفظ run السابق وملف artifact-link-backup.json باسم أرشيف جديد أولًا؛ السكربت يرفض الكتابة فوق الأدلة. ثم `python3 .../test-core-artifact.py` يبدل الروابط ويستعيدها تلقائيًا. تفاصيل استعادة الرابط الأصلي محفوظة في artifact-link-backup.json إذا قُطع تشغيل مستقبلي بـSIGKILL أو انقطاع طاقة. لا يُشغّل هذا بالتوازي مع اختبارات prefix نفسه.

لا يحتاج التشغيل الحالي إلى تراجع إضافي: الروابط أعيدت والمصدر الأصلي وملفات التشغيل الناجحة بقيت كما كانت. التعديل التجريبي محفوظ للمراجعة ولا يُقدم كحل لـAdhesive.
