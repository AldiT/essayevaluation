Training
========

This section explains how you can calculate the bin thresholds used to evaluate an essay later. For this you need a
dataset in the form of an array of strings. You can then use the :class:`~essay_evaluation.pipeline.Pipeline` class to
get a matrix containing the feature value of all texts.

.. code-block:: python

    from essay_evaluation.pipeline import Pipeline

    texts = [
        "This is essay text1",
        "This is essay text2"
        #...
    ]

    pipeline = Pipeline().lexical_variation()\
                    .lexical_sophistication()\
                    .lexical_density()\
                    .lexical_accuracy()\
                    .collocational_aspects()

    feature_matrix, docs = pipeline.pipe(texts)



Extracting and saving the bin thresholds
----------------------------------------
You can extract the bin thresholds using the :meth:`~essay_evaluation.feedback.save_thresholds` function from the
:mod:`~essay_evaluation.feedback` module. Just pass a path or file like object and the documents from the training set.

.. code-block:: python

    from essay_evaluation.feedback import save_thresholds

    save_thresholds(docs, '/data/threshold_a1.json')

The output will be a JSON file containing the mean and standard deviation for all feature values of the training
documents. This file can be used to give feedback for new unseen documents.

Continue to :doc:`usage`.

Deprecated: Use the BinCalculator to get the bin thresholds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In previous versions, the :class:`~essay_evaluation.formative_feedback_evaluator.BinCalculator` class was used to
calculate the bin thresholds. It is still available for backward compatibility. If you are using the latest version you
can skip right ahead to :doc:`usage`.

Each row of the ``feature_matrix`` contains all feature values for one document. You can now use the
:class:`~essay_evaluation.formative_feedback_evaluator.BinCalculator` class to calculate the bin thresholds as follows:

.. code-block:: python

    from essay_evaluation.formative_feedback_evaluator import BinCalculator

    feature_indices = [6, 18, 19, 20, 21, 22, 28, 29, 30, 31, 32, 33]
    level = "A1"
    bin_calc = BinCalculator(feature_indices, feature_matrix, level)
    bin_calc.save_binning_values()

The ``feature_indices`` contains the column index inside the ``feature_matrix`` for which we want to have a binning
threshold. You have to be careful, that the indices of the features are the same when you evaluate an essay later. The
threshold will be saved in the working directory as a `.xml` file.

You can use the generated xml file to evaluate an essay now.

