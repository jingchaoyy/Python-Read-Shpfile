from Tkinter import *
import struct

# define point, polyline classes
class Point:
    # deinfe object initialization method
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Polyline:
    # deinfe object initialization method
    def __init__(self, points=[], partsNum=0, partsIndex=0):
        self.points = points
        self.partsNum = partsNum
        self.partsIndex = partsIndex

# open index file to read in binary mode
shxFile = open('/Users/YJccccc/Desktop/GGS_650_Python/FinalProject/Neighborhood_Clusters/Neighborhood_Clusters.shx', 'rb')

# ----Part 1: read and process the first 100 bytes
# read index file header and interpret the meta information. e.g., bounding box, and # of #records
s = shxFile.read(28)  # read first 28 bytes
# convert into 7 integers

# get file length
header = struct.unpack('>iiiiiii', s)
fileLength = header[len(header) - 1]

# calcualate polyline numbers in the shape file based on index file length
polylineNum = int((fileLength * 2 - 100) / 8)

# read other 72 bytes in header
s = shxFile.read(72)
# convert into values
header = struct.unpack('<iidddddddd', s)
# get boundingbox for the shape file
minX, minY, maxX, maxY = header[2], header[3], header[4], header[5]

# read records meta information, such as offset,
# and content length for each records,

# define an empty list for holding offset of each feature in main file
recordsOffset = []
# loop through each feature
for i in range(polylineNum):
    # jump to beginning of each record
    shxFile.seek(100 + i * 8)
    # read out 4 bytes as offset
    s = shxFile.read(4)
    offset = struct.unpack('>i', s)
    # keep the offset in the list
    recordsOffset.append(offset[0] * 2)

shxFile.close()  # close the index file


# ----Part2. read each polyline and prepare them in right order
# open the main file for read in binary
shpFile = open('/Users/YJccccc/Desktop/GGS_650_Python/FinalProject/Neighborhood_Clusters/Neighborhood_Clusters.shp', 'rb')
# shapefile name can be replaced with any polyline

polylines = []  # define an empty list for polylines

# loop through each offset of all polylines
for offset in recordsOffset:
    # define two lists for holding values
    x, y = [], []
    # jump to partsNum and pointsNum of the polyline and read them out
    shpFile.seek(offset + 8 + 36)
    s = shpFile.read(8)
    polyline = Polyline()  # generate an empty polyline object
    partsNum, pointsNum = struct.unpack('ii', s)
    polyline.partsNum = partsNum
    #print ('partsNum, pointsNum:', partsNum, pointsNum)
    s = shpFile.read(4 * partsNum)
    str = ''
    for i in range(partsNum):
        str = str + 'i'

    # get the starting point number of each part and keep in a partsIndex list
    polyline.partsIndex = struct.unpack(str, s)

    points = []
    for i in range(pointsNum):
        # read out polyline coordinates
        s = shpFile.read(16)
        x, y = struct.unpack('dd', s)

        # read the coordinates values
        # assemble data into objects of points, polyline, and polygon or other types
        point = Point(x, y)
        points.append(point)
    # assign points lists to the polyline
    polyline.points = points
    # add the polyline read to the
    polylines.append(polyline)


# ----Part 3: prepare to visualize the data
# create main window object
root = Tk()

# define wondow size
windowWidth, windowHeight = 600, 600

# calculate ratio for visualization
ratiox = (maxX - minX) / windowWidth
ratioy = (maxY - minY) / windowHeight

# take the smaller ratio
ratio = ratiox
if ratio < ratioy:
    ratio = ratioy

# create canvas object
can = Canvas(root, width=600, height=600)

for polyline in polylines:
    xylist = []  # define an empty xylist for holding converted coordinates

    # loop through each point
    # and calculate the window coordinates, put in xylist
    for point in polyline.points:
        #print (point.x, point.y)
        winX = (point.x - minX) / ratio
        winY = - (point.y - maxY) / ratio
        xylist.append(winX)
        xylist.append(winY)
    #print "xylist: ",xylist

    for k in range(polyline.partsNum):  # visualize each part separately
        if (k == polyline.partsNum - 1):
            endPointIndex = len(polyline.points)
        else:
            endPointIndex = polyline.partsIndex[k + 1]

        # define a temporary list for holding the part coordinates
        tempXYlist = []

        for m in range(polyline.partsIndex[k], endPointIndex):
            # polyline.partsIndex[k]:the first point in this part
            # endPointIndex:the last point in this part
            tempXYlist.append(xylist[(m * 2)])
            tempXYlist.append(xylist[(m * 2 + 1)])
        #print "tempXYList: ",tempXYlist

        # create the line
        can.create_line(tempXYlist, fill='blue')

can.pack()
root.mainloop()

shpFile.close()
