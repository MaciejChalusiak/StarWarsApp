from django.db import models


class DataSetManager(models.Manager):
    def create_data_set(self, name):
        data_set = self.create(name=name)
        return data_set


class PersonManager(models.Manager):
    def create_person(self, **kwargs):
        data_set = self.create(**kwargs)
        return data_set
