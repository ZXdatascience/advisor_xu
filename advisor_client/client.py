import os
import json
import requests

from suggestion.models import Study
from suggestion.models import Trial
from suggestion.models import TrialMetric
from suggestion.algorithm.random_search import RandomSearchAlgorithm
from suggestion.algorithm.grid_search import GridSearchAlgorithm
from suggestion.algorithm.bayesian_optimization import BayesianOptimization
from suggestion.algorithm.tpe import TpeAlgorithm
from suggestion.algorithm.simulate_anneal import SimulateAnnealAlgorithm
from suggestion.algorithm.hyperopt_random_search import HyperoptRandomSearchAlgorithm
from suggestion.algorithm.quasi_random_search import QuasiRandomSearchAlgorithm
from suggestion.algorithm.chocolate_random_search import ChocolateRandomSearchAlgorithm
from suggestion.algorithm.chocolate_grid_search import ChocolateGridSearchAlgorithm
from suggestion.algorithm.chocolate_bayes import ChocolateBayesAlgorithm
from suggestion.algorithm.cmaes import CmaesAlgorithm
from suggestion.algorithm.mocmaes import MocmaesAlgorithm
from suggestion.algorithm.skopt_bayesian_optimization import SkoptBayesianOptimization


class AdvisorClient(object):
  def __init__(self):
    pass

  def create_study(self,
                   study_name,
                   study_configuration,
                   algorithm="BayesianOptimization"):
    study = Study.create(study_name, study_configuration, algorithm)

    return study

  # TODO: Support load study by configuration and name
  def get_study_by_name(self, study_name):

    return Study.objects.get_by_name(study_name)

  def get_or_create_study(self,
                          study_name,
                          study_configuration,
                          algorithm="BayesianOptimization"):

    if Study.objects.isin(study_name) == True:
      study = self.get_study_by_name(study_name)
    else:
      study = self.create_study(study_name, study_configuration, algorithm)

    return study

  def list_studies(self):
    return Study.objects.list_objects()

  def list_trials(self, study_name):
    return [trial for trial in Trial.objects.list_objects() if trial.study_name == study_name]

  def get_suggestions(self, study_name, trials_number=1):
    study = Study.objects.get(name=study_name)
    trials = Trial.objects.filter(study_name=study_name)

    if study.algorithm == "RandomSearch":
      algorithm = RandomSearchAlgorithm()
    elif study.algorithm == "GridSearch":
      algorithm = GridSearchAlgorithm()
    elif study.algorithm == "BayesianOptimization":
      algorithm = BayesianOptimization()
    elif study.algorithm == "TPE":
      algorithm = TpeAlgorithm()
    elif study.algorithm == "HyperoptRandomSearch":
      algorithm = HyperoptRandomSearchAlgorithm
    elif study.algorithm == "SimulateAnneal":
      algorithm = SimulateAnnealAlgorithm()
    elif study.algorithm == "QuasiRandomSearch":
      algorithm = QuasiRandomSearchAlgorithm()
    elif study.algorithm == "ChocolateRandomSearch":
      algorithm = ChocolateRandomSearchAlgorithm()
    elif study.algorithm == "ChocolateGridSearch":
      algorithm = ChocolateGridSearchAlgorithm()
    elif study.algorithm == "ChocolateBayes":
      algorithm = ChocolateBayesAlgorithm()
    elif study.algorithm == "CMAES":
      algorithm = CmaesAlgorithm()
    elif study.algorithm == "MOCMAES":
      algorithm = MocmaesAlgorithm()
    elif study.algorithm == "SkoptBayesianOptimization":
      algorithm = SkoptBayesianOptimization()
    else:
      raise ValueError('Error, Unknown algorithm: {}'.format(study.algorithm))

    new_trials = algorithm.get_new_suggestions(study.name, trials, trials_number)

    return new_trials

  def is_study_done(self, study_name):
    study = self.get_study_by_name(study_name)
    is_completed = True

    if study.status == "Completed":
      return True

    trials = self.list_trials(study_name)
    for trial in trials:
      if trial.status != "Completed":
        return False

    study.status = "Completed"

    return is_completed



  def list_trial_metrics(self, study_name, trial_id):
    """
    等价与views.py里面的 v1_study_trial_metrics
    :param study_name:
    :param trial_id:
    :return:
    """

    trial_metrics = []
    trial_metrics = TrialMetric.objects.get(name=trial_id)

    return trial_metrics

  def get_best_trial(self, study_name):
    # Can only be used when all the trials are completed
    if not self.is_study_done:
      return None

    study = self.get_study_by_name(study_name)
    study_configuration_dict = json.loads(study.study_configuration)
    study_goal = study_configuration_dict["goal"]
    trials = self.list_trials(study_name)

    best_trial = None
    best_objective_value = None

    # Get the first not null trial
    for trial in trials:
      if trial.objective_value:
        best_objective_value = trial.objective_value
        best_trial = trial
        break

    if best_trial == None:
      return None

    for trial in trials:
      if study_goal == "MAXIMIZE":
        if trial.objective_value and trial.objective_value > best_objective_value:
          best_trial = trial
          best_objective_value = trial.objective_value
      elif study_goal == "MINIMIZE":
        if trial.objective_value and trial.objective_value < best_objective_value:
          best_trial = trial
          best_objective_value = trial.objective_value
      else:
        return None

    return best_trial

  def get_trial(self, study_name, trial_id):
    """
    等价于views.py 中的v1_study_trial
    :param study_name:
    :param trial_id:
    :return:
    """
    trial = Trial.objects.get(id=trial_id)

    return trial

  def create_trial_metric(self, study_name, trial_id, training_step,
                          objective_value):
    """
    等价于views.py 中的v1_study_trial_metrics 中的POST方法
    :param study_name:
    :param trial_id:
    :param training_step:
    :param objective_value:
    :return:
    """
    trial_metric = TrialMetric.create(trial_id, training_step, objective_value)

    return trial_metric

  def complete_trial_with_tensorboard_metrics(self, trial,
                                              tensorboard_metrics):
    for tensorboard_metric in tensorboard_metrics:
      self.create_trial_metric(trial.study_name, trial.id,
                               tensorboard_metric.step,
                               tensorboard_metric.value)


    # Update the trial
    trial = Trial.objects.get(id=trial.id)
    trial.status = "Completed"
    objective_value = tensorboard_metrics[-1].value
    trial.objective_value = objective_value

    return trial

  def complete_trial_with_one_metric(self, trial, metric):
    self.create_trial_metric(trial.study_name, trial.id, None, metric)

    objective_value = metric

    # Update the trial
    trial = Trial.objects.get(id=trial.id)
    trial.status = "Completed"
    trial.objective_value = objective_value

    return trial
