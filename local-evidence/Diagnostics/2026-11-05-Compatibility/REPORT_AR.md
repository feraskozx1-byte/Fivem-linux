# تقرير التوافق والاستقرار — 5 نوفمبر 2026

أُصلح مصدر CoreRT وSEH، واجتازت التعديلات اختبارات C++ معزولة تحت AddressSanitizer وUBSan، واختُبرت استراتيجية SEH فعلياً عبر UMU وProton-CachyOS في برنامج مستقل. جرى أيضاً تضييق خطأ Adhesive إلى استثناء داخل تهيئته في تجربة معزولة. لم يُبنَ CoreRT.dll جديد ولم تُستبدل ثنائيات التشغيل؛ لذلك لا يوجد بعد إثبات تشغيل الإصلاح داخل FiveM أو نجاح اتصال بخادم محمي. لم تتغير الحسابات أو إعدادات Heroic أو بيانات اللعبة أو prefixes السابقة. [تفاصيل التجارب الفعلية](EXPERIMENTS_AR.md).

## 1. انهيار CoreRT عند ‎+0x1B6DF

**السبب المثبت:** فرع `HardErrorScope` يفترض تخطيطاً داخلياً لـWindows عند `_fltused - 16`. تفكيك CoreRT الموجود يبين التعليمة `orl $0x2,-0x10(%rax)` عند RVA `0x1B6DF`. يسجل `corert-crash-debug.log` استثناء كتابة `c0000005` إلى نفس العنوان النسبي. سبقت الكتابة مقارنة رقم build فقط، دون استثناء Wine.

**الملفات المفحوصة:** `code/client/citicore/DllGameComponent.Win32.cpp`، `LaunchMode.h`، `corert-crash-debug.log`، نسخ CoreRT في Compiled-Release وRun-Test وRun-Adhesive-Test وملف `Run-Test/dbg/CoreRT.pdb`. GUID وAge في PDB يطابقان CodeView داخل DLL. SHA256 للنسخ الثلاث متطابق: `b38ab16c25c9bf72b537e9e1acfef5411a0939d6289c953f28b4ac2358fc8013`.

**الإصلاح:** إضافة `&& !CfxIsWine()` إلى شرط نطاق builds 18362..19627. لا يجري تغيير رقم إصدار Windows. يبقى `m_oldLdrFlags` غير مملوء عند تجاوز الفرع، فيتجاوز destructor كتابة الاستعادة أيضاً. حُفظ CRLF والنسخة السابقة في `DllGameComponent.Win32.cpp.before.bak`.

**التحقق:** `validate_corert.py` يستخرج فئة الإنتاج نفسها ويجرب 18 حالة: Wine وWindows، حدود builds، وقيم أعلام تبدأ بصفر وبقيمة غير صفرية. على Wine تستخدم التجربة صفحة ذاكرة ممنوعة الوصول وتتحقق من عدم محاولة حل `_fltused` أصلاً؛ على Windows المحاكى تتحقق من تفعيل العلم ثم استعادته. نجحت الاختبارات مع ASan/UBSan. المصدر السابق يفشل بنفس الاختبار بوصول ذاكرة غير صالح، كما هو متوقع. هذه محاكاة Win32 وMinHook، وليست بناء DLL.

**العائق والبناء:** النسخ الحالية لا تتضمن الإصلاح. يلزم بناء هدف `CitiCore` واعتمادياته ثم اختبار DLL الناتج في نسخة تشغيل منفصلة. [workflow الحالي](https://github.com/feraskozx1-byte/fivem-pr4050-build/blob/main/.github/workflows/build.yml) يحتوي شرط CoreRT، لكن فحص الثنائي يثبت أنه غير موجود في النسخ المحلية. لم يُشغّل workflow أو يُرفع تعديل.

## 2. SEH وغياب Rtlp/RtlpxLookupFunctionTable

**السبب المثبت:** التعديل المحلي السابق أضاف استثناء Wine إلى شرط رسالة FatalError فقط؛ ظل يبحث في تعليمات ntdll عن دالة داخلية خاصة بـWindows، وقد يختار دالة ذات توقيع مختلف. كذلك ظل ينفذ استعلام الذاكرة الخاص بمسار Windows قبل تحديد مسار Wine. هذه مشكلة افتراض ABI وتخطيط، وليست مجرد غياب اسم export يجب إضافته عشوائياً.

**الملفات المفحوصة:** `SEHTableHandler.Win32.cpp`، نسخته الاحتياطية السابقة، `seh-wine-fix.patch`، `ExecutableLoader.cpp:240` وما بعده، `LaunchMode.h`، ومكتبة ntdll الفعلية لنسخة Proton-CachyOS. التفاصيل في [seh-analysis.md](seh-analysis.md) و[runtime-ntdll-analysis.md](runtime-ntdll-analysis.md).

**دليل runtime الفعلي:** الدالة `RtlLookupFunctionEntry` في ntdll المحلية تدمج منطق البحث، فلا تستدعي export `RtlLookupFunctionTable`. كلتاهما تستدعي `RtlImageDirectoryEntryToData`. لذلك اختيار اعتراض export البحث وحده غير كافٍ لهذه النسخة. هذه نتيجة تفكيك المكتبة الفعلية، لا افتراض من مصدر Wine العام وحده.

**الإصلاح النهائي:** فرع مبكر صريح لـWine يعترض `RtlImageDirectoryEntryToData` باستخدام stub الموجود، ويعيد جدول الاستثناء الصحيح فقط للموديول المحدد عند طلب `IMAGE_DIRECTORY_ENTRY_EXCEPTION` كصورة محملة. تمر بقية الطلبات إلى الدالة الأصلية. يُفحص نجاح العثور على export وإنشاء وتفعيل خطاف MinHook، ويُفعّل هذا الهدف فقط. يتجاوز الفرع فحص تعليمات Windows واستعلام الذاكرة الخاص به. صُحح الحد الأعلى للعناوين إلى نهاية غير شاملة وفق `base + SizeOfImage` الذي يمرره المستدعي. كما أضيف توقف عند إرجاع `ud_disassemble` صفراً لمنع استمرار الحلقة بعد نهاية فك التعليمات. لم تتغير حماية الاستثناءات أو مصادقة السيرفر.

**التحقق:** `validate-seh.py`: 18 توليفة للموديول ودليل PE وطريقة العرض، وتمرير الوسائط، وحجم الجدول بالبايت، وحدود العناوين، وفشل export وإنشاء وتفعيل الخطاف، ومسار Windows. `validate-seh-scanner.py`: التوقف عند نهاية decoder مع اختبار يثبت فشل المصدر السابق. نجحت تحت ASan/UBSan. الـdecoder وWin32 وMinHook محاكاة؛ لا تثبت هذه الاختبارات فك stack فعلياً داخل Proton. حافظ الملف على CRLF.

**اختبار حي إضافي:** برنامج مستقل اعترض directory helper داخل ذاكرته فقط، فأعادت دوال lookup الفعلية جدولاً منسوخاً مختلف العنوان، ومرت الطلبات الأخرى بالنتائج الأصلية، ثم استُعيدت تعليمات ntdll وحمايتها وتحقق الرجوع للجدول الأصلي. نجح الاختبار برمز 0. هذا يختبر استراتيجية التكامل، وليس MinHook أو DLL الجديد أو فك stack؛ [النتائج](EXPERIMENTS_AR.md).

**العائق والبناء:** يلزم `CitiCore` فقط مع اعتمادياته. ما زال تفعيل MinHook وفك الاستثناءات في DLL المبني بحاجة إلى تجربة فعلية. شرط EOF لا يحل جميع مخاطر البحث في تعليمات غير محدودة؛ لم نغير حدود البحث الخاصة بمسار Windows دون اختبار decoder فعلي. النسخة السابقة مع التعديل المحلي محفوظة في `SEHTableHandler.Win32.cpp.pre-session.bak`.

## 3. Adhesive وخطأ 998

**المثبت من السجلات:** `LoadLibrary` يفشل فعلاً بالرمز 998 ثم ينفذ المصدر السابق fallback إلى Sticky. نسخة Run-Adhesive-Test تطابق المرجع الرسمي SHA256 `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`. [Microsoft](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--500-999-) تعرف 998 بأنه `ERROR_NOACCESS`؛ هذا لا يحدد التعليمة المسببة أو نية DLL.

**الملفات والفحوص:** DLL الرسمي والتجريبي، PE metadata، `DllGameComponent.Win32.cpp`، سجلات CitizenFX التجريبية و`adhesive-wine-debug.log` وسجلات Heroic. سبعة أقسام PE ضمن حدود الملف، وexport `CreateComponent` وTLS وثلاثة callbacks وrelocations وexception metadata. فحص الاستيرادات السابق «0 وظائف مفقودة عبر 25 DLL» لم يُكرر. السجل المسمى wine-debug لا يحتوي تتبع loader/SEH الفعلي؛ لا يجوز استنتاج stack منه. [التفاصيل](adhesive-auth-analysis.md).

**الإصلاح:** لا تعديل داخل DLL أو حماية، ولا دليل يبرر ذلك. لم يُنسب الخطأ إلى kernel driver أو import مفقود أو رفض متعمد؛ هذه تفسيرات غير مثبتة.

**التجربة الجديدة:** التحميل المباشر دون CoreRT كشف أولاً خطأ تهيئة dependency بسبب غياب registry المضيف؛ بعد تحميل CoreRT صراحة نجح تحضيره بلا استثناءات، ووصلت التجربة إلى خطأ قراءة داخل `adhesive.dll+0xD9FEC5` للعنوان `0xA5D36A`، أثناء CRT static initialization عبر `_initterm`. أعاد loader الرمز 998. لم تُستدعَ وظائف إخفاء Wine أو مصانع المكونات أو أي اتصال شبكي. [التفاصيل والحدود](EXPERIMENTS_AR.md).

**العائق والبناء:** موضع الاستثناء مثبت في هذه التجربة المعزولة؛ سبب القراءة غير الصالحة وتطابقه مع عطل FiveM الأصلي لم يثبتا. CoreRT الجديد لا يعيد بناء Adhesive المغلق ولا يضمن تشغيله. لا يبرر هذا الدليل patch للحماية. يلزم السياق الكامل المصرح به أو تشخيص Cfx للحسم.

## 4. No authentication ticket was specified

**السبب المباشر المثبت:** `code/components/citizen-server-impl/src/InitConnectMethod.cpp:641` يرفض غياب حقل `cfxTicket2`. تذكرة Steam `authTicket` منفصلة. `NetLibrary.cpp:1866` وما بعده يتيح لمكون المصادقة إضافة حقول الاتصال؛ منتج تذكرة Cfx الفعلي غير متاح في المصدر المفتوح المحلي.

**الملفات والفحوص:** مصدر رفض الاتصال ومصدر NetLibrary وسجلات ربط الحساب ورفض السيرفر ومسار تحميل Adhesive/Sticky. الربط بالحساب لا يثبت إصدار تذكرة اتصال. فشل الحماية ومسار fallback يدعمان وجود عائق في مكونات الأمان، لكن لا يثبتان أن Adhesive وحده هو السبب الحصري. [التفاصيل](adhesive-auth-analysis.md).

**الإصلاح والعائق والبناء:** لا تزوير أو نسخ تذكرة ولا تعطيل للتحقق. إعادة بناء CoreRT لا تضمن حل التذكرة. أُعيد التحقق من [تعليق Cfx الرسمي](https://github.com/citizenfx/fivem/pull/4050#discussion_r4289067271): لا يعتزم الفريق حالياً السماح باتصالات Linux إلى السيرفرات المحمية. هذه حقيقة دعم مستقلة عن السبب الداخلي الدقيق للخطأ 998؛ يلزم دعم واختبار مكونات الأمان الأصلية من الجهة المالكة.

## 5. Rockstar HTTP 403 DoesNotExist وتكامل Heroic

**المثبت:** السجل `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T202008.log` يختار Epic ويجد Launcher ويسجل حالة دخول، ثم `/ros/validate` يرجع 403 و`DoesNotExist`. لذلك لم يثبت أن Launcher مفقود أو الحساب غير مسجل أو TLS معطّل. سجل Run-Test عند T164029 يتقدم إلى `INIT_CORE` بعد 403؛ لا يثبت هذا الخطأ وحده توقف التهيئة.

**الملفات والفحوص:** سجلات CitizenFX وRockstar، مكونات legitimacy ومنافيستاتها، إعدادات الملف الثاني لـHeroic عبر حقول مسموحة فقط، وmetadata لعبة Epic. تنفيذ ROS هنا DLL مغلق. إعداد GTA الأصلي يستخدم CachyOS وUMU؛ إعداد FiveM الحالي يشير إلى Run-Adhesive-Test ويستخدم prefix عمل منفصلاً. متغير تكامل Epic موثق في [Heroic](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/Rockstar-Games-from-Epic-Games)، ولا يثبت قبول حماية FiveM. [التفاصيل](launcher-network-analysis.md).

**الإصلاح والاختبار والعائق:** لم تُنقل جلسات ولم تتغير إعدادات الحساب أو TLS. السبب الخلفي الدقيق لـ403 غير مثبت؛ قدم إصدار ROS التوافقي احتمال يستحق التحقق وليس سبباً مؤكداً. يتطلب الحسم سجل طلب عادي حديث يحدد العملية الرافضة دون كشف بيانات الجلسة. لا إعادة بناء مبررة لهذا الخطأ من الأدلة الحالية.

## 6. الخادم يطلب build 3889 والعملية تعمل على 3258

**السبب المثبت:** `code/premake5_builds.lua` لا يتضمن 3889؛ أقصى build محلي 3788. `CrossBuildRuntime.h:238` يولد قائمة الدعم، و`NetLibrary.cpp:1813` يرفض 3889 قبل التبديل. تثبيت GTA 3889 لا يضيف دعمه إلى هذا العميل.

**الملفات والاختبار:** القائمة ومصدر فحصها، `CrossBuildLaunch.cpp` و`XBRInit.cpp` وملفا CitizenFX.ini وسجلات رفض 3889. تحقق استخراج القائمة: 3258 موجود و3889 غائب. Run-Test يحدد 3258؛ Run-Adhesive-Test يحدد DefaultBuild=3889 مع SavedBuildNumber=3258. تغيير المفتاح لا يوفر hooks/cache ودعم build الغائب.

**الإصلاح والعائق والبناء:** لم تُعدل الإعدادات المحفوظة ولم تُضف 3889 شكلياً إلى القائمة. الحل يحتاج مصدر عميل يدعم هذا الإصدار فعلياً وبناء مكوناته واختبارها؛ بناء CoreRT وحده لا يكفي. اختيار خادم بإصدار مدعوم يعزل هذه المشكلة فقط، ولا يحل تذاكر الاتصال.

## 7. CURL 52 و56

**المثبت:** سجل Run-Test عند T164029 يسجل رداً HTTP فارغاً أثناء handshake، وعند T182632 يسجل فشل استقبال/connection reset أثناء جلب متغيرات السيرفر. [libcurl](https://curl.se/libcurl/c/libcurl-errors.html) يميز 52 «لا رد» عن 56 «فشل استقبال بيانات».

**الملفات والاختبار:** سجلا CitizenFX المذكوران ومرجع libcurl الرسمي. هذه أدلة نقل فعلية، لكنها لا تحدد هل المصدر الخادم أو وسيط الشبكة أو runtime؛ لا تثبت وحدها رفض مصادقة أو فشل TLS. لم يُكرر اتصال قديم وكأنه يعيد ظروف العطل نفسه.

**الإصلاح والعائق والبناء:** لا تغيير للشبكة أو تعطيل TLS مبرر. يلزم قياس محدود متزامن من العميل والخادم عند إعادة إنتاج الخطأ. لا إعادة بناء مبررة حالياً.

## البناء الأدنى وكيفية نقل الإصلاح

الهدف المحدد في `code/client/citicore/premake5.lua` هو **CitiCore** وينتج **CoreRT.dll**؛ كلا الملفين المعدلين جزء منه. لا حاجة لبناء GTA أو العميل كله لغرض هذين الإصلاحين. يلزم Windows مع Visual Studio 2022 C++ وMSBuild وWindows SDK، واعتماديات المصدر المطابق: Shared وBoost وTBB وMinHook وudis86 والملفات المولدة أثناء تجهيز المصدر. local checkout لا يحتوي solution أو ملفات objects، ومعظم submodules غير مهيأة؛ لا يكفي ربط ملف object بالـrelease الموجود.

بعد تجهيز المصدر المطابق وCEF/prebuild وتوليد solution بواسطة `pwsh ./fxd.ps1 gen -game five`، الأمر المحدد من موجه Visual Studio هو:

```powershell
msbuild code\build\five\CitizenMP.sln /t:CitiCore /restore /p:RestorePackagesConfig=true /p:Configuration=Release /p:WindowsTargetPlatformVersion=10.0.22621.0 /m:4
```

هذا أمر مقترح مبني على تعريف المشروع وworkflow الحالي؛ **لم يُنفذ**. يحدد مشروع CitiCore معمارية x64 عبر إعدادات المصدر. الأمر يترك تعيين platform للـsolution المولد كما يفعل workflow الحالي. يستلزم التجهيز أدوات Python ومولدات المشروع واعتمادياته؛ قد يكون التجهيز الأول طويلاً رغم اقتصار هدف البناء.

workflow البعيد يستنسخ commit `ba07d9d` ويطبق شرط CoreRT فقط؛ لن يشمل تعديل SEH المحلي تلقائياً. Patch SEH المنفصل في هذا المجلد قابل للتطبيق بعد checkout وقبل البناء مع إبقاء خطوة CoreRT الحالية. لم يُعدل workflow ولم يُرفع شيء إلى GitHub. التعديلات السابقة التي تخفي Wine عن مكونات الحماية وتستبدل Adhesive موجودة في أصل PR؛ إصلاحات هذه الجلسة لا تضيفها ولا تعتمد على استخدامها لإثبات الحماية. لا يشكل بناء الفرع نفسه إثباتاً لدعم السيرفرات المحمية.

## حدود التسليم

التعديلات الإنتاجية محصورة في ملفي C++ المذكورين. النسخ الاحتياطية القديمة محفوظة، وأضيفت نسخ ما قبل الجلسة وpatches وتقارير واختبارات داخل Diagnostics. لا يوجد بناء كامل أو استبدال DLL أو push أو تعديل لحساب Epic الأساسي. نتائج أدوات الاختبار المنفصلة، إن نُفذت، تسجل في ملف تجربة مستقل مع runtime والبيئة وحدود الاستنتاج.


آخر متابعة: أضيف تحقق DefaultBuild وأُلغي تفعيل إخفاء Wine في المصدر، ونجح فحص ترجمة SEH إلى Windows x64. لم يتوفر DLL جديد. النتائج المختصرة والمسار التنفيذي للبناء في [CONTINUATION_AR.md](CONTINUATION_AR.md).
