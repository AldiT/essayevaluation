# Essay Evaluation

## Building
Run ```python3 setup.py sdist bdist_wheel``` in the root directory to build the package.

## Testing
Run ```python -m unittest test``` to run the unit tests.
## Jupyter Notebooks
We created several notebooks to complete our subgoals. Here's a short overview

### CorrelationNotebook_Step3 & CorrelationV2
Used to measure the correlation of different indices and the holistic socre

### Data Visualization
Used to generate following graphs:
- token distribution
- score distribution
- average number of token for each score

### Lexical Feature Evaluation
Used to demonstrate the binning process

### New LV Feature extraction code
tba


### Changelog

#### v0.0.2
- lexical variation indices only contain "strong lexical words"
- named entities are removed before passing them to the spell checker

#### v0.0.3
- The spell checker only marks words as spelling mistakes if they can not be found in the en_GB and en_US dictionary. 

### In equal collaboration with [Simon Klimek](mailto:go@simkli.de)

### [Documentation](https://home.in.tum.de/~klimek/essayevaluation/)