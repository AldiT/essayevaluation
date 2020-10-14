import os

from spacy.tokens.doc import Doc

from essay_evaluation import FeaturePipelineComponent
from lexical_diversity import lex_div

### THESE ARE PERTINENT FOR ALL IMPORTANT INDICES ####
noun_tags = ["NN", "NNS", "NNP", "NNPS"]  # consider whether to identify gerunds
proper_n = ["NNP", "NNPS"]
no_proper = ["NN", "NNS"]
pronouns = ["PRP", "PRP$"]
adjectives = ["JJ", "JJR", "JJS"]
verbs = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "MD"]
adverbs = ["RB", "RBR", "RBS"]
content = ["NN", "NNS", "NNP", "NNPS", "JJ", "JJR", "JJS"]  # note that this is a preliminary list
prelim_not_function = ["NN", "NNS", "NNP", "NNPS", "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "VB", "VBD", "VBG", "VBN",
                       "VBP", "VBZ", "MD"]
pronoun_dict = {"me": "i", "him": "he", "her": "she"}
punctuation = "`` '' ' . , ? ! ) ( % / - _ -LRB- -RRB- SYM : ;".split(" ")
punctuation.append('"')


class TaaledTokenClassifier():
    name = 'taaled_token_classifier'

    def __init__(self):
        if not Doc.has_extension('taaled_lemmas'):
            Doc.set_extension('taaled_lemmas', default=[])

        if not Doc.has_extension('context_tokens'):
            Doc.set_extension('context_tokens', default=[])

        if not Doc.has_extension('function_tokens'):
            Doc.set_extension('function_tokens', default=[])

        # Load TAALED word list files
        # source: https://github.com/kristopherkyle/TAALED/tree/master/TAALED_1_3_1_Py3/dep_files
        module_path = os.path.abspath(os.path.dirname(__file__))
        adj_lem_list_path = os.path.join(module_path, "Corpora/adj_lem_list.txt")
        real_words_path = os.path.join(module_path, "Corpora/real_words.txt")

        self.adj_word_list = open(adj_lem_list_path, "r", errors='ignore').read().split("\n")[:-1]
        self.real_word_list = open(real_words_path, "r", errors='ignore').read().split("\n")[:-1]

    def __call__(self, doc):
        for sent in doc.sents:
            for token in sent:
                if token.tag_ in punctuation:
                    continue
                if token.text.lower() not in self.real_word_list:  # lowered because self.real_word_list is lowered
                    continue

                if token.tag_ in content:
                    if token.tag_ in noun_tags:
                        doc._.context_tokens.append(token.lemma_ + "_cw_nn")
                        doc._.taaled_lemmas.append(token.lemma_ + "_cw_nn")
                    else:
                        doc._.context_tokens.append(token.lemma_ + "_cw")
                        doc._.taaled_lemmas.append(token.lemma_ + "_cw")

                if token.tag_ not in prelim_not_function:
                    if token.tag_ in pronouns:
                        if token.text.lower() in pronoun_dict:
                            doc._.function_tokens.append(pronoun_dict[token.text.lower()] + "_fw")
                            doc._.taaled_lemmas.append(pronoun_dict[token.text.lower()] + "_fw")
                        else:
                            doc._.function_tokens.append(token.text.lower() + "_fw")
                            doc._.taaled_lemmas.append(token.text.lower() + "_fw")
                    else:
                        doc._.function_tokens.append(token.lemma_ + "_fw")
                        doc._.taaled_lemmas.append(token.lemma_ + "_fw")

                if token.tag_ in verbs:
                    if token.dep_ == "aux":
                        doc._.function_tokens.append(token.lemma_ + "_fw")
                        doc._.taaled_lemmas.append(token.lemma_ + "_fw")

                    elif token.lemma_ == "be":
                        doc._.function_tokens.append(token.lemma_ + "_fw")
                        doc._.taaled_lemmas.append(token.lemma_ + "_fw")

                    else:
                        doc._.context_tokens.append(token.lemma_ + "_cw_vb")
                        doc._.taaled_lemmas.append(token.lemma_ + "_cw_vb")

                if token.tag_ in adverbs:
                    if (token.lemma_[-2:] == "ly" and token.lemma_[:-2] in self.adj_word_list) or (
                            token.lemma_[-4:] == "ally" and token.lemma_[:-4] in self.adj_word_list):
                        doc._.context_tokens.append(token.lemma_ + "_cw")
                        doc._.taaled_lemmas.append(token.lemma_ + "_cw")
                    else:
                        doc._.function_tokens.append(token.lemma_ + "_fw")
                        doc._.taaled_lemmas.append(token.lemma_ + "_fw")
        return doc


class LexicalVariationTaaled(FeaturePipelineComponent):

    name = 'lexical_variation_taaled'

    feature_names = ['TAALED_TTR_AW', 'TAALED_MTLD_MA_WRAP_CW', 'TAALED_MTLD_MA_WRAP_AW', 'TAALED_MAAS_TTR_CW',
                     'TAALED_MAAS_TTR_AW', 'TAALED_BASIC_NCONTENT_TOKENS', 'TAALED_BASIC_NFUNCTION_TYPES']

    def __init__(self):
        super(LexicalVariationTaaled, self).__init__()

    def __call__(self, doc):
        if (len(doc._.taaled_lemmas) == 0):
            doc._.features['TAALED_TTR_AW'] = 0
            doc._.features['TAALED_MAAS_TTR_AW'] = 0
            doc._.features['TAALED_MTLD_MA_WRAP_AW'] = 0
        else:
            doc._.features['TAALED_TTR_AW'] = lex_div.root_ttr(doc._.taaled_lemmas)
            doc._.features['TAALED_MAAS_TTR_AW'] = lex_div.maas_ttr(doc._.taaled_lemmas)
            doc._.features['TAALED_MTLD_MA_WRAP_AW'] = lex_div.mtld_ma_wrap(doc._.taaled_lemmas)

        if (len(doc._.context_tokens) == 0):
            doc._.features['TAALED_MTLD_MA_WRAP_CW'] = 0
            doc._.features['TAALED_MAAS_TTR_CW'] = 0
        else:
            doc._.features['TAALED_MTLD_MA_WRAP_CW'] = lex_div.mtld_ma_wrap(doc._.context_tokens)
            doc._.features['TAALED_MAAS_TTR_CW'] = lex_div.maas_ttr(doc._.context_tokens)

        doc._.features['TAALED_BASIC_NCONTENT_TOKENS'] = len(doc._.context_tokens)
        doc._.features['TAALED_BASIC_NFUNCTION_TYPES'] = len(set(doc._.function_tokens))
        return doc

class LexicalAccuracyTaaled(LexicalVariationTaaled):
    """
    deprecated! use LexicalVariationTaaled instead
    """
    pass

if __name__ == '__main__':
    import sys
    import spacy
    if len(sys.argv) != 2:
        print("Usage: ", sys.argv[0], ' "this is a text"')
        sys.exit(1)

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(TaaledTokenClassifier(), name=TaaledTokenClassifier.name, last=True)
    nlp.add_pipe(LexicalAccuracyTaaled(), name=LexicalAccuracyTaaled.name, last=True)
    doc = nlp(sys.argv[1])
    for name in LexicalAccuracyTaaled.feature_names:
        print(name, doc._.features[name])