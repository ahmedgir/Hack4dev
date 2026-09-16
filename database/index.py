import os
import pandas as pd
from astropy.io import fits

# 1. تحديد اسم مجلد البيانات الرئيسي (تأكد من كتابة الاسم الصحيح للمجلد لديك)
DATASET_ROOT = "."  # قم بتغيير هذا إلى اسم مجلد البيانات الخاص بك

records = []

print("جاري فحص المجلدات واستخراج البيانات من ملفات FITS...")

# 2. المرور التلقائي على جميع المجلدات والملفات الفرعية
for root, dirs, files in os.walk(DATASET_ROOT):
    for file in files:
        if file.lower().endswith(('.fits', '.fit')):
            full_path = os.path.join(root, file)
            # استخراج المسار النسبي ليعمل الكود على أي جهاز دون مشاكل
            rel_path = os.path.relpath(full_path, DATASET_ROOT) 
            
            try:
                with fits.open(full_path) as hdul:
                    header = hdul[0].header
                    
                    target = header.get("OBJECT", "Unknown")
                    date_obs = header.get("DATE-OBS", None)
                    # MicroObservatory files use EXPTIME; keep EXPOSURE as a fallback.
                    exposure = header.get("EXPTIME", header.get("EXPOSURE", None))
                    filter_type = header.get("FILTER", "Unknown")
                    
                    obs_date = date_obs.split('T')[0] if date_obs and 'T' in str(date_obs) else date_obs
                    
                    records.append({
                        "file_name": file,
                        "relative_path": rel_path,
                        "target_name": target,
                        "date_obs": date_obs,
                        "obs_date": obs_date,
                        "exposure": exposure,
                        "filter": filter_type
                    })
            except Exception as e:
                print(f"خطأ في قراءة الملف {file}: {e}")

# 3. حفظ البيانات في ملف CSV داخل مجلد البيانات الرئيسي
df = pd.DataFrame(records)
output_path = "dataset_index.csv"
df.to_csv(output_path, index=False)

print(f"تم بنجاح! تم إنشاء ملف الفهرس: {output_path}")
print(f"إجمالي عدد الصور المفهـرسة: {len(df)}")
