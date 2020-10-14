#!/usr/bin/env python3
import argparse
import html
import sys
"""
changelog from v1:
- now uses a token-range-condition [50-200] instead of the previous "n essays clostest to the mean"-condition
"""

try:
    from bs4 import BeautifulSoup as BS
    import spacy
    import numpy as np
except ImportError as err:
    print('Dependencies misssing. Please install the ' + str(err.name) + ' module')
    exit()


# spaCy pipeline components
class TokenCountPipelineComponent(object):
    name = "token_counter"

    def __init__(self):
        self.token_count = []
        self.lexical_words_count = []

    def __call__(self, doc):
        list_lexical_words = [str(token) for token in doc if token.pos_ == "NOUN" or token.pos_ == "VERB" or \
                                      token.pos_ == "ADJ" or token.pos_ == "ADV"]

        self.token_count.append(len(doc))# __len__ get the number of tokens in the document
        self.lexical_words_count.append(len(list_lexical_words))

        return doc


def read_essays(input_files):
    """
    reads a list of xml files of the EFCAMDAT corpus
    :param input_files:
    :return: texts, grades, xml
    """
    essays = []
    grades = []
    xml = []

    cnt = 0

    for file in input_files:
        cnt = 0

        with open(file) as fh:
            soup = BS(fh, "lxml")
            writings = soup.find_all("writing")
            for writing in writings:

                if cnt > 10000:
                    break
                cnt += 1

                textxml = writing.find("text")
                if textxml is not None:
                    essays.append(html.unescape(textxml.text))
                    grades.append(int(writing.find('grade').text))
                    xml.append(str(writing))
                else:
                    print("error while reading xml")
    return essays, grades, xml


def get_token_counts(essays):
    nlp = spacy.load('en_core_web_sm')

    # we only need the tokenizer from spaCy
    nlp.remove_pipe('tagger')
    nlp.remove_pipe('parser')
    nlp.remove_pipe('ner')

    token_counter = TokenCountPipelineComponent()
    nlp.add_pipe(token_counter, name=token_counter.name, last=True)

    docs = list(nlp.pipe(essays))

    return docs, token_counter.token_count, token_counter.lexical_words_count



def get_args():
    parser = argparse.ArgumentParser(description='This tool offers to filter the EFCAMDAT dataset based on specified '
                                                 'requirements. (e.g. same essay length, equal distributed scores, ...')
    parser.add_argument('input_files', nargs='+', help='an integer for the accumulator')
    parser.add_argument('output_file', help='an integer for the accumulator')
    parser.add_argument('--length', action='store_true', help='')
    parser.add_argument('-n', '--number', type=int, help='number of essays which shall be output', default=10000)

    return parser.parse_args()


def main():
    args = get_args()
    print("read essays")
    essays, grades, xml = read_essays(args.input_files)

    if len(essays) < args.number:
        print('input data is smaller or equal than requested number of essays (' + str(len(essays)) + ' <= ' +
              str(args.number) + ')')
        exit()

    print("count tokens")
    docs, tk, lex_words = get_token_counts(essays)
    token_counts = np.array(tk)
    lexical_words_count = np.array(lex_words)

    print("Info about lexical words.")
    print("Mean: ", np.mean(lexical_words_count))
    print("Min: ", np.min(lexical_words_count))
    print("Max: ", np.max(lexical_words_count))
    print("Essays: ", len(lexical_words_count))

    print("\nSamples")
    
    mask_0 = (lexical_words_count == 0)
    mask_1 = (lexical_words_count == 1)
    mask_other = ((lexical_words_count > 1) & (lexical_words_count <= 10))

    print("Lexical Word num: ", lexical_words_count[np.argmax(mask_0)])
    print("Sample: {}".format(essays[np.argmax(mask_0)]))
    print("Pos tags: {}".format([token.pos_ for token in docs[np.argmax(mask_0)]]))

    print("Lexical Word num: ", lexical_words_count[np.argmax(mask_1)])
    print("Sample: {}".format(essays[np.argmax(mask_1)]))
    print("Pos tags: {}".format([token.pos_ for token in docs[np.argmax(mask_1)]]))

    print("Lexical Word num: ", lexical_words_count[np.argmax(mask_other)])
    print("Sample: {}".format(essays[np.argmax(mask_other)]))
    print("Pos tags: {}".format([token.pos_ for token in docs[np.argmax(mask_other)]]))

    #filter based on the token counts
    mask_a1_a2 = ((token_counts >= 50) & (token_counts <= 200) & (lexical_words_count >= 35))
    mask_rest = ((token_counts >= 150) & (token_counts <= 300) & (lexical_words_count >= 35))
    #token_counts = token_counts[mask_a1_a2]

    mask = mask_a1_a2

    essays = np.array(essays)
    grades = np.array(grades)
    
    xml = np.array(xml)


    essays = essays[mask]
    grades = grades[mask]
    xml = xml[mask]

    xml = xml.tolist()
    if len(xml) == 0:
        print("No instances for A1")
        
        sys.exit(1)
    print("Instances left: ", len(xml))

    print("write result")
    with open(args.output_file, 'w') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write('<selection id="filtered_selection">\n')
        fh.write('<meta name="inputfiles">' + ','.join(args.input_files) + '</meta>\n')
        fh.write('<writings>\n')

        for index, essay_tag in enumerate(xml):
            #if index >= args.number:
            #    break

            fh.write(essay_tag + '\n')

        fh.write('</writings>\n')
        fh.write('</selection>')


if __name__ == "__main__":
    main()
