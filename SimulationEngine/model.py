from datetime import datetime, date, timedelta, time
from dateutil.parser import parse
import random
from mesa.datacollection import DataCollector
from mesa import Model
from mesa.time import BaseScheduler
from pandas.core.common import flatten
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
from shapely.geometry import Point, mapping, shape
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import json
from pyproj import Transformer
from SimulationEngine.Person import Person

class InfectedModel(Model):

    # Geographical parameters for desired map
    MAP_COORDS = [51.53156765, -0.26761192]  # Tampa

    def __init__(self):
        self.schedule = BaseScheduler(self)
        self.grid = GeoSpace()
        self.steps = 0
        self.startdate = date(2020, 3, 1)
        self.currentdate = self.startdate
        self.enddate = date(2020, 4, 1)
        self.exposure_distance = 800
        self.counts = None
        self.reset_counts()

        # load csv files
        self.buildings = gpd.read_file(os.path.join(os.path.dirname(os.getcwd()),
                                                    'SimulationEngine', 'ealing_buildings.geojson'))
        self.buildings = self.buildings.sample(n=500)
        self.buildings['x'] = self.buildings['geometry'].centroid.x
        self.buildings['y'] = self.buildings['geometry'].centroid.y
        self.houses = self.buildings.loc[self.buildings['type']=='house']
        locations = self.buildings.loc[(self.buildings['type'] != 'house')]
        self.places = []
        for index, row in locations.iterrows():
            self.places.append((row['x'], row['y']))


        # Generate PersonAgent population
        AC = AgentCreator(
            Person, {"model": self}
        )

        #initialization
        pid = 0
        gender = ['male', 'female']
        race = ['white', 'black', 'native', 'asian', 'islander', 'other', 'two']
        for index, row in self.houses.iterrows():
            for occupant in range(0,random.randint(0,5)):
                pid+=1
                house_coord = row['geometry'].centroid
                this_person = AC.create_person(pid,
                                               random.randint(1,80),
                                               random.choice(gender),
                                               random.choice(race),
                                               house_coord)

                self.grid.add_agents(this_person)
                self.schedule.add(this_person)

        print('Population loaded!')
        print(pid)
        self.counts["susceptible"] = pid
        self.datacollector = DataCollector({
                "susceptible": get_susceptible_count,
                "exposed": get_exposed_count,
                "asymptomatic": get_asymptomatic_count,
                "mild": get_mild_count,
                "severe": get_severe_count,
                "critical": get_critical_count,
                "recovered": get_recovered_count,
                "dead": get_dead_count,
                "vaccinated": get_vaccinated_count
        })
        self.datacollector.collect(self)
        self.running = True


    def step(self):
        """Run one step of the model."""
        self.steps += 1
        self.reset_counts()
        self.schedule.step()
        self.grid._recreate_rtree()  # Recalculate spatial tree, because agents are moving
        self.datacollector.collect(self)
        self.currentdate = self.startdate + timedelta(days=self.steps)
        if self.currentdate >= self.enddate:
            self.running = False
            # df = self.datacollector.get_model_vars_dataframe()
            # df.to_csv(os.path.join(os.path.dirname(os.getcwd()), 'ABMSimulator', 'SimulationEngine', 'output', 'output.csv'), index=False)
            print('Simulation stopped!')

    def reset_counts(self):
        self.counts = {
            "susceptible": 0,
            "exposed": 0,
            "asymptomatic": 0,
            "mild": 0,
            "severe": 0,
            "critical": 0,
            "recovered": 0,
            "dead": 0,
            "vaccinated": 0,
        }

# Functions needed for datacollector
def get_susceptible_count(model):
    return model.counts["susceptible"]
def get_exposed_count(model):
    return model.counts["exposed"]
def get_asymptomatic_count(model):
    return model.counts["asymptomatic"]
def get_mild_count(model):
    return model.counts["mild"]
def get_severe_count(model):
    return model.counts["severe"]
def get_critical_count(model):
    return model.counts["critical"]
def get_recovered_count(model):
    return model.counts["recovered"]
def get_dead_count(model):
    return model.counts["dead"]
def get_vaccinated_count(model):
    return model.counts["vaccinated"]

if __name__ == '__main__':
    InfectedModel = InfectedModel()