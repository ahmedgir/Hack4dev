# Backend — مرحلة تجهيز البيانات للويب

في نسخة الهاكثون لا توجد خدمة Backend تعمل على الإنترنت. المقصود بالـBackend هنا هو كود Python المحلي الذي يحول المخرجات العلمية إلى حزمة ثابتة وآمنة للواجهة.

## المسؤوليات

1. قراءة المخرجات الموثوقة من `outputs/` و`config/targets.json`.
2. التحقق من وجود الحقول المطلوبة وعدم تغيير `scientific_status`.
3. دمج معلومات النظام والجلسات في JSON واضح للواجهة.
4. نسخ الصور اللازمة وتحويل إطارات الـTimeline إلى WebP مضغوط.
5. إزالة المسارات المحلية وأي ملفات FITS/WCS كبيرة من حزمة النشر.
6. إنتاج manifest واحد يساعد الواجهة على معرفة الأنظمة والجلسات المتاحة.

## المخرجات المقترحة

```text
webapp/frontend/public/
├── data/
│   ├── systems.json
│   └── systems/
│       └── corot-2/
│           ├── system.json
│           └── sessions/
│               └── 2026-08-09/
│                   ├── summary.json
│                   ├── light-curve.json
│                   ├── timeline.json
│                   └── field.json
└── media/
    └── systems/
        └── corot-2/
            └── 2026-08-09/
                ├── verified-field.webp
                ├── raw.webp
                ├── calibrated.webp
                └── frames/
                    ├── 000.webp
                    └── ...
```

## مصادر الحقيقة الحالية

- `config/targets.json`: أسماء الكواكب والإحداثيات والقيم المنشورة.
- `outputs/audit/session_completeness.json`: اكتمال الجلسات.
- `outputs/<system>/<date>/summary.json`: حكم الجلسة والمقاييس.
- `outputs/<system>/<date>/web_light_curve.json`: نقاط الرسم.
- `outputs/<system>/<date>/web_timeline.json`: كل الإطارات المقبولة والمرفوضة.
- `outputs/<system>/<date>/01_verified_field.png`: صورة الحقل المثبت.

## عقد البيانات الضروري

### System card

- `slug`
- `star_name`
- `planet_name`
- `published_depth_percent`
- `period_days`
- `duration_hours`
- `best_session_id`
- `best_session_status`
- `available_sessions`

### Session summary

- `id`, `date`, `target`
- `accepted_frames`, `total_frames`
- `pre_transit_points`, `in_transit_points`, `post_transit_points`
- `published_depth_percent`, `fitted_depth_percent`
- `fitted_duration_hours`, `fitted_mid_offset_minutes`
- `residual_scatter_percent`
- `coverage_complete`, `precision_sufficient`
- `scientific_status`, `fit_valid`, `fit_interpretation`
- `limitations_ar`, `limitations_en`

### Timeline frame

- `frame`, `time`, `preview_path`
- `relative_flux`, `model_flux`
- `accepted`, `rejection_reason`
- `target_snr`, `background`
- `shift_x`, `shift_y`, `registration_stars`

يجب أن يبقى كل إطار في الـTimeline، بما فيه المرفوض، مع سبب الرفض.

## ما لا يفعله هذا الجزء

- لا يشغّل التحليل عند زيارة المستخدم.
- لا يقدم API حيًا.
- لا يخزن FITS في Vercel.
- لا يعيد حساب WCS أو photometry.
- لا يصحح نتيجة علمية يدويًا داخل JSON.

## سياسة الصور

- حوّل معاينات الـTimeline إلى WebP؛ لا تستخدم PNG لكل الإطارات إلا عند الحاجة العلمية.
- احتفظ بنسخة عالية الوضوح من صورة الحقل المثبت.
- الرسم الأساسي للـlight curve ينتج من JSON داخل الواجهة.
- `02_light_curve.png` و`03_quality_control.png` مواد توثيق/احتياط، وليستا بديلًا عن التجربة التفاعلية.

## التحقق قبل النشر

- كل مسار صورة داخل JSON نسبي ويعمل من `public/`.
- عدد عناصر Timeline يساوي `total_frames`.
- عدد `accepted=true` يساوي `accepted_frames`.
- لا توجد ملفات FITS أو مفاتيح أو مسارات من جهاز المطور.
- حالات CoRoT-2 وQatar-1 وWASP لم تتغير لغويًا أو رقميًا.
- حجم الحزمة النهائية مناسب للتحميل السريع.

## متى نعيد التفكير في FastAPI؟

فقط إذا أضفنا حسابات، تعليقات، رفع بيانات، بحثًا معقدًا، أو تشغيل pipeline عبر الإنترنت. عندها يكون FastAPI خيارًا منطقيًا، لكنه خارج Scope الهاكثون الحالي.

