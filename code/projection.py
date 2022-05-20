from dataclasses import dataclass
from map import Map
from typing import Optional
import contextily as cx
import geopandas

@dataclass
class Projection:
    maps: list[Map]
    size: tuple[int, int]
    source: Optional[object] = None
    backgroundMap: bool = False
    def __post_init__(self):
        if self.source:
            assert backgroundMap

        self.xs = []
        self.ys = []
        for map in self.maps:
            self.xs.append(map.maxX)
            self.xs.append(map.minX)
            self.ys.append(map.maxY)
            self.ys.append(map.minY)
        self.maxX = max(self.xs)
        self.minX = min(self.xs)
        self.maxY = max(self.ys)
        self.minY = min(self.ys)

        for oneMap in self.maps:
            oneMap.zoomData = oneMap.data.cx[
                self.minY: self.maxY,
                self.minX: self.maxX]




    def draw(self, outfileName: str):
        ax = None
        axlist = []
        for i in range(len(self.maps)):
            oneMap = self.maps[i]
            if i == 0:
                base = oneMap.data.plot(facecolor=oneMap.facecolor,
                                         edgecolor=oneMap.edgecolor,
                                         figsize=self.size,
                                         alpha=oneMap.alpha,
                                         column=oneMap.selectedColumn,
                                         legend = True if i == len(self.maps) - 1 else False,
            )
                print(f"the base is: {base}")
                axlist.append(base)
            else:
                ax = oneMap.data.plot(ax = axlist[i-1],
                                 facecolor=oneMap.facecolor,
                                   edgecolor=oneMap.edgecolor,
                                   figsize=self.size,
                                   alpha=oneMap.alpha,
                                   column=oneMap.selectedColumn,
                                   legend=oneMap.legend,
                                       )
                print(f"the {i}th axis is: {ax}")
                axlist.append(ax)
            if i == len(self.maps) - 1:
                ax.set_axis_off()
                if self.backgroundMap:
                    newBase = cx.add_basemap(ax=ax)
                    print(newBase, type(newBase))
                    newBase.figure.savefig(outfileName)
                else:
                    ax.figure.savefig(outfileName)


