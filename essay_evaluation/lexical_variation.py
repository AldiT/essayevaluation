import warnings
from collections import Counter

from lexicalrichness import LexicalRichness
from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from collections import defaultdict

from essay_evaluation import FeaturePipelineComponent

features_lv = ['LV_W', 'LV_WT', 'LV_WT1', 'LV_TTR', 'LV_CTTR', 'LV_RTTR', 'LV_HDD', 'LV_DUGA', 'LV_MAAS', 'LV_SUMM',
               'LV_YULEK', 'LV_MTLD', 'LV_MSTTR', 'LV_MATTR']


class LexicalVariationFeatures(FeaturePipelineComponent):
    """
    Spacy pipline component which adds lexical variation index values to a document.
    Algorithm descriptions from LexicalRichness (inspect.getdoc(LexicalRichness.XXX)
    """
    name = "features_lv"

    feature_names = ['LV_W', 'LV_WT', 'LV_WT1', 'LV_TTR', 'LV_CTTR', 'LV_RTTR', 'LV_HDD', 'LV_DUGA', 'LV_MAAS', 'LV_SUMM',
                   'LV_YULEK', 'LV_MTLD', 'LV_MSTTR', 'LV_MATTR']

    hdd_draws = 35
    """
        see the HDD formula for details:
        import inspect
        inspect.getdoc(LexicalRichness.hdd)
    """

    mtld_threshold = 0.72
    """
    Factor threshold for MTLD. Algorithm skips to a new segment when TTR goes below the
    threshold (default=0.72).
    """

    msttr_segment_window = 25
    """
    Size of each segment (default=100).
    """

    msttr_discard = True
    """
    If True, discard the remaining segment (e.g. for a text size of 105 and a segment_window
    of 100, the last 5 tokens will be discarded). Default is True.
    """

    mattr_window_size = 25
    """
    Size of each sliding window for the mattr algorithm.
    """

    def __init__(self):
        super().__init__()

        if not Doc.has_extension(self.name):
            Doc.set_extension(self.name, default=[])

        if not Token.has_extension('is_lexical'):
            Token.set_extension('is_lexical', default=False)


    def __call__(self, doc):
        # check if the tagger component is part of the pipeline
        if not doc.is_tagged:
            warnings.warn('The spaCy document was not tagged. Please add the TAGGER component or else the '
                          'lexical variation indices will be based on all tokens and not just lexical ones!', Warning)
            lex = LexicalRichness(doc.text)

        else:
            # remove all non lexical words
            self.mark_lexical_token(doc)
            list_lexical_words = [str(token) for token in doc if token._.is_lexical]

            lexical_word_text = ' '.join(list_lexical_words)

            lex = LexicalRichness(lexical_word_text)

        

        doc._.features['LV_W'] = self.get_lv_w(lex)
        doc._.features['LV_WT'] = self.get_lv_wt(lex)
        doc._.features['LV_WT1'] = self.get_lv_wt1(lex)
        doc._.features['LV_TTR'] = self.get_lv_ttr(lex)
        doc._.features['LV_CTTR'] = self.get_lv_cttr(lex)
        doc._.features['LV_RTTR'] = self.get_lv_rttr(lex)
        doc._.features['LV_HDD'] = self.get_lv_hdd(lex)
        doc._.features['LV_DUGA'] = self.get_lv_duga(lex)
        doc._.features['LV_MAAS'] = self.get_lv_maas(lex)
        doc._.features['LV_SUMM'] = self.get_lv_summ(lex)
        doc._.features['LV_YULEK'] = self.get_lv_yulek(lex)
        doc._.features['LV_MTLD'] = self.get_lv_mtld(lex)
        doc._.features['LV_MSTTR'] = self.get_lv_msttr(lex)
        doc._.features['LV_MATTR'] = self.get_lv_mattr(lex)


        # deprecated! do not use doc._.features_lv anymore, use doc._.features instead!
        doc._.features_lv = [
            doc._.features['LV_W'],
            doc._.features['LV_WT'],
            doc._.features['LV_WT1'],
            doc._.features['LV_TTR'],
            doc._.features['LV_CTTR'],
            doc._.features['LV_RTTR'],
            doc._.features['LV_HDD'],
            doc._.features['LV_DUGA'],
            doc._.features['LV_MAAS'],
            doc._.features['LV_SUMM'],
            doc._.features['LV_YULEK'],
            doc._.features['LV_MTLD'],
            doc._.features['LV_MSTTR'],
            doc._.features['LV_MATTR']
        ]

        return doc

    @staticmethod
    def mark_lexical_token(doc):
        for token in doc:
            token._.is_lexical = ((token.pos_ == "NOUN" and token.tag_ != 'NNP' and token.tag_ != 'NNPS') or
                (token.pos_ == "VERB" and token.tag_ != 'MD') or
                token.pos_ == "ADJ" or token.pos_ == "ADV")


    @staticmethod
    def get_lv_w(lex):
        """
        LV_W: #tokens
        :param doc:
        :return: int, number of tokens inside the whole document
        """
        # todo: return len(doc) is different to lex.words
        return lex.words

    @staticmethod
    def get_lv_wt(lex):
        """
        LV_WT: #types (word types)
        :param doc:
        :return:
        """
        # TODO: can this be done in a simpler way?
        # return len(set([token.lemma for token in doc])) # todo: different to Edas results
        return lex.terms

    @staticmethod
    def get_lv_wt1(lex):
        """
        LV_WT1: number of unique tokens
        Todo: why is this called LD_WT1 and not LD_W1 ?? it's not about types
        :param doc:
        :return:
        """
        # c = Counter([str(token) for token in doc])
        # return len([t for t, num in c.items() if num == 1]) todo: why is this different to Eda's code?
        frequency_dict = Counter()
        word_list = Counter(lex.wordlist)

        for k in word_list.keys():
            frequency_dict[word_list[k]] += 1

        return frequency_dict[1]

    @staticmethod
    def get_lv_ttr(lex):
        """
        LV_TTR: type token ration
        :param tex:
        :param lex:
        :return:
        """
        if lex.words == 0:
            return 0
        return lex.ttr

    @staticmethod
    def get_lv_cttr(lex):
        """
        LV_CTTR: corrected type token ration
        :param lex:
        :return:
        """
        if lex.words == 0:
            return 0
        return lex.cttr

    @staticmethod
    def get_lv_rttr(lex):
        """
        LV_RTTR: Index of Guiraud, Guiraud's Root TTR
        :param lex:
        :return:
        """
        if lex.words == 0:
            return 0
        return lex.rttr

    def get_lv_hdd(self, lex):
        """
        LV_HDD: Hypergeometric distribution diversity (HD-D) score.
        :param doc:
        :param lex:
        :return:
        """
        if lex.words < self.hdd_draws:
            return 0.0
        return float(lex.hdd(draws=self.hdd_draws))

    @staticmethod
    def get_lv_duga(lex):
        """
        LV_DUGA: Computed as (log(w) ** 2) / (log(w) - log(t)), where t is the number of unique terms/vocab,
        and w is the total number of words.
        (Dugast 1978)
        :param lex:
        :return:
        """
        if lex.words == lex.terms:
            return 0  # see formula (div by 0)
        return lex.Dugast

    @staticmethod
    def get_lv_maas(lex):
        """
        LV_MAAS: Maas's TTR, computed as (log(w) - log(t)) / (log(w) * log(w)), where t is the number of
        unique terms/vocab, and w is the total number of words. Unlike the other measures, lower
        maas measure indicates higher lexical richness.
        (Maas 1972)
        :param lex:
        :return:
        """
        if lex.words == lex.terms:
            return 0  # see formula (div by 0)
        return lex.Maas

    @staticmethod
    def get_lv_summ(lex):
        """
        LV_SUMM: Computed as log(log(t)) / log(log(w)), where t is the number of unique terms/vocab, and
        w is the total number of words.
        (Summer 1966)
        :param lex:
        :return:
        """
        if lex.words <= 1 or lex.terms <= 1:  # see formula (log(terms)
            return 0.0
        return lex.Summer

    @staticmethod
    def get_lv_yulek(lex):
        """
        LV_YULEK: Yule’s K
        Todo: refactor!
        :param lex:
        :return:
        """
        N = lex.words
        if N == 0:
            return 0.0
        frequency_dict = Counter()
        word_list = Counter(lex.wordlist)
        for k in word_list.keys():
            frequency_dict[word_list[k]] += 1

        K_yulek = 0

        for k in frequency_dict.keys():
            K_yulek += (k ** 2) * frequency_dict[k]

        return (K_yulek - N) / (1.0 * (N ** 2))

    def get_lv_mtld(self, lex):
        """
        LV_MTLD: Measure of textual lexical diversity, computed as the mean length of sequential words in
        a text that maintains a minimum threshold TTR score.

        Iterates over words until TTR scores falls below a threshold, then increase factor
        counter by 1 and start over. McCarthy and Jarvis (2010, pg. 385) recommends a factor
        threshold in the range of [0.660, 0.750].
        (McCarthy 2005, McCarthy and Jarvis 2010)

        :return:
        :param lex:
        :return:
        """
        if lex.words == 0:
            return 0.00
        return lex.mtld(threshold=self.mtld_threshold)

    def get_lv_msttr(self, lex):
        """
        LV_MSTTR: Mean segmental TTR (MSTTR) computed as average of TTR scores for segments in a text.

        Split a text into segments of length segment_window. For each segment, compute the TTR.
        MSTTR score is the sum of these scores divided by the number of segments.
        (Johnson 1944)
        todo: what to do if len(doc) < msttr_segment_window? (Eda: return number of token)
        :param doc:
        :param lex:
        :return:
        """
        if lex.words <= self.msttr_segment_window:
            return lex.words

        return lex.msttr(segment_window=self.msttr_segment_window, discard=self.msttr_discard)

    def get_lv_mattr(self, lex):
        """
        Moving average TTR (MATTR) computed using the average of TTRs over successive segments
        of a text.

        Estimate TTR for tokens 1 to n, 2 to n+1, 3 to n+2, and so on until the end
        of the text (where n is window size), then take the average.
        (Covington 2007, Covington and McFall 2010)
        todo: what to do if len(doc) < mattr_window_size? (Eda: return number of token)
        :param lex:
        :return:
        """
        if lex.words <= self.mattr_window_size:
            return lex.words
        return lex.mattr(window_size=self.mattr_window_size)

"""
This object is a spacy component meant to add to each token the field is_repetition which will be true if it is a repetition, and false if it isn't.
"""
class IsRepetition(FeaturePipelineComponent):
    name = 'detect_repetitions'
    def __init__(self):
        super().__init__()

        if not Doc.has_extension(self.name):
            Doc.set_extension(self.name, default=[])

        if not Token.has_extension('is_repetition'):
            Token.set_extension('is_repetition', default=False)

    
    def __call__(self, doc):
        return self._find_repetitions(doc)

    """
    Put all lemmas in a dict and count which ones are repeted
    """
    def _find_repetitions(self, doc):
        lemma_dict = defaultdict(lambda: 0)

        for token in doc:
            if not token.is_stop and not token._.in_coref:
                lemma_dict[token.lemma_.lower()] += 1

        for token in doc:
            if not token.is_punct and not token.is_stop and not token._.in_coref and lemma_dict[token.lemma_.lower()] > 1:
                token._.is_repetition = True
        
        return doc


if __name__ == '__main__':
    import sys
    import spacy
    if len(sys.argv) != 2:
        print("Usage: ", sys.argv[0], ' "this is a text"')
        sys.exit(1)

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(LexicalVariationFeatures(), name=LexicalVariationFeatures.name, last=True)
    doc = nlp(sys.argv[1])
    for index, name in enumerate(LexicalVariationFeatures.feature_names):
        print(name, doc._.features_lv[index])