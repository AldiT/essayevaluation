from spacy.tokens.doc import Doc


class LexicalDensityFeatures(object):
    name = "features_ld"

    feature_names = ["LD_LXUR", "LD_GRUR"]

    def __init__(self):
        if not Doc.has_extension(self.name):
            Doc.set_extension(self.name, default=[])

        if not Doc.has_extension(self.name + '_legacy'):
                Doc.set_extension(self.name + '_legacy', default=[])

    def __call__(self, doc):
        #CAUTION: We assume that tokenization and POS tagging is already done by the time this method is called
        doc._.features["LD_LXUR"], doc._.features["LD_GRUR"] = self.get_ld_lxur_ld_grur(doc)

        # deprecated! do not use doc._.features_ld , use doc._.features instead.
        doc._.features_ld = [doc._.features["LD_LXUR"], doc._.features["LD_GRUR"]]
        return doc


    #Ure's definition Lexical words / total # of words
    #Code: LD_LXUR
    @staticmethod
    def get_ld_lxur_ld_grur(doc):
        count_lexical_words = 0
        count_grammatical_words = 0
        total_words = 0

        for token in doc:
            if token.pos_ == "NOUN" or token.pos_ == "VERB" or token.pos_ == "ADJ"  or token.pos_ == "ADV":
               count_lexical_words += 1

            if  ((token.pos_ == "CONJ" and token.tag_ == "CC") or #coordinating conjunction
                (token.pos_ == "ADP" and token.tag_ == "IN" ) or  #subordinating conjuction
                (token.pos_ == "PART" and token.tag_ == "RP") or #adverb, particle
                (token.pos_ == "VERB" and token.tag_ == "MD") or #verb modal
                (token.pos_ == "VERB" and token.tag_ == "BES") or#auxiliary be's
                (token.pos_ == "ADJ"  and token.tag_ == "PRP$") or#possesive pronoun
                (token.pos_ == "ADJ"  and token.tag_ == "PDT") or#predeterminer
                (token.pos_ == "ADJ"  and token.tag_ == "WDT") or#wh-determiner
                (token.pos_ == "NOUN" and token.tag_ == "WP") or#wh-personal, wh-pronoun
                (token.pos_ == "ADJ"  and token.tag_ == "WP$") or#wh-possessive, wh-pronoun
                (token.pos_ == "ADV"  and token.tag_ == "WRB") or#wh-adverb
                (token.pos_ == "PART" and token.tag_ == "TO") or#infinitival to
                (token.pos_ == "ADV"  and token.tag_ == "EX") or#Existential there
                (token.pos_ == "INTJ" and token.tag_ == "UH")): #UH interjection
                count_grammatical_words += 1

            total_words += 1

        return [count_lexical_words/total_words, count_grammatical_words/total_words]