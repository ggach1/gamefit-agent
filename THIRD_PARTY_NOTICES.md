# Bundled software

GameFit Windows x64 includes Python (PSF license), Pillow (MIT-CMU), and a PyInstaller-built launcher (GPL with the PyInstaller distribution exception). License texts are in `licenses/`.

Tesseract 5.5.3 Windows build and its runtime dependencies are extracted from the upstream Windows release:
https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.3
https://github.com/UB-Mannheim/tesseract/wiki
Tesseract: Apache-2.0. Original notices are preserved in `_internal/vendor/tesseract/doc/`.

Korean and English models: tessdata_fast, Apache-2.0.
https://github.com/tesseract-ocr/tessdata_fast

Runtime DLLs are dynamically linked, replaceable components from the Tesseract distribution. Upstream build and dependency sources:
https://github.com/tesseract-ocr/tesseract
https://github.com/msys2/MINGW-packages
https://www.leptonica.org/about-the-license.html

No job-posting images, user skills, or API keys are included in the distribution.
