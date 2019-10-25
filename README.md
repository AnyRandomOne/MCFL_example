MCFL
MissingCodeFaultLocalization

1. Getting Start

```
  git clone https://github.com/AnyRandomOne/MCFL_example.git
  cd MCFL_example
  chmod a+x run.sh
  ./run.sh
```
  The program will run the example experiment. The result is in data/result. The result include the output of experiment and compare experiment(SBFL).

  the ``experiment_**_analyze.csv'' output the result of EXAM score.

  the ``experiment_**_fault.csv'' output the detailed result of each fault location in the buggy version.

  Need: Python >= 3.6.8

    numpy >= 1.17.2

    scipy >= 1.3.1

2. File Structure

  --data: the experiment input.

    --result: the output saved here.

  --MCFL: the experiment code.

    --AST_analyzer: extract AST information from the AST code.
