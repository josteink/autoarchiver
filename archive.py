#!/usr/bin/python3

import os
import datetime
import re

# settings
dpi = 300
basepath = "~/DocumentArchive"


def get_date_from_parts(year, month, day):
    [iyear, imonth, iday] = map(int, [
        year, month, day
    ])
    return datetime.date(iyear, imonth, iday)


def get_validated_date(year, month, day):
    try:
        date = get_date_from_parts(year, month, day)
        is_ok = (date.year > 1970 and not date > datetime.date.today())
        if is_ok:
            return date

    except:
        return None

    return None

#
# date regexps
# pre-compiled for better performance when generating training-data
# for ML.
#

sep = "(_|-|\\.|\\:|\\/| )?"
date_iso = re.compile(
    "^.*" +               # whatever
    "(\\d{4})" + sep +    # year 1
    "(\\d{2})" + "\\2" +  # month 3
    "(\\d{2})" + sep +    # day 4
    ".*$"                 # whatever
)

date_normal = re.compile(
    "^.*" +               # whatever
    "(\\d{2})" + sep +    # day 1
    "(\\d{2})" + "\\2" +  # month 3
    "(\\d{4})" + sep +    # year 4
    ".*$"                 # whatever
)

date_no_year = re.compile(
    "^(.*[^\\d]+)?" + sep +  # whatever
    "(\\d{2})" + sep +       # day 1
    "(\\d{2})" + sep +       # month 3
    ".*$"                    # whatever
)


def get_date_from_string(string):
    if string is None:
        return None

    m = date_iso.match(string)
    if m is not None:
        [year, i1, month, day, i2] = m.groups()
        date = get_validated_date(year, month, day)
        if date:
            return date

    m = date_normal.match(string)
    if m is not None:
        [day, i1, month, year, i2] = m.groups()
        date = get_validated_date(year, month, day)
        if date:
            return date

    m = date_no_year.match(string)
    if m is not None:
        [i0, i01, day, i1, month, i2] = m.groups()
        year = datetime.date.today().year
        date = get_validated_date(year, month, day)
        if date:
            return date

    return None


def get_tags(tags):
    return tags or ["Ukategorisert"]


def format_date(date, seperator="/"):
    formatted = "{0}{3}{1:02d}{3}{2:02d}".format(
        date.year, date.month, date.day, seperator
    )
    return formatted


def get_user_choice(values, default):
    while True:
        result = input("Please input a value between {0} and {1}. Default = {2}: ".format(
            min(values), max(values), default
        ))

        if result == '':
            result = default

        try:
            value = int(result)
            if value in values:
                return value
        except:
            continue


def get_dates_from_contents(file):
    with open(file, 'r') as f:
        contents = f.read()
        lines = contents.split("\n")

        dates = {}
        for line in lines:
            date = get_date_from_string(line)
            if not date:
                continue

            if date not in dates:
                dates[date] = []

            dates[date].append(line)

        return dates


def get_date_from_contents(file):
    dates = get_dates_from_contents(file)

    if len(dates) == 0:
        return None

    if len(dates) == 1:
        return dates.keys()[0]

    print("Found {0} dates in document.\n".format(len(dates)))

    count = 1
    for date, lines in sorted(dates.items()):
        print("{0}: {1}:".format(count, format_date(date)))
        for line in lines:
            print("- {0}".format(line))
        print("")
        count += 1

    choice = get_user_choice(range(1, count), 1)
    date = sorted(dates.keys())[choice - 1]
    return date


def get_date_modified(filename):
    t = os.path.getmtime(filename)
    return datetime.date.fromtimestamp(t)


def get_date_for_file(pdf, txt):
    date = get_date_from_contents(txt) \
           or get_date_modified(pdf)

    return date


def open_silently(command, error_message, custom_stdin=None):
    import subprocess

    # print("Exec: " + " ".join(command))

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

    return output


def scan_document():
    import tempfile

    # scan original
    print("Scanning...")
    fid, scanned = tempfile.mkstemp(suffix=".tiff")
    bytes = open_silently([
        "scanimage", "--resolution=" + str(dpi), "--format=tiff"
    ], "Error attempting to scan document.")

    with open(scanned, 'wb') as f:
        f.write(bytes)

    return scanned


def ocr_document(source, txt_only=False):
    import tempfile
    fid, temp_base = tempfile.mkstemp(prefix="ocr_")
    os.unlink(temp_base)

    # preprocess for OCR
    print("Preparing for OCR...")
    tesseract_source = temp_base + ".tiff"
    open_silently([
        "convert", "-quiet", "-density", str(dpi), "-depth", "8",
        "-colorspace", "Gray",
        # avoid alpha channel. required so that processed PDFs can be
        # processed by leptonica and tesseract.
        "-background", "white", "-flatten", "+matte",
        source, tesseract_source
    ], "Error preparing scanned document for tesseract.")

    # OCR scanned document
    tesseract_txt = temp_base + ".txt"

    # create TXT
    print("OCRing...")
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
    print("Creating PDF...")
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

    print("Archiving...")

    if date is None:
        date = get_date_for_file(pdf, txt)

    # print("PDF: %r\nTXT: %r\nDate: %r\nArgs: %r" % (pdf, txt, date, tags))

    date_part = format_date(date)
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

    print("Archiving to {0}...".format(path))
    # create target dir and archive
    os.makedirs(path)
    tpdf = os.path.join(path, "result.pdf")
    ttxt = os.path.join(path, "result.txt")
    copy(pdf, tpdf)
    copy(txt, ttxt)


def delete_files(files):
    for file in files:
        os.unlink(file)


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
