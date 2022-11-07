from rest_framework.serializers import ModelSerializer

from people.models import DataSet, Person


class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        exclude = ["data_set"]


class DataSetSerializer(ModelSerializer):
    class Meta:
        model = DataSet
        fields = "__all__"
