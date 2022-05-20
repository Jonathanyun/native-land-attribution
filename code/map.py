import geopandas
from dataclasses import dataclass



@dataclass
class Map():
     data: geopandas.geodataframe.GeoDataFrame
     selectedColumn: str = None
     facecolor: str = "none"
     edgecolor: str = "k"
     alpha: float = 1
     legend: bool = False

     def __post_init__(self):

         # convert to shared coordinate format
         self.data = self.data.to_crs(epsg=3857)
         # get coordinate window values
         self.xs = self.data["geometry"].apply(lambda x: x.bounds[1])
         self.ys = self.data["geometry"].apply(lambda x: x.bounds[0])
         self.maxX = self.xs.max()
         self.minX = self.xs.min()
         self.maxY = self.ys.max()
         self.minY = self.ys.min()







