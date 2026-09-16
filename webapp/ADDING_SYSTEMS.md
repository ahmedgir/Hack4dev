# إضافة نظام أو جلسة جديدة إلى الموقع

هذه التعليمات مصممة للفريق ولأي جلسة Codex لاحقة. لا تعدّل مكونات React لكل كوكب؛ أضف البيانات والأصول إلى العقد الموحد فقط.

## ما يحتاجه الموقع لكل جلسة

### إلزامي

1. `summary.json`
2. `web_light_curve.json`
3. صورة حقل موثقة تحدد النجم المضيف، ويفضل WebP أو PNG.
4. سجل النظام الأساسي داخل `webapp/frontend/src/data/catalog.json` (مرة واحدة فقط لكل نظام).

### اختياري حاليًا

- إطارات Timeline بصيغة WebP.
- Raw / calibrated comparison.
- صورة quality control.
- جلسات إضافية للنظام نفسه.

إذا غابت صورة اختيارية يجب أن تعرض الواجهة حالة «قيد التجهيز» ولا تفترض مسارًا غير موجود.

## بنية الملفات

```text
webapp/frontend/public/
├── data/systems/<slug>/<date>/
│   ├── summary.json
│   └── light-curve.json
└── media/systems/<slug>/<date>/
    ├── verified-field.webp
    └── frames/
        ├── 0000.webp
        └── ...
```

## الحالات العلمية المسموحة

- `promising_preliminary_transit`
- `insufficient_for_transit_claim`
- `transit_like_but_parameters_inconsistent`
- `not_analysed`

لا يخترع Codex حالة أخرى ولا يرفع قوة الادعاء من دون تعديل موثق في الـpipeline.

## Prompt جاهز لـCodex

انسخ النص التالي بعد اكتمال أي كوكب:

```text
أضف النظام <SYSTEM> والجلسة <DATE> إلى موقع Hack4Dev.

مصدر نتائج الـpipeline:
outputs/<OUTPUT_FOLDER>/<DATE>/

التزم بـwebapp/ADDING_SYSTEMS.md، وانسخ summary.json وweb_light_curve.json وصورة
01_verified_field.png إلى بنية public الصحيحة. حدّث catalog.json فقط ولا تغيّر
scientific_status أو القيم العلمية. إذا كانت timeline_frames موجودة انسخها، وإذا لم
توجد اتركها اختيارية ولا تنشئ صورًا وهمية. شغّل pnpm validate:data ثم pnpm build.
لا تعدّل تصميم المكونات إلا إذا تغيّر عقد البيانات نفسه.
```

## الطريقة الأسرع الموحّدة

إذا كان النظام موجودًا أصلًا في `catalog.json`، لا تنسخ الملفات ولا تكتب سجل الجلسة يدويًا. من داخل `webapp/frontend` شغّل:

```bash
pnpm import:session --slug=wasp-10 --output=../../outputs/wasp_10/2026-08-08
pnpm build
```

الأمر يقرأ القيم العلمية حرفيًا من `summary.json`، وينسخ المنحنى وصورة الحقل إلى `public/`، ثم يضيف الجلسة أو يحدّثها باستخدام `slug + date`. صفحات `/systems/<slug>` والبطاقات تُبنى تلقائيًا من نفس `catalog.json`، لذلك لا ننسخ مكونات React لكل كوكب.

لإضافة نظام جديد كليًا، أضف مرة واحدة ملفه التعريفي المنشور إلى `catalog.json` مع `sessions: []`، ثم استخدم الأمر نفسه لكل جلسة مكتملة. لا تضف نتائج تحليل يدويًا ولا تغيّر `scientific_status`.

## عندما نحتاج صورًا جديدة من الـpipeline

اطلب من مسؤول الـpipeline إضافة Export واضح بدل تعديل الصورة يدويًا. الأنواع المفيدة:

- `verified-field`: الهدف ونجوم المقارنة مع legend قصير.
- `raw-frame`: عرض FITS بتمديد بصري موحد.
- `calibrated-frame`: الإطار نفسه بعد Master Dark.
- `timeline-frame`: صورة نظيفة مع موضع الهدف فقط وحالة القبول/الرفض في JSON، لا كنص مطبوع داخل الصورة.
- `quality-map`: الخلفية وSNR والانجراف عند الحاجة.

الأفضل ألا يكتب الـpipeline جملًا طويلة داخل الصور؛ النصوص والترجمة وحالات الجودة مسؤولية الواجهة. الصورة تحمل البيانات البصرية، وJSON يحمل المعنى.

## فحص الإضافة

من `webapp/frontend`:

```bash
pnpm validate:data
pnpm build
```

يفشل الفحص إذا كان مسار ملف أساسي غير موجود، أو كانت الحالة العلمية غير معروفة، أو كان عدد المقبول أكبر من عدد الإطارات.
