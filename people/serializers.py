from rest_framework.serializers import ModelSerializer

from people.models import DataSet, Person, Planet


class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        exclude = ["data_set"]


class DataSetSerializer(ModelSerializer):
    class Meta:
        model = DataSet
        fields = "__all__"


class PlanetSerializer(ModelSerializer):
    class Meta:
        model = Planet
        fields = "__all__"
