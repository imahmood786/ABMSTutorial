from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from model import InfectedModel, Person
from mesa_geo.visualization.MapModule import MapModule


class InfectedText(TextElement):
    """
    Display a text count of how many steps have been taken
    """
    def __init__(self):
        pass

    def render(self, model):
        return "Days: " + str(model.currentdate)

def infected_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, Person):
        portrayal["radius"] = "1"
    if agent.state in ["susceptible"]:
        portrayal["color"] = "Blue"
    elif agent.state in ["exposed"]:
        portrayal["color"] = "Orange"
    elif agent.state in ["asymptomatic"]:
        portrayal["color"] = "Purple"
    elif agent.state in ["mild"]:
        portrayal["color"] = "Red"
    elif agent.state in ["severe"]:
        portrayal["color"] = "Darkred"
    elif agent.state in ["critical"]:
        portrayal["color"] = "Darkgrey"
    elif agent.state in ["recovered"]:
        portrayal["color"] = "Green"
    elif agent.state in ["dead"]:
        portrayal["color"] = "Black"
    return portrayal


infected_text = InfectedText()
map_element = MapModule(infected_draw, InfectedModel.MAP_COORDS, 10, 800, 1450)
infected_chart = ChartModule(
    [
        {"Label": "susceptible", "Color": "Blue"},
        {"Label": "exposed", "Color": "Orange"},
        {"Label": "asymptomatic", "Color": "Purple"},
        {"Label": "mild", "Color": "Red"},
        {"Label": "severe", "Color": "Darkred"},
        {"Label": "critical", "Color": "Darkgrey"},
        {"Label": "recovered", "Color": "Green"},
        {"Label": "dead", "Color": "Black"}
    ]
)

server = ModularServer(
    InfectedModel,
    [map_element, infected_text, infected_chart],
    # [infected_text],
    "SEIR Cast Spatial ABM Simulator",
    # model_params,
)

server.launch()
