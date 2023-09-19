[under construction]

This repo is a toolkit to manage ML experiments.

It allows to organize hyperparameters and experiments configurations, load and save results, and perform hyperparameter search using some optimization algorithm.


## Installation

To install the latest stable version, run the following:
```bash
pip install experiments-manager
```

To install the latest version, run the following:
```bash
pip install git+https://github.com/jvasso/experiments_manager
```


## Quickstart

This is the basic structure of a project with experiments-manager:

```bash
├── main.py
├── config
│   ├── hyperparams.yaml
│   ├── exp_config.yaml
│   └── extra_config.yaml
├── ids
└── results
```

To run an experiment, you simply need to complete these 2 steps:
- set your config files
- define your experiment

### Step 1: set your config files

There are 3 files in ```config/``` which set the parameters of the experiment(s):

- ```hyperparams.yaml``` (can also be a directory): contains all the hyperparameters of the ML model. Try multiple hyperparams values by entering a list (example below).
- ```exp_config.yaml``` (can also be a directory): contains the parameters of the experiment (dataset, RL environment etc.). Similarly to ```hyperparams.yaml``` you can run multiple experiments by entering lists of values. The idea is that two experimental results obtained with different ```exp_config``` values are not comparable (i.e. they are different experiments).
- ```extra_config.yaml```: contains other parameters such as the metrics to measure, the number of seeds for each exp, the metrics for the gridsearch, the logging policy etc.

```yaml
# config/hyperparams.yaml
num_layers: [4,6]
activation: ["relu", "tanh"]
```
This will run all configurations: {"num_layers": 4, "activation": "relu"}, {"num_layers": 4, "activation": "tanh"}, {"num_layers": 6, "activation": "relu"} etc.

```yaml
# config/exp_config.yaml
dataset: "dataset1"
train_test_split: 0.8
```

```yaml
# config/extra_config.yaml
log_frequency: 5
metrics: {"train_loss", "valid_loss"} # metrics measured at each experiment
gridsearch_metric: "valid_loss"       # metric used for the gridsearch (it will drive the search in the hyperparameter space)
criteria_complete_result: {"seed":10} # criteria that must be fulfilled to consider one experiment as complete (--> as many "trials" as values: here, 10 seeds will be tried)
```

### Step 2: define your experiment

To run your own experiment, you just need to subclass the ```Experiment``` base class, which contains one mandatory method: ```run_experiment```.

```python
from experiments_manager.experiment import Experiment
from experiments_manager.config import ConfigManager
from experiments_manager.experiment import ExperimentManager

class CustomExperiment(Experiment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_experiment(self, trial_params):
        seed = trial_params["seed"]

        num_layers = self.config.hyperparams.num_layers
        activation = self.config.hyperparams.activation
        loss = self.config.exp_config.loss

        model = MyModel(num_layers=num_layers, activation=activation)
        results = model.train(loss=loss)
        return result

configManager = ConfigManager()
experimentManager = ExperimentManager(configManager, experiment_cls=CustomExperiment)
experimentManager.run_experiments()
results = experimentManager.compare_results(metrics=["valid_loss"])
```