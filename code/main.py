import requests
import json
import geopandas
from map import Map
from projection import Projection

#Get Native Territory data
r = requests.get("https://native-land.ca/api/index.php?maps=territories")
response = r.json()
geoJSON = {
 "type": "FeatureCollection",
 "features": response
}
nativeData = geopandas.read_file(json.dumps(geoJSON))

#Reformat
nativeData["NameStr"] = nativeData["Name"].astype(str)

nativeMap = Map(nativeData, selectedColumn="NameStr")
laMap = Map(data = geopandas.read_file("../dat/City_Boundaries.geojson"),
            alpha = 0.3,
            edgecolor = "black")
maplist = [nativeMap, laMap]

finalMap = Projection(maps=maplist,
                      backgroundMap=True,
                      size=(10, 15),
                      )
finalMap.draw("finalMap.jpg")