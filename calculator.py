import csv
import ast
import pdb
import sys
import math
import pandas as pd
import matplotlib.pyplot as plt

def load_data(dPath):
    buildings = pd.DataFrame(columns=['BuildingId', 'BuildingName', 'AgeClass', 'Height', 'Flats', 'TypeBuilding', 'Footprint', 'HeatNetworkConnected'])
    buildings.set_index('BuildingId', inplace=True)

    with open(dPath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                building_id = int(row["BuildingId"])
            except ValueError:
                print('Skipping building {}'.format(row["BuildingId"]))
                continue
            if row["AgeClass"] == "-1":
                print('Skipping building {} due to invalid age class, unknown age class'.format(row['BuildingId']))
                continue
            if row["Footprint"].startswith("[[["):
                print('Skipping building {} due to invalid footprint, footprint is not a polygon'.format(row['BuildingId']))
                continue
            building_name = row["BuildingName"]
            age_class = row["AgeClass"]
            height = float(row["Height"])
            flats = int(row["Flats"])
            type_building = row["TypeBuilding"]
            footprint = ast.literal_eval(row["Footprint"])
            heat_network_connected = int(row["HeatNetworkConnected"])
            
            buildings.loc[building_id] = [building_name, age_class, height, flats, type_building, footprint, heat_network_connected]
    return buildings

def get_wall_length(building_footprint=None):
    """ For a given, correct, building footprint calculates it's total wall length and returns float"""
    length = 0
    for i, point in enumerate(building_footprint):
        x0 = building_footprint[i][0]
        y0 = building_footprint[i][1]
        print('Current footprint: x: {}, y: {}'.format(x0,y0))
        try:
            x1 = building_footprint[i+1][0]
            y1 = building_footprint[i+1][1]
        except IndexError:
            x1 = building_footprint[0][0]
            y1 = building_footprint[0][1]
        partialLength = math.sqrt((x1-x0)**2+(y1-y0)**2)
        length += partialLength
    return length

def get_building_area(building_data):
    building_type = building_data['TypeBuilding']
    age_class = building_data['AgeClass']
    wall_length = get_wall_length(building_data['Footprint'])
    wall_area = wall_length * building_data['Height']

def get_u_values(data_folder = None,
                file_names = ['UValuesFloor', 'UValuesRoof', 'UValuesWall', 'UValuesWindow'],
                filetype='csv'):
    """ Reads u values from multiple files and concatenates into a single pandas dataframe indexed with supplied index """
    u_values = dict()
    ageClasses = ['1','2','3','4','5','6','7','8','9']
    buildingTypes = ['BMFH', 'SFH', 'SMFH', 'AB']
    surfaces = ['Floor','Window','Wall','Roof']
    surfaceDict = {'UValuesFloor' :'Floor', 'UValuesRoof': 'Roof', 'UValuesWall': 'Wall', 'UValuesWindow': 'Window'}

    propertyDict = dict()
    for ageClass in ageClasses:
        propertyDict[ageClass] = dict()
        for surface in surfaces:
            propertyDict[ageClass][surface] = None

    for buildingType in buildingTypes:
        u_values[buildingType] = propertyDict.copy()

    for fileName in file_names:
        with open('{}/{}.{}'.format(data_folder, fileName, filetype)) as f:
            reader = csv.DictReader(f)
            for row in reader:
                for buildingType in buildingTypes:
                    u_values[buildingType][row['AgeClass']][surfaceDict[fileName]] = row[buildingType]
    # Returns u_values with shape u_values['BuildingType']['AgeClass']['Surface']
    return u_values

def make_solution_span(floor, ceiling, slices):
    """Creates a list of tuples containing minimum and maximum values for each section
    in a uniformly sliced range between ceiling and floor
    """
    spans = list()
    delta = (ceiling-floor)/slices
    for i in range(slices):
        spans.append((i*delta, (i+1)*delta))
    return spans

def plot_buildings(buildings):
    for footprint in buildings['Footprint']:
        x_house = list()
        y_house = list()

        for edge in footprint:
            #print(edge)
            x_house.append(edge[0])
            y_house.append(edge[1])
        plt.plot(x_house, y_house)
    plt.show()
    return None

def main(load_buildings = False, plot_buildings = False):
    u_values = get_u_values(data_folder='C:/Users/AlexanderKa/Desktop/Sinfonia Local/InvFront/BolzanoData')

    if load_buildings:
        buildings = load_data("BolzanoData/Building_0.csv".format(i)
        for i in range(1,12):
            temp = load_data("BolzanoData/Building_{}.csv".format(i))    
            buildings = pd.concat([buildings, temp)

    if plot_buildings:
        plot_buildings(buildings)
    
    return None
            

if __name__ == "__main__":
    main()
    window_ratio = {'SFH': 0.08,
                    'SMFH': 0.1,
                    'BMFH': 0.11,
                    'AB': 0.12
                    }
   
