import csv
import logging
from datetime import datetime

import requests
from django.http import HttpResponse, QueryDict
from django.shortcuts import render

from people.models import DataSet, Person
from people.serializers import PersonSerializer


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
    data_set = DataSet.objects.create_data_set(name=str(datetime.now().strftime("%d.%m.%Y, %H:%M:%S")))

    page = 1
    is_next_page = True
    homeworld_dictionary = {}
    while is_next_page:
        response = requests.get(f"https://swapi.dev/api/people/?page={page}")
        for person in response.json()["results"]:

            if homeworld_url := person.get("homeworld"):
                if homweworld_name := homeworld_dictionary.get(homeworld_url):
                    person["homeworld"] = homweworld_name
                else:
                    homeworld_response = requests.get(homeworld_url)
                    homweworld_name = homeworld_response.json()["name"]
                    person["homeworld"] = homweworld_name
                    homeworld_dictionary[homeworld_url] = homweworld_name

            if edited := person.get("edited"):
                person["date"] = edited.split("T")[0]
            else:
                person["date"] = "unknown"

            serializer = PersonSerializer(data=person)
            if serializer.is_valid() is False:
                logging.warning(
                    f"During collecting data set for person_name: '{person['name']}' serializer return "
                    f"error: '{serializer.errors}'"
                )
                continue
            Person.objects.create_person(data_set_id=data_set.id, **serializer.data)

        page += 1
        is_next_page = response.json()["next"]

    return render(
        request,
        "create_dataset.html",
        context={"data_set": data_set},
    )


def count(request, data_set_id):
    person_key = [field.name for field in Person._meta.get_fields()]
    query = QueryDict(request.META["QUERY_STRING"])

    if categories := query.getlist("categories"):
        if len(categories) != 2:
            return HttpResponse(status=400, content="Only two values are accepted!")
        if not all(x in person_key for x in categories):
            return HttpResponse(status=400, content="Bad categories!")

        persons = list(Person.objects.filter(data_set=data_set_id).values())
        first_category_values_set = set()
        second_category_values_set = set()

        for person in persons:
            if person[categories[0]] != "unknown":
                first_category_values_set.add(person[categories[0]])
            if person[categories[1]] != "unknown":
                second_category_values_set.add(person[categories[1]])

        count_list = []
        for first_value in first_category_values_set:
            for second_value in second_category_values_set:
                result = list(
                    Person.objects.filter(data_set=data_set_id)
                    .filter(**{categories[0]: first_value})
                    .filter(**{categories[1]: second_value})
                    .values()
                )
                if result:
                    count_list.append({categories[0]: first_value, categories[1]: second_value, "count": len(result)})
        return render(
            request,
            "count.html",
            context={"data_set_id": data_set_id, "person_key": person_key, "count_list": count_list},
        )

    return render(request, "count.html", context={"data_set_id": data_set_id, "person_key": person_key})
