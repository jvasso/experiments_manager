[under construction]

This repo is a toolkit to manage ML experiments.

It allows to organize hyperparameters and experiments' configurations, load and save results, and perform hyperparameter search using some optimization algorithm.


### Basic usage


#### Step 1: set your configuration files

Configure the settings of your experiment (use a list to run multiple configurations):
```yaml
# file: config/exp_config.yaml

loss: "loss1"
```

Set the hyperparameters of your ML model (use a list to run multiple configurations):
```yaml
# file: config/hyperparams.yaml

num_layers: [4,6]
activation: ["relu", "tanh"]
```

Other parameters (results, logs, metric used for gridsearch etc.):
```yaml
# file: config/extra_config.yaml

verbose: 1
log_frequency: 5
gridsearch_metric: "test"
```


#### Step 2: run your own experiment

To run your own experiment, you first need to subclass the `Experiment` base class.

```python
from experiments_manager.experiment import Experiment

class CustomExperiment(Experiment):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run_experiment(self):
        num_layers = self.config.hyperparams.num_layers
        activation = self.config.hyperparams.activation
        loss = self.config.expConfig.loss
        model = MyModel(num_layers=num_layers, activation=activation)
        results = model.train(loss=loss)
        # results = {"train":random.randint(0,9), "test":random.randint(0,9)}
        return result
```

Then you can write the following code to run all the configurations and save results.

```python
from experiments_manager.config import ConfigManager
from experiments_manager.experiment import ExperimentManager

configManager = ConfigManager()
experimentManager = ExperimentManager(configManager, experiment_cls=CustomExperiment)
experimentManager.run_experiments()

```