
# autoarchiver

autoarchiver is a scanning, OCRing and archiving-solution built on top
of various Linux libraries and utilities.

It offers a date and tag-based storage hierarchy on top of a regular
file-system making it easy to navigate, maintain and backup through
standard backup technologies and utilities like rsync, AWS S3, etc.

## features

Main features:

* Command-line only.
* Minimal syntax. Provide only what is at minimum needed.
* Automatic date-extraction from scanned documents.
* Archive existing documents into same hierarchy, and get text
  indexing included for free.

## dependencies

autoarchiver depends on the following software:

* Python3 (standard modules only)
* [SANE/XSANE](http://xsane.org/) (for scanning)
* [Tesseract](https://github.com/tesseract-ocr/tesserac) & [Leptonica](http://www.leptonica.org/) (for OCR)
* [Exact-image](http://dl.exactcode.de/oss/exact-image/) (for PDF processing)

Most of these should be available as packages on Debian-based distros,
but Tesseract may need to be built from source in order to support
HOCR-output used by Exact-image.

