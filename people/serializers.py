from rest_framework.serializers import ModelSerializer
from people.models import Person, DataSet


class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        # fields = ["data_set", "name", "height", "mass", "hair_color", "skin_color", "eye_color", "birth_year", "gender", "homeworld", "films", "species", "vehicles", "starships", "created", "edited", "url"]
        # fields = "__all__"
        exclude = ['data_set']


class DataSetSerializer(ModelSerializer):
    class Meta:
        model = DataSet
        fields = "__all__"
