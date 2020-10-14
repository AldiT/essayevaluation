Usage in production
===================

This section is meant to use this package in production, to give feedback for essays written by language learners.
In order to evaluate an essay you need two things:

1. the essay itself as string
2. the binning thresholds for the proficiency level of the writer

Preprocessing of unseen texts
-----------------------------

First of all, you need to run the essay through a spaCy pipeline. This way the feature indices are calculated for the
new, unseen text. In the next step, they will be compared to our existing bin thresholds in order to give feedback.

.. code-block:: python

    from essay_evaluation.pipeline import Pipeline

    text = "This essay will be evaluated!"

    nlp = Pipeline().lexical_variation()\
                    .lexical_sophistication()\
                    .lexical_density()\
                    .lexical_accuracy()\
                    .collocational_aspects()\
                    .get_pipe()

    doc = nlp(text)


Evaluation
----------

We now use the threshold file, generated in the :doc:`training` step before. We will use the
:class:`~essay_evaluation.feedback.Feedback` class.

    >>> from essay_evaluation.feedback import Feedback
    >>> feedback = Feedback('a1.json')
    >>> feedback.get_feedback(doc)
    {'LV_W': 'negative', 'LV_WT': 'negative', 'LV_WT1': 'negative', 'LV_TTR': 'positive', 'LV_CTTR': 'negative', 'LV_RTTR': 'negative', 'LV_HDD': 'positive', 'LV_DUGA': 'positive', 'LV_MAAS': 'positive', 'LV_SUMM': 'none', 'LV_YULEK': 'positive', 'LV_MTLD': 'negative', 'LV_MSTTR': 'negative', 'LV_MATTR': 'negative', 'TAALED_TTR_AW': 'negative', 'TAALED_MAAS_TTR_AW': 'positive', 'TAALED_MTLD_MA_WRAP_AW': 'negative', 'TAALED_MTLD_MA_WRAP_CW': 'positive', 'TAALED_MAAS_TTR_CW': 'positive', 'TAALED_BASIC_NCONTENT_TOKENS': 'negative', 'TAALED_BASIC_NFUNCTION_TYPES': 'none'}

At the end you get a dictionary containing the feature indices as key and the feedback category as value. Possible
values are ``none``, ``negative``, ``positive``.

Some feature indices should return negative feedback when the essays falls in bin 4 (``value >= mean + std``). You can
pass a list of those features as argument of the :class:`~essay_evaluation.feedback.Feedback` class' constructor.

    >>> feedback = Feedback('a1.json', ['LA_ERR', 'LA_ERR_R'])

If you don't pass this argument, the :class:`~essay_evaluation.feedback.Feedback` class will use the default list of
the module: :data:`~essay_evaluation.feedback.DEFAULT_NEGATED_INDICES`


Deprecated: Using the FormativeFeedbackEvaluator for giving feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you need to use a bin threshold file in xml format from a previous version, the
:class:`~essay_evaluation.formative_feedback_evaluator.FormativeFeedbackEvaluator` class is still included for backward
compatibility.

After having retrieved the document, you can pass it to the
:class:`~essay_evaluation.formative_feedback_evaluator.FormativeFeedbackEvaluator` class in order to get feedback for
the essay. The feature indices need to be in a specific order as the array index is hardcoded in the
:class:`~essay_evaluation.formative_feedback_evaluator.FormativeFeedbackEvaluator` class. So make sure you create a
pipeline exactly as shown above.

.. code-block:: python

    from essay_evaluation.formative_feedback_evaluator import FormativeFeedbackEvaluator

    pretrained_bin_thresholds = "./bin_thresholds.xml"
    level = "A1"

    features = list(doc._.features.values())
    feature_matrix = np.load(pretrained_bin_thresholds)

    feedback = ffe(features, level)


``feedback`` is a list containing -1 for negative feedback, 0 for no feedback and 1 for positive feedback. Each element
is for another feature index. The order of features used in the ``feedback`` list look like this (at the point of
writing this documentation):

    >>> from essay_evaluation.formative_feedback_evaluator import feature_names
    >>> feature_names
    array(['LV_W', 'LV_WT', 'LV_WT1', 'LV_TTR', 'LV_CTTR', 'LV_RTTR',
           'LV_HDD', 'LV_DUGA', 'LV_MAAS', 'LV_SUMM', 'LV_YULEK', 'LV_MTLD',
           'LV_MSTTR', 'LV_MATTR', 'LS_FPC_NG', 'LS_FPC_NA', 'LS_FPC_TC',
           'LS_FPC_BS', 'LS_FPC_CA', 'LS_FPC_CT', 'LS_FPC_CGA1',
           'LS_FPC_CGA2', 'LS_FPC_CGA3', 'LS_FOMN_NG', 'LS_FOMN_NA',
           'LS_FOMN_TC', 'LS_FOMN_BS', 'LS_FOMN_CA', 'LA_ER', 'LA_COL_ERR_R',
           'CA_BIN1_R', 'CA_BIN2_R', 'CA_BIN3_R', 'LD_LXUR', 'LD_GRUR'],
          dtype='<U12')
