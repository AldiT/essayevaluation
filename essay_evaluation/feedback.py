"""
essay_evaluation.feedback
~~~~~~~~~~~~~~~~~~~~~~~~~
Contains a helper methods for calculating and storing the bin thresholds and also a class for giving feedback for a
given document.
"""

import pandas as pd

DEFAULT_NEGATED_INDICES = ['LA_ER', 'LA_COL_ERR_R', 'CA_BIN1_R']


def save_thresholds(docs, file=None):
    """Calculates the mean and standard deviation for a list of documents

    :param docs: List of spaCy document objects
    :param file: str or file handle, optional
            File path or object. If not specified, the result is returned as
            a string.
    :return: json string or None if the file parameter is set.
    """
    df = pd.DataFrame([d._.features for d in docs])
    mean = df.mean().rename("mean")
    std = df.std().rename("std")
    return pd.concat([mean,std], axis=1).to_json(file)


class Feedback:
    """Returns if a document should get feedback for each feature index it was trained for.
    """
    def __init__(self, threshold_file, negated_indices = None):
        """This class stores a pretrained threshold file and assigns feedback to spaCy document objects.

        :param threshold_file: str or file handle, should be a json encoded file generated by the save_thresholds
                method.
        :param negated_indices: list of feature indices where BIN 4 (value >= mean + std) indicates negative feedback,
                optional.
        """
        self.thresholds = pd.read_json(threshold_file)

        if negated_indices is None:
            negated_indices = DEFAULT_NEGATED_INDICES

        self.negated_indices = negated_indices

    def get_feedback(self, doc):
        """Gives feedback for a single spaCy document.

        :param doc: spaCy document object.
        :return: dict containing feedback for each pre-trained feature. Keys are the feature name, value contains one
                 of ['positive', 'negative', 'none'].
        """
        result = {}
        for index, row in self.thresholds.iterrows():
            if index not in doc._.features:
                continue

            if doc._.features[index] <= row['mean'] - row['std']:
                result[index] = 'negative' if index in self.negated_indices else 'positive'
            elif doc._.features[index] >= row['mean'] + row['std']:
                result[index] = 'positive' if index in self.negated_indices else 'negative'
            else:
                result[index] = 'none'
        return result

    def pipe(self, docs):
        """Returns a generator which returns feedback for the spaCy documents.

        :param docs: iterable returning spaCy document objects.
        :return: generator which yields a feedback dict with feature names as keys and values representing the feedback.
                Possibles values are: 'positive', 'negative' or 'none'.
        """
        return (self.get_feedback(d) for d in docs)