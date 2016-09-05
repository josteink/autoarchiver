
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
* Easily locate documents based on tags or content.

## dependencies

autoarchiver depends on the following software:

* Python3 (only standard modules required)
* [SANE/XSANE](http://xsane.org/) (for scanning)
* [ImageMagick](http://www.imagemagick.org/script/index.php) (for OCR pre-processing)
* [Tesseract](https://github.com/tesseract-ocr/tesserac) & [Leptonica](http://www.leptonica.org/) (for OCR)
* [Exact-image](http://dl.exactcode.de/oss/exact-image/) (for PDF
  processing)

Most of these should be available as packages on Debian-based
distros. As of Ubuntu 16.04 this also includes Tesseract, but on
earlier distries Tesseract may need to be [built from source](https://github.com/josteink/machine-build/blob/master/profiles/80-documentarchive-deps.conf) in order to support
the HOCR-output used by Exact-image.

## installation

On Ubuntu 16.04 you can use the following commands to install all
dependencies and setup autoarchiver for simple CLI usage:

````bash
$ sudo apt install python3 sane-utils imagemagick tesseract-ocr
$ cd $HOME
$ git clone https://github.com/josteink/autoarchiver
$ mkdir -p $HOME/bin
$ export PATH=$PATH:$HOME/bin
$ ln -s $HOME/autoarchiver/archive.py $HOME/bin/da
````

## usage

To use autoarchiver simply invoke the `archive.py` (or whatever
short-hand alias you've created) from the command-line:

````bash
$ ./archive.py --help
usage: archive.py [-h] [--date DATE] [--file FILE] [tags [tags ...]]

positional arguments:
  tags                  The tags to apply to the document.

optional arguments:
  -h, --help            show this help message and exit
  --date DATE, -d DATE  Date of the archived document. Use when auto-detection
                        fails.
  --file FILE, -f FILE  The file to archive. If omitted, document will be
                        retrieved from scanner.
````

Archived documents will be stored in `$HOME/DocumentArchive` sorted on
date, and stored with tags.

Date will be attempted detected from the document. Overriding
detection can be done from the command-line. You can use as minimal
syntax as possible "31-12" will be interpreted as December 31th, this
year. Etc.

Both a plain-text OCRed representation (easily searched by `grep`) and
a PDF containing the originally scanned document merged with the OCRed
data will be available in a per-archived document folder.

This means you can easily identity documents based either on the tags
used to archive it, the period it was archived or the content of the
scanned document using standard Linux command-line tools like `find`
and `grep`.

A simple tool for these kind of queries is included in the form of a
shell-script called [da-search](da-search.sh).

