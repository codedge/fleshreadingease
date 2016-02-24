#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from urllib import request
from bs4 import BeautifulSoup
from xml.etree import ElementTree
from re import search
import os
import humanfriendly

def is_url_or_file(item):
    ret = "file"

    if search("http[s]", item):
        ret = "url"
    return ret


def remove_html_tags(t):
    return ''.join(ElementTree.fromstring(t).itertext())


def readability_index(lang, asl, asw):
    idx = 206.835 - (1.015 * asl) - (84.6 * asw)
    if lang == "de":
        idx = 180 - asl - (58.5 * asw)
    return idx


def readability_notes(index):
    note = "Very difficult to read. Best understood by university graduates."

    if index > 90:
        note = "Very easy to read. Easily understood by an average 11-year-old student."
    elif index > 80:
        note = "Easy to read. Conversational English for consumers."
    elif index > 70:
        note = "Fairly easy to read."
    elif index > 60:
        note = "Plain English. Easily understood by 13- to 15-year-old students."
    elif index > 50:
        note = "Fairly difficult to read."
    elif index > 30:
        note = "Difficult to read."

    return note


def count_syllables(lang, word):
    """
    Detect syllables in words
    Thanks to http://codegolf.stackexchange.com/questions/47322/how-to-count-the-syllables-in-a-word
    """
    if lang == 'en':
        cnt = len(''.join(" x"[c in"aeiouy"]for c in(word[:-1]if'e' == word[-1]else word)).split())
    else:
        cnt = len(''.join(" x"[c in"aeiou"]for c in(word[:-1]if'e' == word[-1]else word)).split())
    return cnt


def output(r_idx, r_note):
    print()
    print("Readability checker (Flesh Reading Ease)")
    print("========================================")
    print()
    print("Score:\t%.2f" % r_idx)
    print("Note:\t%s" % r_note)
    exit()


def main(arguments):
    src = arguments.source
    lang = arguments.lang
    source_type = is_url_or_file(src)
    paragraphs = []
    sentences_cnt = 0
    word_cnt = 0
    syllables_cnt = 0

    if source_type == "url":
        content = request.urlopen(src).read()
        paragraphs = BeautifulSoup(content, "html.parser").find_all("p")
        for idx, el in enumerate(paragraphs):
            paragraphs[idx] = remove_html_tags(str(el))

    else:
        if os.path.isfile(src):
            with open(src, "r") as f:
                content = f.read()
                paragraphs = content.split("\n\n")
        else:
            print("-> The specified file (" + src + ") does not exist!")
            exit()

    if len(paragraphs) > 0:
        for p in paragraphs:
            words = p.split()
            word_cnt += len(words)
            sentences_cnt += len(p.split("."))

            for w in words:
                syllables_cnt += count_syllables(lang, w)

        asl = word_cnt / sentences_cnt
        asw = syllables_cnt / word_cnt
        ridx = readability_index(lang, asl, asw)
        output(ridx, readability_notes(ridx))
    else:
        print("-> No text to analyze!")


if __name__ == '__main__':
    parser = ArgumentParser(description="Check the readability of a given text (URL or local file) with the \
    Flesh Reading Ease algorithm.")
    parser.add_argument('lang', default="en", help="Select the language of the text, supported 'en' or 'de'")
    parser.add_argument('source', help="Specify a URL (http://example.com) or a local file (path/to/file)")
    args = parser.parse_args()
    main(args)
