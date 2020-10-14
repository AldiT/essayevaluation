Getting started
===============
The essay_evaluation packages basically consists of serveral spaCy pipeline components. Before you start you should get
yourself comfortable with using the spaCy pipeline and adding components. Have a look at `spaCy's documentation
<https://spacy.io/usage/processing-pipelines>`_ for more information.


The pipeline builder
--------------------
Instead of adding the components manually to the spaCy pipeline, you should always use the
:class:`~essay_evaluation.pipeline.Pipeline` builder provided by this package. Some components have dependencies on
other components. The pipeline builder always makes sure, that all required components are added to the spaCy pipeline.

.. code-block:: python

    from essay_evaluation.pipeline import Pipeline

    nlp = Pipeline().lexical_variation()\
                    .lexical_accuracy()\
                    .collocational_aspects()\
                    .get_pipe()

    doc = nlp("This is a test")

If you want to use a specific spaCy model just pass it to the constructor of the
:class:`~essay_evaluation.pipeline.Pipeline` class.

You can even use the :class:`~essay_evaluation.pipeline.Pipeline`
class directly:

.. code-block:: python

    from essay_evaluation.pipeline import Pipeline

    pipeline = Pipeline().lexical_variation()
    doc = pipeline("This is a test")


Components
----------
Here is an overview of pipeline components provided by this package. One special kind of components are the so called
*feature* components. They calculate a specific feature index values (like type-token-ration) and store them in a
feature dictionary, which can be accessed using ``doc._.features``.

    >>> from essay_evaluation.pipeline import Pipeline
    >>> nlp = Pipeline().lexical_variation().get_pipe()
    >>> doc = nlp("This is a tests")
    >>> doc._.features
    OrderedDict([('LV_W', 2), ('LV_WT', 2), ('LV_WT1', 2), ('LV_TTR', 1.0), ('LV_CTTR', 1.0), ('LV_RTTR', 1.414213562373095), ('LV_HDD', 0.0), ('LV_DUGA', 0), ('LV_MAAS', 0), ('LV_SUMM', 1.0), ('LV_YULEK', 0.0), ('LV_MTLD', 2.0), ('LV_MSTTR', 2), ('LV_MATTR', 2)])
    >>> nlp = Pipeline().lexical_variation().lexical_density().get_pipe()
    >>> doc = nlp("This is a tests")
    >>> doc._.features
    OrderedDict([('LV_W', 2), ('LV_WT', 2), ('LV_WT1', 2), ('LV_TTR', 1.0), ('LV_CTTR', 1.0), ('LV_RTTR', 1.414213562373095), ('LV_HDD', 0.0), ('LV_DUGA', 0), ('LV_MAAS', 0), ('LV_SUMM', 1.0), ('LV_YULEK', 0.0), ('LV_MTLD', 2.0), ('LV_MSTTR', 2), ('LV_MATTR', 2), ('LD_LXUR', 0.5), ('LD_GRUR', 0.0)])

You can access features values easily using the dictionary access:

    >>> doc._.features['LV_WT']
    2



Our package provides following spaCy pipeline components:

Feature components:
^^^^^^^^^^^^^^^^^^^

You can access the feature values provided by these components using ``doc._.features['FEATURE_NAME']``.

- :class:`~essay_evaluation.collocational_aspects.CollocationalAspects`
- :class:`~essay_evaluation.lexical_accuracy.LexicalAccuracy`
- :class:`~essay_evaluation.lexical_density.LexicalDensityFeatures`
- :class:`~essay_evaluation.lexical_sophistication.LexicalSophisticationFeatures`
- :class:`~essay_evaluation.lexical_variation.LexicalVariationFeatures`
- :class:`~essay_evaluation.lexical_variation_taaled.LexicalVariationTaaled`

Other components:
^^^^^^^^^^^^^^^^^

These might add their own extension the the spaCy document object. Please refer to the class documentation
of the component to see the added extension and how to access them.

- :class:`~essay_evaluation.association_scores.AssociationScores`
- :class:`~essay_evaluation.lexical_accuracy.CollocationDetector`
- :class:`~essay_evaluation.lexical_accuracy.CollocationEvaluator`
- :class:`~essay_evaluation.lexical_accuracy.CollocationPreprocessor`
- :class:`~essay_evaluation.lexical_variation_taaled.IsRepetition`
- :class:`~essay_evaluation.lexical_accuracy.SpellChecker`
- :class:`~essay_evaluation.lexical_accuracy.TaaledTokenClassifier`



After you understood the basics you can dive in and see how the heuristic and machine learning approach can be used.