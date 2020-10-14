from spacy.tokens import Doc
from essay_evaluation import FeaturePipelineComponent


class CollocationalAspects(FeaturePipelineComponent):
    name = "features_ca"

    feature_names = ['CA_BIN1_R', 'CA_BIN2_R', 'CA_BIN3_R'
                     # , 'CA_BIN1', 'CA_BIN2', 'CA_BIN3'
                     ]

    def __init__(self):
        super().__init__()
        if not Doc.has_extension("features_ca"):
            Doc.set_extension("features_ca", default=[])

    def __call__(self, doc):
        num_of_correct_collocations = len(doc._.collocation_twf_values) * 1.00
        bins = [0.00, 0.00, 0.00]
        for twf in doc._.collocation_twf_values:
            bin = self.bin_collocation(twf)
            bins[bin] += 1

        # doc_features_ca is deprecated!
        # use doc._.features instead
        # CA_BIN1-3 are not added to doc._.features_ca because of a legacy issue with the FormativeFeatureEvaluator
        # (if added the FEE binning indexes would be wrong)

        if num_of_correct_collocations == 0:
            doc._.features['CA_BIN1_R'] = 0
            doc._.features['CA_BIN2_R'] = 0
            doc._.features['CA_BIN3_R'] = 0
            doc._.features['CA_BIN1'] = 0
            doc._.features['CA_BIN2'] = 0
            doc._.features['CA_BIN3'] = 0
            doc._.features_ca = [
                0, 0, 0,  # 0, 0, 0
            ]
        else:
            doc._.features['CA_BIN1_R'] = bins[0] / num_of_correct_collocations
            doc._.features['CA_BIN2_R'] = bins[1] / num_of_correct_collocations
            doc._.features['CA_BIN3_R'] = bins[2] / num_of_correct_collocations
            doc._.features['CA_BIN1'] = bins[0]
            doc._.features['CA_BIN2'] = bins[1]
            doc._.features['CA_BIN3'] = bins[2]
            doc._.features_ca = [
                doc._.features['CA_BIN1_R'],
                doc._.features['CA_BIN2_R'],
                doc._.features['CA_BIN3_R']
                # bins[0],
                # bins[1],
                # bins[2]
            ]

        return doc

    @staticmethod
    def bin_collocation(twf):
        if twf < 1.064:
            return 0
        if twf < 1.64:
            return 1
        return 2


if __name__ == '__main__':
    import sys
    import spacy
    from essay_evaluation import lexical_accuracy, FeaturePipelineComponent, FeaturePipelineComponent, \
        FeaturePipelineComponent, FeaturePipelineComponent, FeaturePipelineComponent

    if len(sys.argv) != 2:
        print("Usage: ", sys.argv[0], ' "this is a text"')
        sys.exit(1)

    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(lexical_accuracy.SpellChecker(), name=lexical_accuracy.SpellChecker.name, last=True)
    nlp.add_pipe(lexical_accuracy.CollocationPreprocessor(), name=lexical_accuracy.CollocationPreprocessor.name,
                 last=True)
    nlp.add_pipe(lexical_accuracy.CollocationDetector(), name=lexical_accuracy.CollocationDectector.name, last=True)
    nlp.add_pipe(lexical_accuracy.CollocationEvaluator(), name=lexical_accuracy.CollocationEvaluator.name, last=True)
    nlp.add_pipe(CollocationalAspects(), name=CollocationalAspects.name, last=True)
    doc = nlp(sys.argv[1])
    for index, name in enumerate(CollocationalAspects.feature_names):
        print(name, doc._.features_ca[index])
