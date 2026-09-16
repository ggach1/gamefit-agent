$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force '.build-tools', 'vendor' | Out-Null
Invoke-WebRequest 'https://github.com/tesseract-ocr/tesseract/releases/download/5.5.3/tesseract-ocr-w64-setup-5.5.3.20260724.exe' -OutFile '.build-tools/tesseract-setup.exe'
Invoke-WebRequest 'https://www.7-zip.org/a/7z2301-x64.msi' -OutFile '.build-tools/7zip.msi'
$msi = Join-Path $PSScriptRoot '.build-tools\7zip.msi'
$target = Join-Path $PSScriptRoot '.build-tools\7zip'
Start-Process msiexec.exe -ArgumentList ('/a "' + $msi + '" /qn TARGETDIR="' + $target + '"') -Wait -WindowStyle Hidden
$extractor = Join-Path $target 'Files\7-Zip\7z.exe'
$ocrTarget = Join-Path $PSScriptRoot 'vendor\tesseract'
& $extractor x '.build-tools/tesseract-setup.exe' "-o$ocrTarget" -y
if ($LASTEXITCODE -ne 0) { throw 'OCR extraction failed' }
foreach ($lang in @('kor', 'eng')) {
    Invoke-WebRequest "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/$lang.traineddata" -OutFile "vendor/tesseract/tessdata/$lang.traineddata"
}
& 'vendor/tesseract/tesseract.exe' --version
