#!/usr/bin/env python3
"""
Подготовка фото перед ASCII-конвертацией:
  1. убрать фон (rembg, если установлен)
  2. поднять локальный контраст (CLAHE через OpenCV, если установлен)
  3. положить на белый фон -> фон уходит в пробелы ASCII-рампы

  python scripts/prep_photo.py my-photo.jpg   ->  source-prepped.png
"""
import sys, os
from PIL import Image, ImageOps, ImageEnhance

src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
im = Image.open(src).convert("RGBA")

# 1) фон
try:
    from rembg import remove
    im = remove(im)
    print("rembg: фон удалён")
except Exception as e:
    print("rembg недоступен, пропускаю удаление фона:", e)

# 2) белая подложка
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
bg.alpha_composite(im)
g = bg.convert("L")

# 3) контраст
try:
    import numpy as np, cv2
    arr = np.array(g)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    g = Image.fromarray(clahe.apply(arr))
    print("CLAHE: контраст поднят")
except Exception as e:
    print("OpenCV недоступен, использую autocontrast:", e)
    g = ImageOps.autocontrast(g, cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(1.35)

g.save("source-prepped.png")
print("wrote source-prepped.png", g.size)
