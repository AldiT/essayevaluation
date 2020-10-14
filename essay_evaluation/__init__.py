from spacy.tokens.doc import Doc
from collections import OrderedDict

import os
import logging

name = "essay_evaluation"

class FeaturePipelineComponent:

    def __init__(self):
        if not Doc.has_extension("features"):
            Doc.set_extension("features", default=OrderedDict())


debug_logging_mode = False
if "EE_MODE" in os.environ:
    if os.environ['EE_MODE'].lower() == "debug":
        debug_logging_mode = True


##Use the mode set above to set the logging level
logging.basicConfig(filename="./essay_evaluation.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w')


logger = logging.getLogger()