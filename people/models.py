from django.db import models

from people.managers import DataSetManager, PersonManager


class DataSet(models.Model):
    objects = DataSetManager()

    name = models.CharField(max_length=128)

    @staticmethod
    def create(cls, name):
        data_set = cls(name=name)
        return data_set


class Person(models.Model):
    objects = PersonManager()

    data_set = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="person")
    date = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    height = models.CharField(max_length=128)
    mass = models.CharField(max_length=128)
    hair_color = models.CharField(max_length=128)
    skin_color = models.CharField(max_length=128)
    eye_color = models.CharField(max_length=128)
    birth_year = models.CharField(max_length=128)
    gender = models.CharField(max_length=128)
    homeworld = models.CharField(max_length=128)
