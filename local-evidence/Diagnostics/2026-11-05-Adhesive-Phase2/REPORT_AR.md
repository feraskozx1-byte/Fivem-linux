# المرحلة الثانية — Adhesive داخل المضيف الحقيقي

**النتيجة: أثبتنا نفس موضع الفشل المباشر داخل FiveM الحقيقي، ولم نجد بعد خلل Windows API عامًا يبرر patch في Wine. التحميل ما زال يفشل.** لم تُكرر التجارب الخمس السابقة، ولم يُعد بناء CoreRT أو العميل.

## Root Cause — ما ثبت وما لم يثبت

شُغّل `FiveM.exe` الحقيقي الموجود في نسختنا، مع CoreRT الجديد وAdhesive الرسمي، في تخطيط معزول وشبكة معطلة. سجل PID:TID `014c:0150` التسلسل التالي:

| الحدث | دليل fullhost-legacy-ui/wine.log |
| --- | --- |
| دخول Adhesive PROCESS_ATTACH، base=`0x6FFFF56E0000` | 19828 |
| أول استثناء في النطاق: قراءة `0xC0000005`، RIP=`0x6FFFF647FEC5` | 19877 |
| إزاحة التعليمة عن base | `0xD9FEC5` |
| عنوان القراءة | `0x20E6732`، السطر19879 |
| operands في سجل المعالج | `r9=0x1FB6720`، `rax=0x130012`، مجموعهما يطابق العنوان |
| عودة PROCESS_ATTACH صفرًا | 19909 |
| فشل تهيئة Adhesive | 19912 |
| سجل العميل، السطر3 | `Adhesive failed ... (error 998), falling back to sticky.` |

إطارات unwind العشرة تطابق الاختبار المستقل `new-builtin-1` واختبار v3 السابق، بما فيها سلسلة Adhesive `D9FEC5 → D9DE92 → D9DDC9 → D9DC96 → CC2457` ثم UCRT `_initterm+0x2A` وCRT الخاص بـAdhesive. CoreRT وlegitimacy وnet-tcp-server وnet وWINTRUST نجحت تهيئتها قبل ذلك. هذا يزيل فرضية أن العطل المرصود لا يظهر إلا لأن executable الاختبار صغير أو لأنه لم يشغّل ترتيب المكونات المعتاد.

هذا إثبات **نفس الفشل المباشر في تشغيل حقيقي جديد**، وليس كشفًا لأصل المؤشر. تشغيل العميل التاريخي لا يحتوي stack كافيًا، ولا نعيد كتابة تاريخه اعتمادًا على رمز998 وحده. لم نثبت أن كل العيوب المحتملة أو كل سياقات التشغيل متطابقة.

### ما أضافه تسجيل الذاكرة

في تشغيل مستقل للـhost مع `+virtual`، تكرر RVA نفسه، وعنوان القراءة أصبح `0x2046E02`. آخر dump للـview في PID نفسه يسجل الجزء `0x2030000–0x269FFFF` دون committed bit، بعد commit حتى `0x202FFFF`؛ العنوان يقع داخل الجزء المحجوز غير committed.

هذا **دليل داخلي من Wine على آخر حالة مسجلة**، وليس استدعاء VirtualQuery ولا دليل MEM_FREE. نتيجة MEM_FREE القديمة تخص الأداة المستقلة وحدها. تفسير حرف `c` في dump مستند إلى [مصدر Wine العام](https://github.com/wine-mirror/wine/blob/master/dlls/ntdll/unix/virtual.c)، ولا نفترض أن master مطابق تمامًا لكل patch في CachyOS. الأحداث والرموز الأصلية محفوظة في `memory-observation.json` و`memory-trace-excerpt.txt`.

محاولة أخذ `/proc/maps` التقطت أربع عمليات wrapper، لا عملية FiveM الفعلية. تم رفضها كدليل لحالة ذاكرة المضيف بعد مراجعة صورها المحملة. كذلك توقف pipe في تلك التجربة بعد info[1]؛ لا توجد فيها registers أو stack كاملة. دليل المكدس الكامل يأتي من التشغيل السابق، وليس من هذه التجربة. عُدّل runner اللاحق ليصرف بيانات pipe المتبقية بعد إيقاف العملية، وليرفض خرائط wrappers مستقبلًا.

### ما أضافه تسجيل الواجهات العامة

فُعّل Wine relay بقائمة `RelayFromInclude=adhesive.dll` مؤقتة في **prefix التشخيص فقط**. سجل Wine تحميل الفلتر، ثم سجل تهيئة المكتبة والاستثناء وعودة التهيئة صفرًا. تحت relay تتغير صيغة دخول DLL إلى `Call PE DLL`؛ أرقامها:32987، الاستثناء34299، return34342. parser أول نسخة من runner لم يتعرف هذه الصيغة، لذلك حقول base/return في summary لهذا التشغيل null؛ التحليل مستند إلى السجل الخام، وأُضيف دعم الصيغة لاحقًا دون إعادة التشغيل.

الدليل الأكثر تحديدًا:

- السطر34162: استدعاء `malloc(0xD8000)`؛34163 يعيد `0x1EF3820`.
- السطر34304: `r9=0x1EF3820`، مطابق رقميًا لذلك العنوان؛34303 يسجل `rax=0x130012`.
- عنوان القراءة `0x2023832` يساوي مجموعهما، ويتجاوز نهاية **حجم الطلب المرصود** `0x1FCB820` بمقدار `0x58012`.
- لم يُرصد free/realloc عام لذلك العنوان بين عودة malloc والفشل. هذا حد للرصد، لا إثبات كامل لعمر الكائن أو لمعنى البيانات.
- عمليات NT القريبة لفتح الملفات، الاستعلام عنها، التخصيص، القراءة، الإغلاق والتحرير تعيد STATUS_SUCCESS. لا نستنتج أن buffers أو byte counts أو كل semantics صحيحة لمجرد عودة صفر.
- لا تُفسر قيم retval لدوال void مثل free أو WakeAllConditionVariable على أنها حالات خطأ؛ قد يسجل relay بقايا register. وكذلك لا تُفسر البتات العليا المسجلة لمعاملات ULONG على أنها حجم64-bit صالح.

هذه قرينة محددة على قراءة تتجاوز طلب تخصيص مرصود داخل التهيئة الخاصة، لكنها لا تفسر كيف اشتُق index أو ما المدخل المتوقع. لا نجري تحليلًا لمنطق الحماية المغلق أو تغييرًا له. التفاصيل المنقحة في `api-observation.json` و`api-trace-excerpt.txt`.

## المرحلة1 — مراجعة الأدلة السابقة

قُرئت تقارير المرحلة الأولى ونتائجها ومقتطفاتها وتصنيف dumps؛ لم تُكرر تجاربها. بقيت الفجوة الأساسية ربط العطل بالمضيف الحقيقي. نتائج CRT السابقة لا تثبت صحة جميع APIs، والدُمبات العشرون لا تلتقط Adhesive mapped. حُفظت baseline جديدة قبل العمل، ثم تحققنا من بقاء المصدر والأدلة السابقة كما كانت.

أُضيف تصحيح تشخيصي مهم: `Run-CoreRT-Test/dbg/CoreRT.pdb` القديم GUID=`8B792D8E…` لا يطابق DLL الجديد GUID=`D93B51AE…`، age1. توجد نسخة PDB المطابقة في artifact CI42019993897؛ استُخدمت عبر رابط في dbg المعزول فقط. لم نستبدل PDB النسخة الناجحة. الدليل: `CoreRT-PDB-validation.txt`.

فحص المصدر والـdisassembly المحدود لدالة CoreRT المفتوحة `EarlyMode_Init` يدعم غياب استدعاء إخفاء Wine؛ matching PDB الجديد لا يحتوي رمز WineCompat_InstallHooks. لم يستعمل الاختبار DLL قديمًا يثبت هذا hook. الدليل: `CoreRT-EarlyMode-disassembly.txt`.

## المرحلة2 — التخطيط والاختبارات الجديدة

أنشأ `prepare-fullhost.py` مجلد `private/fullhost`:

- نُسخ exe الحقيقي وINI وcomponents.json وmarker الموجود `.formaldev`، وملفا إعداد صغيران للنسخ الاحتياطي/cache. الإجمالي المنسوخ عند الإعداد **5,134,565 بايت**.
- بقية DLLs وملفات .bin والمجلدات الثابتة روابط رمزية، مع grants read-only لمصادرها. ملف Adhesive يظل الملف الرسمي نفسه؛ لا hardlinks قابلة للكتابة.
- logs وcrashes وdata/cache محلية؛ ملفات cache الكبيرة روابط read-only، وgame_files.dat الصغير نسخة محلية قابلة للكتابة. لم تُنسخ profile/account directories.
- INI المحلي فقط أضيف له `DisableCrashUpload=1` بعد حفظ backup. `.formaldev` من التخطيط السابق، ومساره في المصدر يتجاوز updater؛ لم يتغير اختيار الحماية أو تحققها.
- prefix المستخدم هو prefix التشخيص السابق بلا حسابات. الشبكة معطلة بـ`--unshare=network`. لا مدخلات اتصال أو أوامر auth أو تغييرات tickets.

| الاختبار الجديد | الفرضية/الهدف | النتيجة |
| --- | --- | --- |
| fullhost-1 | تشغيل المضيف الحقيقي كما هو | توقف قبل Adhesive: XAML activation ثم fail-fast؛ ليس عطل Adhesive |
| fullhost-legacy-ui | إزالة عائق UI بالاختيار الموجود في FiveM | وصل إلى Adhesive؛ نفس RVA والمكدس ثم998 |
| fullhost-memory-trace | معرفة lifecycle الذاكرة في المضيف الحقيقي | نفس RVA و998؛ آخر view يسجل target في جزء محجوز غير committed |
| fullhost-public-api-1 | رصد API/allocator قبل الفشل | نفس RVA و998؛ malloc/base/index المذكورة أعلاه |

`CitizenFX_NoTenUI=1` خيار موجود في `UpdaterUI.cpp:1302–1326` لاختيار الواجهة القديمة. سبب استعماله أن `fullhost-1` سجل عدم توفر WindowsXamlManager ثم C++ exception وfail-fast قبل تحميل Adhesive. لم نوسع العمل إلى إصلاح XAML أو إعادة بناء launcher.

تتوقف أداة التشغيل بعد التقاط نتيجة Adhesive، مع مهلة45ثانية وسقف12MiB للسجل. الاختبارات التي وصلت للمكتبة استغرقت نحو3ثوانٍ إجمالًا مع UMU. سجلاتها نحو2.9MB و7.4MB و4.3MB؛ لا إعادة نسخ لمجلد5.5GB. خروج host=-15 في هذه التجارب نتيجة الإيقاف المقصود من runner بعد جمع الدليل، وليس كود انهيار Adhesive. قد يتقدم startup الأصلي لبضعة milliseconds قبل الإشارة؛ سجل أحد الاختبارات بدء subprocess بعد998، دون شبكة أو حسابات أو اختبار مصادقة.

## Fixes — المرحلة3

لم يثبت اختلاف سلوك Windows API محددة عن Windows، ولا توجد بيئة Windows مرجعية متاحة في الأدوات الحالية. لذلك لم ننشئ محاكاة Windows ولم نكتب patch تخمينيًا في Wine أو نعيد بناءه. عدم وجود trap غير منفذ قرب الفشل لا يثبت صحة النتائج بالكامل.

الإصلاحات العملية في **أدوات التشخيص فقط**: استعمال PDB المطابق، اختيار UI الموجود، ربط التحليل بـPID/TID، فصل فشل UI عن Adhesive، إضافة تسجيل الذاكرة وAPI العام، تحسين حفظ pipe ودعم صيغة relay. DLLs والمصدر السابق لم يتغيرا.

اختلاف PE versions (`Adhesive1.0.0.24769` مقابل local1.0.0.1) ليس برهان ABI mismatch: `code/tools/gen_rc.py:9,18–19` يستخدم CI_PIPELINE_ID مع default1. توافق المكونات المفتوح يُقرأ من FXCOMPONENT manifests؛ لا توجد مصفوفة Adhesive ABI معتمدة محليًا. يلزم Cfx لتأكيد مجموعة binaries المناسبة، ولا نغير الأرقام لتجاوز checks.

## Evidence — الحفظ والتراجع

- `fullhost-comparison.json` و`fullhost-trace-excerpt.txt`: المقارنة الدقيقة مع المرحلة الأولى، بمواضع السطور ونطاق العملية.
- `memory-observation.json` و`memory-trace-excerpt.txt`: رصد الذاكرة وحدوده.
- `api-observation.json` و`api-trace-excerpt.txt`: حدود API والـallocator.
- `fullhost-layout.json`: كل ملف منسوخ أو مربوط، مصادره وبصمات الملفات المناسبة.
- `sandbox-verification.json`: مصادر binaries وcache وGTAV mounted read-only. بعد إلغاء grant المسار الرئيسي يظهر ملف shadow آخر من persistent home في Flatpak بنفس الاسم؛ فحص device/inode يثبت أنه ليس ملف prefix الرئيسي الحقيقي. لا نعتمد على exists وحده لإثبات العزل.
- `preservation-check.json`: ملفات baseline، Git status/diff، وأدلة المرحلة الأولى كلها محفوظة كما كانت.
- `private/registry-backup-fullhost-public-api-1/`: backup user.reg قبل الفلتر وإثبات استعادته byte-for-byte. المحاولة التحضيرية الأولى رفضت Debug key الموجود قبل أي كتابة أو تشغيل؛ عُدل wrapper ليتعامل مع defaults بعد فحصها.

كل ملفات العمل الجديدة داخل Phase2. لا تغيير منتج يحتاج التراجع. نسخة INI قبل التعديل داخل private/fullhost؛ يمكن إبقاء التخطيط والأدلة أو إزالة مجلد Phase2 لاحقًا دون لمس المصادر. إذا قُطع تشغيل API trace مستقبلًا بانقطاع طاقة/SIGKILL قبل finally، وبعد التأكد من توقف prefix التشخيص، استعد **user.reg التشخيص فقط** من نسخة registry-backup الموافقة. لا تستعده إلى prefix الرئيسي.

## Remaining Blockers — المرحلة4

يلزم Cfx.re لتحديد initializer الخاص بهذه البصمة، وتفسير مصدر buffer/index، وتأكيد متطلبات host/component ABI والمدخل المتوقع. المطلوب diagnostic build أو symbols/logging محدود يوضح الأطوال وأصل البيانات دون أسرار. إذا ظهر خلل عام محدد في API، يمكن إنشاء reproducer مستقل ومقارنته بـWindows أو مواصفاتها ثم إصلاح Wine المحدود. لا يوجد الآن دليل كافٍ لهذا patch.

أُعد `CFX_REPORT.md` جديد يتضمن الدليل داخل المضيف الحقيقي، والاستثناء وحدود الذاكرة وAPI والـreproducer. **لم يُرسل أو يرفع** شيء. لم تُعدل مكتبة الحماية، ولم تُخف Wine، ولم يُغير fallback أو Sticky أو tickets أو شروط فحص الحماية. التهيئة لم تكتمل، وبالتالي وظائف الحماية غير مثبتة.

## أوامر إعادة الاختبار

التخطيط موجود؛ لا تعِد مرحلة الإعداد أو تجارب CRT السابقة. استعمل tag جديدًا وشغّل اختبارات prefix التشخيص بالتسلسل فقط:

```bash
cd /home/feras/Projects/FiveM-PR4050-Test
python3 Diagnostics/2026-11-05-Adhesive-Phase2/run-fullhost.py --tag verify-host-1 --legacy-ui
# اختياري فقط لتكرار دليل lifecycle الذاكرة:
python3 Diagnostics/2026-11-05-Adhesive-Phase2/run-fullhost.py --tag verify-memory-1 --legacy-ui --virtual-trace
# اختياري فقط لتكرار دليل API العام؛ wrapper يحفظ الفلتر ويستعيده:
python3 Diagnostics/2026-11-05-Adhesive-Phase2/run-api-trace.py verify-api-1
```

تعاد النتيجة من DLL trace وسجل العميل، لا من exit code الخاص بالـrunner. لا يُعد تحميل Sticky أو بدء subprocess نجاحًا لـAdhesive. إعادة الإعداد ليست مطلوبة إلا إذا أردت تخطيطًا جديدًا بعد مراجعة المسارات؛ السكربت يرفض استبدال التخطيط الموجود.
