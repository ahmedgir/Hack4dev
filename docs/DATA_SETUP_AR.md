# تجهيز البيانات الخام

صور FITS غير مرفوعة إلى Git لأن حجمها نحو 1.1 GB. الفهارس والـmetadata موجودة داخل `database/`، أما كل عضو فيضع الصور محليًا في البنية التالية:

```text
database/
  observations/
    2026-08-09/
      CoRoT-2/
        session_01/
          *.fits
  calibration/
    2026-08-09/
      Dark-*.fits
  metadata/
  dataset_index.csv
```

لتشغيل المثال الأقوى، يكفي أولًا نقل:

```text
database/observations/2026-08-09/CoRoT-2/session_01/
database/calibration/2026-08-09/
```

ثم:

```powershell
conda activate exoplanet-poc
.\run_poc.ps1 --target CoRoT-2 --date 2026-08-09 --cached-only
```

خيار `--cached-only` يستخدم حل WCS الموجود في `outputs/` ولا يرسل الصورة إلى Astrometry.net.

## مشاركة البيانات بين الفريق

استخدموا Google Drive أو Dropbox أو قرصًا محليًا لمجلدي `observations` و`calibration`. لا تضيفوا ملفات FITS إلى Git، ولا تستخدموا Git LFS قبل اتفاق الفريق؛ البيانات الأصلية منفصلة عن كود المشروع ونتائجه المشتقة.

## التحقق بعد النقل

يجب أن تظهر الأعداد التالية عند اكتمال المجموعة:

- 1,681 صورة علمية.
- 60 صورة معايرة.
- 1,741 ملف FITS إجمالًا.
- 8 أهداف و22 جلسة.
