from django.http import JsonResponse, HttpResponse
import requests
from people.models import DataSet, Person
from datetime import datetime
from people.serializers import PersonSerializer
import logging


def show_dataset(request):
    return HttpResponse(content=DataSet.objects.values())


def show_dataset_details(request, data_set_id):
    return HttpResponse(content=Person.objects.filter(data_set=data_set_id).values())


def create_dataset(request):
    data_set = DataSet.objects.create_data_set(name=str(datetime.now().strftime("%d.%m.%Y, %H:%M:%S")))

    page = 1
    is_next_page = True
    while is_next_page:
        response = requests.get(f"https://swapi.dev/api/people/?page={page}")
        for person in response.json()["results"]:
            if url := person.get("homeworld"):
                homeworld_response = requests.get(url)
                person["homeworld"] = homeworld_response.json()["name"]

            if edited := person.get("edited"):
                person["date"] = edited.split("T")[0]
            else:
                person["date"] = "unknown"

            serializer = PersonSerializer(data=person)
            if serializer.is_valid() is False:
                logging.warning(f"During collecting data set for person_name: '{person['name']}' serializer return "
                                f"error: '{serializer.errors}'")
                continue

            Person.objects.create_person(data_set_id=data_set.id, **person)

        page += 1
        is_next_page = response.json()["next"]

    return HttpResponse(status=200, content="Data set is correctly created")
