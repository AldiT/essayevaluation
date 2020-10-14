from spacy.tokens.doc import Doc


class Classifier:
    name = 'Classifier'
    def __init__(self, clf, extension='score'):
        """

        :type clf: Classifier, needs to have a predict(X) function
        """
        self.clf = clf
        self.extension = extension
        if not Doc.has_extension(extension):
            Doc.set_extension(extension, default=-1)

    def __call__(self, doc):
        doc._.set(self.extension, self.clf.predict([list(doc._.features.values())])[0])
        return doc
