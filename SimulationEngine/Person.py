import datetime
from dateutil.relativedelta import relativedelta
import json
import datetime as dt
import pandas as pd
import os
import random
import pyproj

from mesa_geo import GeoAgent
from shapely.geometry import Point

class Person(GeoAgent):
    """Person Agent."""

    def __init__(
        self,
        unique_id,
        age,
        gender,
        race,
        model,
        shape
    ):
        """
        Create a new person agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param shape:       Shape object for the agent
        """
        super().__init__(unique_id, model, shape)
        # Agent parameters
        self.age=age
        self.gender=gender
        self.race=race
        self.homex = shape.x
        self.homey = shape.y


        if self.randomTrue(0.1):
            self.state = "exposed"
            self.model.counts["exposed"] += 1  # Adjust initial counts
            self.model.counts["susceptible"] -= 1

        else:
            self.state = "susceptible"

        self.init_infected = 0.05
        self.moving = True

        #Risk Probabilities
        self.recovery_rate = 0.2
        self.visit_count = 0

        self.infection_risk = 0.5
        self.prob_asymptomatic = 0.5
        self.hospitalization_risk = 0.1624
        self.ICU_risk = 0.2527
        self.death_risk = 0.95

        #Phases
        self.exposed_to_presymptomatic = 6 #days
        self.presymptomatic_to_mild = 4
        self.mild_to_severe = 7
        self.severe_to_critical = 7
        self.critical_to_recovery = 8
        self.phase_count = 0

    def print(self):
        print(self.unique_id,  self.age, self.gender, self.race,  self.state, self.shape.x, self.shape.y)


    def randomTrue(self, prob):
        r = random.uniform(0, 1)
        if r < prob:
            return True
        else:
            return False

    def step(self):
        if self.state == "susceptible":
            # check neigbours for exposure
            neighbors = self.model.grid.get_neighbors_within_distance(self, self.model.exposure_distance)
            for neighbor in neighbors:
                if (neighbor.state == "exposed" or neighbor.state=="asymptomatic" or neighbor.state== "mild" or neighbor.state=="severe" or neighbor.state=="critical"):
                    if self.randomTrue(self.infection_risk):
                        if (self.randomTrue(0.5)):
                            self.state = "exposed"
                            self.moving = True
                            break
            # self.move()

        elif self.state == "exposed":
            self.phase_count += 1
            if (self.phase_count > self.exposed_to_presymptomatic):
                self.phase_count = 0
                if self.randomTrue(self.prob_asymptomatic):
                    self.state = "asymptomatic"
                    self.moving = True
                else:
                    self.state = "mild"
                    self.moving = True

        elif self.state == "mild":
            self.phase_count += 1
            if (self.phase_count > self.mild_to_severe):
                self.phase_count = 0
                if self.randomTrue(self.hospitalization_risk):
                    self.state = "severe"
                    self.moving = False
                else:
                    self.state = "recovered"
                    self.moving = True

        elif self.state == "severe":
            self.phase_count += 1
            if (self.phase_count > self.severe_to_critical):
                self.phase_count = 0
                if self.randomTrue(self.ICU_risk):
                    self.state = "critical"
                    self.moving=False
                else:
                    self.state = "recovered"
                    self.moving = True


        elif self.state == "critical":
            self.phase_count += 1
            if (self.phase_count > self.critical_to_recovery):
                self.phase_count = 0
                if self.randomTrue(self.death_risk):
                    self.state = "dead"
                    self.moving = False
                else:
                    self.state = "recovered"
                    self.moving = True

        elif (self.state != "severe") and (self.state != "critical")  and (self.state != "dead"):
            if self.moving:
                if self.model.steps % 2 == 0:
                    self.shape = Point(self.homex, self.homey)
                else:
                    loc = random.choice(self.model.places)
                    # self.shape = Point(loc[0], loc[1])
                    self.shape = Point(self.model.MAP_COORDS[0],self.model.MAP_COORDS[1])

        self.model.counts[self.state] += 1  # Count agent type