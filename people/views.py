import csv
import logging
from datetime import datetime

import requests
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from petl import fromdicts, valuecounter
from django.core.exceptions import ObjectDoesNotExist

from people.models import DataSet, Person, Planet
from people.serializers import PersonSerializer, PlanetSerializer


def people_home_page(request):
    return render(request, "home.html")


def show_dataset(request):
    dataset_list = list(DataSet.objects.values())
    return render(request, "show_dataset.html", context={"dataset_list": dataset_list})


def show_dataset_details(request, data_set_id):
    person_list = list(Person.objects.filter(data_set=data_set_id).values())
    query = QueryDict(request.META["QUERY_STRING"])
    if limit := query.get("limit"):
        person_list = person_list[0: int(limit)]
    else:
        limit = None
    return render(
        request,
        "show_dataset_details.html",
        context={"person_list": person_list, "data_set_id": data_set_id, "limit": limit},
    )


def download_dataset(request, data_set_id):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=data_set_{data_set_id}.csv"},
    )

    writer = csv.writer(response)
    person_list = list(Person.objects.filter(data_set=data_set_id).values())
    writer.writerow(person_list[0].keys())
    for person in person_list:
        writer.writerow(list(person.values()))
    return response


def create_dataset(request):
    data_set = DataSet.objects.create(name=str(datetime.now().strftime("%d.%m.%Y, %H:%M:%S")))

    page = 1
    is_next_page = True
    while is_next_page:
        response = requests.get(f"https://swapi.dev/api/people/?page={page}")
        for person in response.json()["results"]:

            if homeworld_url := person.get("homeworld"):
                try:
                    person["homeworld"] = Planet.objects.get(url=homeworld_url).name
                except ObjectDoesNotExist:
                    homeworld_response = requests.get(homeworld_url).json()
                    person["homeworld"] = homeworld_response["name"]
                    serializer = PlanetSerializer(data=homeworld_response)
                    if serializer.is_valid():
                        Planet.objects.create(**serializer.data)
                    else:
                        logging.warning(
                            f"During collecting data set for planet_url '{homeworld_url}' serializer return "
                            f"error: '{serializer.errors}'"
                        )

            if edited := person.get("edited"):
                person["date"] = edited.split("T")[0]
            else:
                person["date"] = "unknown"

            serializer = PersonSerializer(data=person)
            if serializer.is_valid():
                Person.objects.create(data_set_id=data_set.id, **serializer.data)
            else:
                logging.warning(
                    f"During collecting data set for person_name: '{person['name']}' serializer return "
                    f"error: '{serializer.errors}'"
                )
                continue

        page += 1
        is_next_page = response.json()["next"]

    return render(
        request,
        "create_dataset.html",
        context={"data_set": data_set},
    )


def count(request, data_set_id):
    person_key = [field.name for field in Person._meta.get_fields() if field.name not in ["id", "data_set"]]
    query = QueryDict(request.META["QUERY_STRING"])

    if categories := query.getlist("categories"):
        if len(categories) < 2:
            return HttpResponse(status=400, content="At least two values are required!")
        if not all(category in person_key for category in categories):
            return HttpResponse(status=400, content="Bad categories!")

        persons = list(Person.objects.filter(data_set=data_set_id).values())
        petl_table = fromdicts(persons)
        count_dict = dict(valuecounter(petl_table, *categories))

        delete = [key for key in count_dict if "unknown" in key]
        for key in delete:
            del count_dict[key]

        return render(
            request,
            "count.html",
            context={
                "person_key": person_key,
                "count_dict": count_dict,
                "categories": categories,
            },
        )

    return render(request, "count.html", context={"person_key": person_key})
