import numpy as np
import os
import geopandas as gpd
import pandas as pd
import plotly.express as px
import  plotly as py
import os


path = os.path.join(os.path.dirname(os.getcwd()),  'SimulationEngine', 'ealing_buildings.csv')
df = pd.read_csv(path)
fig = px.scatter_mapbox(df, lat="y", lon="x",
                        color_discrete_sequence=px.colors.qualitative.G10,
                        color="type",
                        size_max=3,
                        hover_name='type',
                        zoom=10)
fig.update_layout(mapbox_style="open-street-map", title= "Hillsborough" + ' Location Graph', width=1000, height=800, legend=dict(x=0, y=0, orientation ="h"))
py.offline.plot(fig, filename= "LG.html")
fig.show()