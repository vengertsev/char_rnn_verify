# Formal Verification of Character RNN

Code to reproduce the results in [Recurrent Neural Network Properties and Their Verification with Monte Carlo Techniques](https://scholarworks.boisestate.edu/cgi/viewcontent.cgi?article=1237&context=cs_facpubs). 

# Data sets
The data for char-rnn training is [Nietzsche texts](https://www.kaggle.com/pankrzysiu/nietzsche-texts).  <br />

# Execution
train_char_rnn.ipynb - trains next character prediction RNN using Nietzsche dataset

calc_ground_truth.ipynb - calculates ground truth (next character) for the whole training dataset and stores states 

properties_analysis.ipynb - initial visualization of the properties (like confidence of the character)
![Character prediction confidence](/img/confidence_visualization.png)

robustness.ipynb, long_term_relationship.ipynb, memorization.ipynb - properties verification

calc_convergence.ipynb - calcualte the convergence statistics for Table 1

# Requirements
Import python conda environment using requirements.txt

# Citations

Below are the paper to cite if you find the algorithms in this repository useful in your own research:
```
@article{vengertsev2020recurrent,
  title={Recurrent Neural Network Properties and Their Verification with Monte Carlo Techniques},
  author={Vengertsev, Dmitri and Sherman, Elena},
  year={2020}
}
```

# License Info

This code is offered under the [MIT License](https://opensource.org/licenses/MIT).
