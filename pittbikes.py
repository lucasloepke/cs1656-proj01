import argparse
import collections
import csv
import json
import glob
import math
import os
import re
import requests
import string
import sys
import time
import xml
import ssl

class Bike():
    def __init__(self, baseURL, station_info, station_status):
        self.baseURL = baseURL
        self.station_info_name = station_info
        self.station_status_name = station_status

        info_url = baseURL + "/" + station_info
        status_url = baseURL + "/" + station_status

        self.station_info = requests.get(info_url).json()
        self.station_status = requests.get(status_url).json()

        self.info_by_id = {}
        for s in self.station_info["data"]["stations"]:
            self.info_by_id[s["station_id"]] = s

        self.status_by_id = {}
        for s in self.station_status["data"]["stations"]:
            self.status_by_id[s["station_id"]] = s

    def total_bikes(self):
        total = 0
        for station in self.station_status["data"]["stations"]:
            total += station.get("num_bikes_available", 0)
        return total

    def total_docks(self):
        total = 0
        for station in self.station_status["data"]["stations"]:
            total += station.get("num_docks_available", 0)
        return total

    def percent_avail(self, station_id):
        station = self.status_by_id.get(station_id)
        if station is None:
            return ""

        bikes = station.get("num_bikes_available", 0)
        docks = station.get("num_docks_available", 0)
        total = bikes + docks
        if total == 0:
            return "0%"

        percentage = math.floor((docks / total) * 100)
        return str(percentage) + "%"

    def closest_stations(self, latitude, longitude):
        distances = []

        for station_id, info in self.info_by_id.items():
            lat = info.get("lat")
            lon = info.get("lon")
            if lat is None or lon is None:
                continue

            d = self.distance(latitude, longitude, lat, lon)
            distances.append((d, str(station_id), info.get("name", "")))

        distances.sort(key=lambda x: x[0])

        result = {}
        for _, station_id, name in distances[:3]:
            result[station_id] = name
        return result


    def closest_bike(self, latitude, longitude):
        candidates = []

        for station_id, status in self.status_by_id.items():
            if status.get("num_bikes_available", 0) <= 0:
                continue

            info = self.info_by_id.get(station_id)
            if info is None:
                continue

            lat = info.get("lat")
            lon = info.get("lon")
            if lat is None or lon is None:
                continue

            dist = self.distance(latitude, longitude, lat, lon)
            candidates.append((dist, str(station_id), info.get("name", "")))

        if not candidates:
            return {}

        candidates.sort(key=lambda x: x[0])
        _, station_id, name = candidates[0]
        return {station_id: name}
        
    def station_bike_avail(self, latitude, longitude):
        for station_id, info in self.info_by_id.items():
            lat = info.get("lat")
            lon = info.get("lon")
            if lat is None or lon is None:
                continue

            if float(lat) == float(latitude) and float(lon) == float(longitude):
                status = self.status_by_id.get(station_id)
                if status is None:
                    return {}
                return {str(station_id): int(status.get("num_bikes_available", 0))}

        return {}
        

    def distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p)) / 2
        return 12742 * math.asin(math.sqrt(a))


# testing and debugging the Bike class

if __name__ == '__main__':
    instance = Bike('http://labrinidis.cs.pitt.edu/cs1656/data', 'station_information.json', 'station_status.json')
    print('------------------total_bikes()-------------------')
    t_bikes = instance.total_bikes()
    print(type(t_bikes))
    print(t_bikes)
    print()

    print('------------------total_docks()-------------------')
    t_docks = instance.total_docks()
    print(type(t_docks))
    print(t_docks)
    print()

    print('-----------------percent_avail()------------------')
    p_avail = instance.percent_avail(342885) # replace with station ID
    print(type(p_avail))
    print(p_avail)
    print()

    print('----------------closest_stations()----------------')
    c_stations = instance.closest_stations(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_stations))
    print(c_stations)
    print()

    print('-----------------closest_bike()-------------------')
    c_bike = instance.closest_bike(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_bike))
    print(c_bike)
    print()

    print('---------------station_bike_avail()---------------')
    s_bike_avail = instance.station_bike_avail(40.445834, -79.954707) # replace with exact latitude and longitude of station
    print(type(s_bike_avail))
    print(s_bike_avail)
