# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json


class Objects():
  def __init__(self):
    self.__items = {}
    self.__id = 0
    self.__items_by_name = {}
  def add(self, item):
    assert self.__id == item.id
    self.__items[self.__id] = item
    self.__id += 1
    self.__items_by_name[item.name] = item
  def get(self, **params):
    if 'name' in params:
      return self.get_by_name(params['name'])
    if 'id' in params:
      return self.get_by_id(params['id'])
    raise ValueError
  def filter(self, **params):
    filtered_items = []
    for item in self.__items.values():
      satisfied = True
      for param in params.keys():
        item_value = getattr(item, param)
        filter_by_value = params[param]
        if filter_by_value != item_value:
          satisfied = False
          break
      if satisfied:
        filtered_items.append(item)
    return filtered_items

  def get_by_id(self, i):
    return self.__items[i]
  def get_by_name(self, name):
    return self.__items_by_name[name]
  def isin(self, key):
    return key in self.__items_by_name
  def remove_by_id(self, key):
    self.__items_by_name.pop(self.__items[key].name)
    self.__items.pop(key)
  def remove_by_name(self, key):
    self.__items.pop(self.__items_by_name[key].id)
    self.__items_by_name.pop(key)
  def list_objects(self):
    return self.__items.values()
  def len(self):
    return len(self.__items)


class Model():

  def __init__(self):
    self.name = None
    self.status = None
    self.id = None


class Study():
  # name = models.CharField(max_length=128, blank=False, unique=True)
  # study_configuration = models.TextField(blank=False)
  # algorithm = models.CharField(max_length=128, blank=False)
  #
  # status = models.CharField(max_length=128, blank=False)
  # created_time = models.DateTimeField(auto_now_add=True)
  # updated_time = models.DateTimeField(auto_now=True)

  study_id = 0
  objects = Objects()
  def __init__(self):
    super().__init__()
    self.study_configuration = None
    self.algorithm = None

  def __str__(self):
    return "{}-{}".format(self.id, self.name)

  @classmethod
  def create(cls,
             name,
             study_configuration,
             algorithm="RandomSearchAlgorithm",
             status="Pending"):
    study = cls()
    study.name = name
    study.study_configuration = json.dumps(study_configuration)
    study.algorithm = algorithm
    study.status = status
    study.id = Study.study_id
    Study.study_id += 1
    Study.objects.add(study)
    return study


  def to_json(self):
    return {
        "id": self.id,
        "name": self.name,
        "study_configuration": self.study_configuration,
        "algorithm": self.algorithm,
        "status": self.status,
        "created_time": self.created_time,
        "updated_time": self.updated_time
    }



class Trial(Model):
  # TODO: Use foreign key or not
  #study_name = models.ForeignKey(Study, related_name="trial_study", to_field=Study.name)
  # study_name = models.CharField(max_length=128, blank=False)
  # name = models.CharField(max_length=128, blank=False)
  # parameter_values = models.TextField(blank=True, null=True)
  # objective_value = models.FloatField(blank=True, null=True)
  #
  # status = models.CharField(max_length=128, blank=False)
  # created_time = models.DateTimeField(auto_now_add=True)
  # updated_time = models.DateTimeField(auto_now=True)
  trial_id = 0
  objects = Objects()

  def __str__(self):
    return "{}-{}".format(self.id, self.name)

  def __init__(self):
    super().__init__()
    self.study_name = None
    self.algorithm = None
    self.parameter_values = None
    self.objective_value = None

  @classmethod
  def create(cls, study_name, name):
    trial = cls()
    assert Study.objects.isin(study_name)
    trial.study_name = study_name
    trial.name = name
    trial.status = "Pending"
    trial.id = Trial.trial_id
    Trial.trial_id += 1
    Trial.objects.add(trial)
    return trial

  def to_json(self):
    return {
        "id": self.id,
        "study_name": self.study_name,
        "name": self.name,
        "parameter_values": self.parameter_values,
        "objective_value": self.objective_value,
        "status": self.status,
        "created_time": self.created_time,
        "updated_time": self.updated_time
    }


class TrialMetric(Model):
  # trial_id = models.IntegerField(blank=False)
  # training_step = models.IntegerField(blank=True, null=True)
  # objective_value = models.FloatField(blank=True, null=True)
  #
  # created_time = models.DateTimeField(auto_now_add=True)
  # updated_time = models.DateTimeField(auto_now=True)
  objects = Objects()
  metric_id = 0
  def __init__(self):
    self.trial_id = None
    self.training_step = None
    self.objective_value = None

  def __str__(self):
    return "Id: {}, trial id: {}, training_step: {}".format(
        self.id, self.trial_id, self.training_step)

  @classmethod
  def create(cls, trial_id, training_step, objective_value):
    trial_metric = cls()
    trial_metric.id = TrialMetric.metric_id
    TrialMetric.metric_id += 1
    trial_metric.name = trial_id
    trial_metric.training_step = training_step
    trial_metric.objective_value = objective_value
    TrialMetric.objects.add(trial_metric)
    return trial_metric

  def to_json(self):
    return {
        "id": self.id,
        "trial_id": self.trial_id,
        "training_step": self.training_step,
        "objective_value": self.objective_value,
        "created_time": self.created_time,
        "updated_time": self.updated_time
    }


class Algorithm(Model):
  # name = models.CharField(max_length=128, blank=False)
  #
  # status = models.CharField(max_length=128, blank=False)
  # created_time = models.DateTimeField(auto_now_add=True)
  # updated_time = models.DateTimeField(auto_now=True)

  algorithm_id = 0
  objects = Objects()

  def __init__(self):
    super().__init__()

  def __str__(self):
    return "{}-{}".format(self.id, self.name)

  @classmethod
  def create(cls, name):
    algorithm = cls()
    algorithm.name = name
    algorithm.status = "AVAIABLE"
    algorithm.id = Algorithm.algorithm_id
    Algorithm.algorithm_id += 1
    Algorithm.objects.add(algorithm)
    return algorithm

  def to_json(self):
    return {"name": self.name}


if __name__ == '__main__':
  a = Algorithm.create('bayes')
  s = Study.create('st', 'the configuration of study')
  t = Trial.create('st', 'trial')
  t2 = Trial.create('st', 'trial2')
  s2 = Study.create('sss', 'the configuration of study')
  t3 = Trial.create('sss', 'trial')
  print(Trial.objects.filter(study_name='sss')[0])