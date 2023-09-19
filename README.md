[under construction]

This repo is a toolkit to manage ML experiments.

It allows to organize hyperparameters and experiments configurations, load and save results, and perform hyperparameter search using some optimization algorithm.


## Installation

To install the latest stable version, run the following:
```bash
pip install experiments-manager
```

Install the latest version, run the following:
```bash
pip install git+https://github.com/jvasso/experiments_manager
```


## Quickstart

This is the basic tree structure of a project with experiments-manager.

```bash
├── main.py
├── config
│   ├── hyperparams.yaml
│   ├── exp_config.yaml
│   └── extra_config.yaml
├── ids
└── results
```

Each time a new experiment is launched, the ```ConfigManager``` will load the parameters from the ```config/``` directory and extract the configurations of hyperparameters and experiments which have not been tested.
Then the ```ExperimentManager``` runs these configurations and saves the results in ```results/```.

To run an experiment, you simply need to complete these 2 steps:
• set your config files
• set your experiment


### Step 1: set your config files

Configure the settings of your experiment (use a list to run multiple configurations):
```yaml
# file: config/exp_config.yaml
dataset: "dataset1"
loss: "mse"
train_test_split: 0.8
```

Set the hyperparameters of your ML model (use a list to run multiple configurations):
```yaml
# file: config/hyperparams.yaml
num_layers: [4,6]
activation: ["relu", "tanh"]
# this will run all configurations: {"num_layers": 4, "activation": "relu"}, {"num_layers": 4, "activation": "tanh"} etc.
```

Other parameters (results, logs, metrics used for the gridsearch etc.):
```yaml
# file: config/extra_config.yaml
log_frequency: 5

# results params (mandatory)
metrics: {"train_loss", "valid_loss"} # metrics measured at each experiment
gridsearch_metric: "valid_loss"       # metric used for the gridsearch (it will drive the search in the hyperparameter space)
criteria_complete_result: {"seed":10} # criteria that must be fulfilled to consider one experiment as complete (--> as many "trials" as values: here, 10 seeds will be tried)
```


### Step 2: run your own experiment

To run your own experiment, you just need to subclass the `Experiment` base class.


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