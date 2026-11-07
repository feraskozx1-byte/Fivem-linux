# Frequently asked questions / أسئلة شائعة

[Home](../README.md) · [Documentation hub](INDEX.md)

### Does FiveM work on Linux with this repository?
**No complete working release was achieved.** Some modified-client launch stages worked in the recorded test environment, but the official security component did not initialize and protected public-server join was not demonstrated.

### هل نجحنا في دخول السيرفرات العامة؟
**لا.** وصلنا إلى بعض مراحل التشغيل، لكن تحميل `Adhesive.dll` والمصادقة الرسمية ظلا عائقين. هذا المستودع ليس حلًا جاهزًا.

### What is error 998?
The tested client logged `Adhesive failed to load under Wine (error 998)`. The investigations recorded an access violation during original DLL initialization, `0xC0000005` at `adhesive+0xD9FEC5`. Error 998 is the Windows `ERROR_NOACCESS` status. See [findings](FINDINGS.md).

### Why are Windows and Wine NTDLL exports compared?
An observed name-table walk ran out of bounds during loading. The test builds differed in export-name count, but **the count difference does not identify the missing function or establish the cause**. Details: [FINDINGS](FINDINGS.md).

### Was the Wine TLS incompatibility fixed?
A **narrow, isolated experimental prototype** changed the measured public API result in the expected direction. It **did not** change the Adhesive crash. It should **not** be installed as an Adhesive fix.

### Why is the repository private?
The author originally kept it private while organizing research evidence. A private GitHub archive still needs proper review for secrets and third-party licensing before any future public release. The content's private status is not a claim that its assets are safe for unrestricted publication.

### Does the repository contain the entire PS5 project?
It contains a **selected 179-file text/source evidence import** plus explanatory documents. The multi-gigabyte client binaries, official protection components, game assets, some logs and original Wine prefixes were deliberately excluded.

### Can I run the scripts or apply the patches?
They document the original experiments. Some depend on paths, specific runtime versions and binary inputs from the original host; many patches are obsolete or experiments that did not work. **Do not assume they are safe or standalone.**

### Why did the project stop?
After roughly ten days, the main user outcome was not achieved and the remaining cause was unresolved. The archive preserves both successful intermediate milestones and negative findings. See [BLOCKERS](BLOCKERS.md).

### Is this affiliated with Rockstar or Cfx.re?
No. This is an independent community research archive; original trademarks, code and binaries remain with their owners.
