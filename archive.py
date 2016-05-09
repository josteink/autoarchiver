#!/usr/bin/python3

import os
import datetime

# settings
dpi = 300
basepath = "~/DocumentArchive"

def get_date_from_parts(year, month, day):
    [iyear, imonth, iday] = map(int, [
        year, month, day
    ])
    return datetime.datetime(iyear, imonth, iday)


def get_date_from_string(string):
    import re

    if string is None:
        return None

    sep = "(_|-|\\.|\\:|\\/)?"
    date_iso = re.compile(
        "^.*" +             # whatever
        "(\\d{4})" + sep +  # year 1
        "(\\d{2})" + sep +  # month 3
        "(\\d{2})" +        # day 5
        ".*$"               # whatever
    )
    m = date_iso.match(string)
    if m is not None:
        [year, i1, month, i2, day] = m.groups()
        return get_date_from_parts(year, month, day)

    date_normal = re.compile(
        "^.*" +             # whatever
        "(\\d{2})" + sep +  # day 1
        "(\\d{2})" + sep +  # month 3
        "(\\d{4})" +        # year 5
        ".*$"               # whatever
    )
    m = date_normal.match(string)
    if m is not None:
        [day, i1, month, i2, year] = m.groups()
        return get_date_from_parts(year, month, day)

    date_no_year = re.compile(
        "^.*" +             # whatever
        "(\\d{2})" + sep +  # day 1
        "(\\d{2})"          # month 3
        ".*$"               # whatever
    )
    m = date_no_year.match(string)
    if m is not None:
        [day, i1, month] = m.groups()
        year = datetime.datetime.now().year
        return get_date_from_parts(year, month, day)

    return None


def get_tags(tags):
    return tags or ["Ukategorisert"]


def open_silently(command, error_message, custom_stdin=None):
    import subprocess

    print("Exec: " + " ".join(command))

    stdin_value = None
    if custom_stdin:
        stdin_value = subprocess.PIPE

    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        stdin=stdin_value
    )

    if stdin_value:
        proc.stdin.write(custom_stdin)
        proc.stdin.flush()
        proc.stdin.close()

    output = proc.stdout.read()
    retcode = proc.wait()
    if retcode is not 0:
        raise Exception((error_message + ":\n%r") % output)


def scan_document():
    import tempfile

    # scan original
    fid, scanned = tempfile.mkstemp(suffix=".tiff")
    open_silently([
        "scanimage", "--resolution=" + str(dpi), "--format=tiff", scanned
    ], "Error attempting to scan document.")
    return scanned


def ocr_document(source, txt_only=False):
    import tempfile
    fid, temp_base = tempfile.mkstemp(prefix="ocr_")
    os.unlink(temp_base)

    # preprocess for OCR
    tesseract_source = temp_base + ".tiff"
    open_silently([
        "convert", "-quiet", "-density", dpi, "-depth", "8",
        "-colorspace", "Gray",
        # avoid alpha channel. required so that processed PDFs can be
        # processed by leptonica and tesseract.
        "-background", "white", "-flatten", "+matte",
        source, tesseract_source
    ], "Error preparing scanned document for tesseract.")

    # OCR scanned document
    tesseract_txt = temp_base + ".txt"

    # create TXT
    open_silently([
        "tesseract", tesseract_source, temp_base,
        "-l", "nor"
    ], "Error processing document with tesseract.")

    if txt_only:
        os.unlink(tesseract_source)
        return (None, tesseract_txt)

    # create HTML
    tesseract_html = temp_base + ".html"
    open_silently([
        "tesseract", tesseract_source, temp_base,
        "-l", "nor", "hocr"
    ], "Error processing document with tesseract.")

    # combine source TIFF and ocr data to PDF
    pdf = temp_base + ".pdf"
    with open(tesseract_html, "rb") as f:
        html = f.read()
        open_silently([
            "hocr2pdf", "-r", "-" + str(dpi), "-i", source,
            "-o", pdf
        ], "Errror processing document!", custom_stdin=html)

    # remove temp-file
    delete_files([tesseract_source, tesseract_html])

    return (pdf, tesseract_txt)


def archive(pdf, txt, date, tags):
    from shutil import copy

    print("PDF: %r\nTXT: %r\nDate: %r\nArgs: %r" % (pdf, txt, date, tags))

    date_part = "{0}/{1:02d}/{2:02d}".format(
        date.year, date.month, date.day
    )
    tags_part = " ".join(tags)
    path = os.path.join(os.path.expanduser(basepath), date_part, tags_part)

    if os.path.isdir(path):
        num = 2
        template = path + " ({0})"
        while True:
            path = template.format(num)
            if not os.path.isdir(path):
                break
            num += 1

    # create target dir and archive
    os.makedirs(path)
    copy(pdf, path)
    copy(txt, path)


def delete_files(files):
    for file in files:
        print("Not deleting: %r" % file)
        #os.unlink(file)


def main():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument("--date", "-d", help="Date of the archived document.")
    p.add_argument("--file", "-f", help="The file to archive. If omitted, document will be retrieved from scanner.")
    p.add_argument("tags", nargs="*", help="The tags to apply to the document.")

    args = p.parse_args()

    date = get_date_from_string(args.date)
    tags = get_tags(args.tags)
    filename = args.file

    if filename is None:
        # scan, OCR to TXT and create PDF
        filename = scan_document()
        pdf, txt = ocr_document(filename)
        archive(pdf, txt, date, tags)
        delete_files([filename, pdf, txt])
        return

    else:
        # validate
        filename = os.path.expanduser(filename)
        if not os.path.isfile(filename):
            raise Exception(
                "Cannot process file: '{0}'. File not found!".format(filename)
            )

        base, ext = os.path.splitext(filename)
        if ext.lower() == ".pdf":
            # create TXT index, but archive PDF as is.
            # TODO: use pandoc or something better for this,
            _, txt = ocr_document(filename, txt_only=True)
            archive(filename, txt, date, tags)
            delete_files([txt])
        else:
            # OCR to TXT, and create PDF
            pdf, txt = ocr_document(filename)
            archive(pdf, txt, date, tags)
            delete_files([pdf, txt])


if __name__ == "__main__":
    main()
