# تحقيق Rockstar وHeroic وإصدارات اللعبة والشبكة — 5 نوفمبر 2026

العمل قراءة فقط، عدا إنشاء هذا التقرير. لم تُشغّل تطبيقات ولم تتغير حسابات Heroic أو prefixes أو مجلدا التشغيل أو الثنائيات. البيانات هنا منقحة ولا تتضمن جلسات حسابات أو تذاكر أو cookies.

## إصدار اللعبة: السبب مثبت

- `Original-PR4050-Source/code/premake5_builds.lua:3` يحدد أحدث إصدار مدعوم محلياً: **3788**. قائمة GTA كاملة: 1، 1604، 2060، 2189، 2372، 2545، 2612، 2699، 2802، 2944، 3095، 3258، 3323، 3407، 3570، 3751، 3788. الإصدار **3889 غير موجود**.
- `code/client/shared/CrossBuildRuntime.h:238` ينشئ `IsSupportedGameBuild()` من القائمة؛ `code/components/net/src/NetLibrary.cpp:1813` يرفض الإصدار غير المدعوم قبل طلب التبديل.
- الدليل التشغيلي: `Run-Test/logs/CitizenFX_log_2026-11-04T164029.log:303` ورسائل متكررة: `Server specified an invalid game build enforcement (3889)`؛ أيضاً `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T192501.log:249`.
- إعداد `Run-Test/CitizenFX.ini`: `SavedBuildNumber=3258` و`DefaultBuild=3258`؛ إعداد `Run-Adhesive-Test/CitizenFX.ini`: `SavedBuildNumber=3258` لكن `DefaultBuild=3889`.
- `code/client/launcher/CrossBuildLaunch.cpp:73` يقرأ SavedBuildNumber، بينما `code/client/shared/XBRInit.cpp:85` يقبل أي DefaultBuild موجب دون التحقق من دعمه. لذلك تغيير المفتاح وحده لا يضيف دعم hooks أو game-cache للإصدار 3889. يوجد عدم اتساق مثبت في إعداد النسخة التجريبية، لكن لا يوجد إثبات أن انهياراً بعينه ناتج عنه.
- metadata الحالية لنسخة Epic GTA Legacy تبلغ عن `1.0.3889.0_v1`. إصدار اللعبة المثبت لا يحدد تلقائياً ما يدعمه عميل FiveM القديم.

**الاختبار:** استخراج قائمة الإصدارات من premake بواسطة Python، والتحقق أن 3258 موجود و3889 غائب: نجح. لم يتم تبديل إصدار أو تنزيل بيانات.

**الإصلاح/العائق:** لم تُضف 3889 إلى القائمة فقط؛ الدعم يحتاج تغييرات upstream الفعلية للعميل، وتوافق hooks/cache واختبارها. يحتاج العميل المبني من مصدر محدث إلى إعادة بناء؛ إعادة بناء CoreRT وحده لا تضيف هذا الدعم. اختيار سيرفر يتطلب إصداراً مدعوماً يعزل مشكلة الإصدار فقط ولا يصلح المصادقة أو الحماية. أي تجربة ضبط DefaultBuild تكون على نسخة إعداد جديدة منفصلة وبعد أخذ نسخة احتياطية؛ إعدادا التشغيل الحاليان بقيا كما هما.

## Rockstar HTTP 403 DoesNotExist: العرض مثبت، السبب التفصيلي غير محسوم

في `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T202008.log`:

| السطر | الحدث المنقح |
| --- | --- |
| 9 | اختيار مسار Epic |
| 14 | العثور على Rockstar Launcher |
| 17 | Launcher يبلغ عن جلسة مسجلة الدخول؛ حُذفت هوية الحساب من هذا التقرير |
| 19 | بدء `/ros/validate` |
| 22 | استجابة HTTP 403 ورسالة XML `DoesNotExist` |
| 35 | إصدارات طبقة Rockstar المضمنة: Launcher 1.0.53.576 وSocial Club 2.0.9.0 |

لا يثبت هذا أن Launcher مفقود، أو أن المستخدم لم يسجل الدخول، أو وجود عيب TLS، أو انعدام ملكية اللعبة. في سجل `Run-Test/...T164029.log:21` يظهر 403، ثم يكتمل `INIT_CORE` عند السطر 339؛ إذن هذا الخطأ لم يمنع دائماً التهيئة اللاحقة.

كود ROS الفعلي غير متاح هنا: `code/components/legitimacy/` يحتوي DLLs جاهزة في debug/release وmanifest، دون تنفيذ C++ لهذه العملية. strings الثنائيات توضح وجود `/ros/validate` المحلي ومسارات entitlement، لكنها لا تحدد أي طلب خلفي فشل أو لماذا. استخدام إصدارات Rockstar قديمة داخل طبقة التوافق يجعل تغير API احتمالاً، وليس سبباً مثبتاً.

**الإصلاح:** لا تعديل مصدر مبرر بهذا الدليل. لم يتم تجاوز validation أو نقل بيانات الجلسات. إعادة البناء غير مبررة لهذا الخطأ حالياً.

**الخطوة العادية التالية:** تجربة جديدة واحدة عبر مسار Heroic/UMU الحالي المخصص للنسخة التجريبية، ثم جمع سجل منقح بتوقيت واضح يحدد العملية الخلفية الفاشلة دون نشر بياناتها السرية. لا يبرر السجل تغيير الحساب الأساسي أو استبدال DLLs أو تعطيل TLS.

## إعداد Heroic الفعلي

جذر ملف Epic الثاني هو `/home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic`.

- إعداد GTA: `GamesConfig/9d2d0eb64d5c44529cece33fe2a46482.json`.
- prefix GTA: `/home/feras/Games/Heroic/Prefixes/Grand Theft Auto V`.
- runner: `tools/proton/Proton-CachyOS-latest/proton`؛ ملف version يقرأ `1792530497 cachyos-11.0-20261015-slr`.
- UMU غير معطل (`disableUMU=false`)؛ ملف التشغيل البديل `GTAV/fix.bat`، ومتغير `USE_FAKE_EPIC_EXE=true`.
- metadata اللعبة: `legendaryConfig/legendary/installed.json`؛ executable هو `PlayGTAV.exe` وإصدار التثبيت 1.0.3889.0_v1.
- إعداد FiveM الحالي: `GamesConfig/wC6nr6dqw6GVLd8H6ysDhV.json` يشير إلى `/home/feras/Projects/FiveM-PR4050-Test/Run-Adhesive-Test/FiveM.exe` ويستخدم `/home/feras/Games/FiveM-Official-Test/GTA-Prefix-Work` وrunner CachyOS نفسه، مع esync/fsync. يختلف executable الحالي عن الهدف الأقدم المسجل في التقرير السابق.

توثق [صفحة Heroic الرسمية لتشغيل ألعاب Rockstar المملوكة عبر Epic](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/Rockstar-Games-from-Epic-Games) متغير التكامل المذكور وwrapper التشغيل. هذا تكامل عادي بين Heroic وRockstar، ولا يثبت دعم حماية FiveM أو قبول السيرفرات.

سجل Launcher في prefix GTA الأصلي: `drive_c/users/steamuser/Documents/Rockstar Games/Launcher/launcher.log` يؤكد نسخة GTA 3889 عند السطرين 241 و244، وخروجين نظيفين للعبة عند 304 و346 بتاريخ 4 نوفمبر. هذا يثبت تقدماً سابقاً في تشغيل اللعبة عبر التكامل؛ لا يثبت الوصول للعب أو قبول سيرفر محمي. لم تتم إعادة التجربة أو تعديل هذا prefix.

**الاختبار:** قراءة حقول إعداد غير سرية بقائمة سماح، ومطابقتها مع تقرير HEROIC_AUDIT السابق. لم تُقرأ أو تُنسخ ملفات جلسات الحسابات لهذا التحقيق.

## CURL 52 و56

- `Run-Test/logs/CitizenFX_log_2026-11-04T164029.log:656`: رد HTTP فارغ أثناء handshake، CURL52.
- `Run-Test/logs/CitizenFX_log_2026-11-04T182632.log:356` بحسب rg: إعادة ضبط اتصال أثناء جلب server variables، CURL56. عدّ Python على فواصل LF أعطى السطر 357 بسبب محرف تحكم داخل سجل سابق؛ الرسالة ذاتها واحدة.

وفق [توثيق libcurl الرسمي](https://curl.se/libcurl/c/libcurl-errors.html)، 52 يعني عدم وصول رد و56 يعني فشل استقبال بيانات. لا يحدد الرمزان وحدهما سبباً في Wine أو الحماية أو TLS. يمكن أن يقع الخلل عند السيرفر أو وسيط الشبكة أو العميل؛ لا توجد حزمة شبكة أو سجلات سيرفر تفصل بينها هنا.

**الإصلاح/الاختبار/العائق:** مطابقة الرسائل الفعلية بتوثيق الأخطاء فقط؛ لا تعديل مصدر مبرر ولا حاجة لإعادة بناء مثبتة. الخطوة التالية عند تكرار العطل هي مقارنة طلب عادي إلى endpoint عام معروف ومسموح من البيئة نفسها وفي التوقيت نفسه، وسجل السيرفر إن توفر، مع الحفاظ على TLS والمصادقة. لا تُكرر محاولات دخول محمية بهدف تشخيص transport وحده.

## ملفات إضافية فُحصت

`Diagnostics/2026-11-04/RESULTS_AR.md`، `HEROIC_AUDIT.md`، `SOURCE_AUDIT.md`، `Diagnostics/Heroic-Recovery/PRIOR_BASELINE.md`، `code/client/shared/CrossBuildRuntime.h`، `XBRInit.cpp`، `code/client/launcher/CrossBuildLaunch.cpp`، و`code/components/legitimacy/{component.lua,component.json}`، إضافةً إلى السجلات والإعدادات المشار إليها أعلاه.
