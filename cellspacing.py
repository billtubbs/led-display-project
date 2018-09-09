#!/usr/bin/env python
""" Algorithm to produce evenly-spaced cells on a flat plane
to develop a simulated topography of receptor distribution
Using graphics.py, numpy, scipy libraries
http://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf
Bill Tubbs, December 2014."""

import sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import KDTree
import graphics as gr
import datetime
import socket
from random import shuffle

# Home made module that contains all the important
# 'constants' for algorithm optimisation
from globals import *

# File globals.py should contain initialisation of the
# following global variables:
# spacingDisorderIndex
# desiredCellSpacing
# densityDeviationIndex
# numNeighbours
# width
# height
# cell_radius
# numCells
# maxIterations
# loopTimes
# costGoal
# gridSpacing
# logFilename


class CellArray:
    """CellArray class"""

    # Initialise cell array instance with the following:
    #  n: number of cells
    #  w: width dimension (units are arbitrary)
    #  h: height dimension (")
    #  r: average radius of cells
    # gs: grid spacing for cell density calculations
    # nn: number of neighbours to include in cell cost
    #     function calculations
    def __init__(self, n, w, h, r, gs, nn):
        """Initialize cell array instance."""

        self.numCells = n
        self.width = w
        self.height = h
        self.avgRadius = r
        self.radiusDistIndex = gbl.radiusDistIndex
        self.radiiVec = np.random.normal(r, self.radiusDistIndex*r, n)
        self.centresVec = np.zeros((n*2))
        self.gradientsVec = np.zeros((n*2))
        self.numNeighbours = nn

        # Not sure if its necessary to initialise these pointers
        # here as they will be assigned to data by functions later
        self.KDTree = None
        self.nearestNeighboursVec = np.zeros((n, nn))
        self.nearestNeighbourDistanceVec = np.zeros((n, nn))
        self.nearestNeighbourGapVec = np.zeros((n, nn))

        # The following matrix is used by functions such as errorFunction
        # to keep x, y co-ordinates (self.centresVec) within the cell array
        # area defined by w, h
        # Only needs calculating once therefore do it at initialisation
        self.m = np.concatenate((np.repeat(w, n), np.repeat(h, n)))

        # set up a regular grid to be used for cell density
        # calculation
        self.gridSpacing = gs
        self.gridPoints = self.sequenceOfXYRegularGrid(self.gridSpacing)

        # Set radius of the circular area around each grid point to
        # ensure that all space is covered (circle edges touch when
        # self.areaRadiusFactor = 0.5*np.sqrt(2.0)
        self.areaRadiusFactor = 0.70710678118654757

        # Note: for good results ensure that grid spacing is large enough
        # ensure that:
        # gridSpacing * areaRadiusFactor > n * cellRadius
        # where n is at least 2

        self.cellDensitiesAtGridPoints = np.zeros((w/gs, h/gs))

    def addCell(self):
        """Function to add one new cell"""
        newPoint = self.findLowDensityPoint()
        self.centresVec = np.append(np.insert(self.centresVec, self.numCells, \
                            newPoint[0]), newPoint[1])
        self.radiiVec = np.append(self.radiiVec, np.random.normal(self.avgRadius, \
                            self.radiusDistIndex*self.avgRadius, 1))
        self.nearestNeighboursVec = np.append(self.nearestNeighboursVec, \
                            np.zeros(self.numNeighbours))
        self.nearestNeighbourDistanceVec = np.append(self.nearestNeighbourDistanceVec, \
                            np.zeros(self.numNeighbours))
        self.nearestNeighbourGapVec = np.append(self.nearestNeighbourGapVec, \
                            np.zeros(self.numNeighbours))
        self.numCells += 1
        self.m = np.concatenate((np.repeat(self.width, self.numCells), \
                    np.repeat(self.height, self.numCells)))

    def removeCell(self, c):
        """Function to removes one cell - WARNING: NOT WORKING PROPERLY!"""
        self.centresVec = np.delete(np.delete(self.centresVec, self.numCells + c), c)
        self.radiiVec = np.delete(self.radiiVec, c, 0)
        self.nearestNeighboursVec = np.delete(self.nearestNeighboursVec, c, 0)
        self.nearestNeighbourDistanceVec = np.delete(self.nearestNeighbourDistanceVec, c, 0)
        self.numCells -= 1
        self.m = np.concatenate((np.repeat(self.width, self.numCells), \
                    np.repeat(self.height, self.numCells)))

    def calculateNearestNeighbours(self):
        """Function to calculate nearest n neighbours to each cell"""

        # query the tree with the sequence of (x, y) cordinates of
        # all cells
        q = self.KDTree.query(self.sequenceOfXY(), k=1 + self.numNeighbours)

        # assign two class variables to results after removing
        # the first query result for each cell which is the
        # cell itself (distance = 0) not the nearest neighbour
        self.nearestNeighbourDistanceVec = q[0][:, 1:]
        self.nearestNeighboursVec = q[1][:, 1:] % self.numCells

        # If using the range function with the cell gap calculation
        # include the following code to populate the gap matrix with
        # the sum of the radii of current cell and each nearest neighbour
        # minus the distance to each neighbour
        # (uses a python iterable to walk through the matrix):
        it = np.nditer(self.nearestNeighbourGapVec, flags=['multi_index'], op_flags=['writeonly'])
        while not it.finished:

            # it.multi_index[0] is the row index
            r = it.multi_index[0]

            # it.multi_index[1] is the column index
            c = it.multi_index[1]

            # it[0] is the matrix element's value
            it[0] = self.nearestNeighbourDistanceVec[r][c] \
                    - self.radiiVec[self.nearestNeighboursVec[r][c]] \
                    - self.radiiVec[r]
            it.iternext()


    def calculateCellsWithinRange(self, pt, r):
        """Function to find all cells within a range r of point x, y
        Returns list of cell IDs"""

        q = self.KDTree.query_ball_point(pt, r)

        return q

    def calculateNearestCell(self, pt):
        """ Function to find the nearest cell to point x, y
        Returns cell ID and distance """

        q = self.KDTree.query(pt)

        return q

    def cellDensity(self):
        """ Calculate the overall (average) density of cells in the array """
        return self.numCells*np.pi*self.avgRadius**2 / (self.width*self.height)

    def localCellDensity(self, x, y, r):
        """ Calculate the local density of cells within distance r of point x, y.
        WARNING: THIS FUNCTION IS NOT WRITTEN YET."""
        return None

    def calculateCellDensitiesAtGridPoints(self):
        """Calculate the cell densities around each point on
        a regular grid across the whole array.
        m is the radius of the circular area (in number of cell radii)
        around the each grid point to do the density calculation in.
        Returns an array of cell densities """

        # This function assumes self.gridPoints has been assigned
        # to a sequence of points (x, y) covering the area of the
        # cell array.  Function sequenceOfXYRegularGrid() should
        # have been called during the CellArray class initialisation.
        # Also assumes the KDTree has been created and self.KDTree
        # assigned to it

        # Radius of the circular areas is defined by
        r = self.areaRadiusFactor*self.gridSpacing

        tree = self.KDTree
        q = tree.query(self.gridPoints, k=self.numCells, \
                          distance_upper_bound=r)

        cellAreas = np.sum( \
            vOverlappingAreaOfTwoCircles(self.avgRadius, \
                                         r, \
                                         q[0]), axis=1)

        self.cellDensitiesAtGridPoints = \
                    cellAreas / (np.pi*(r**2))


    def createKDTree(self):
        """Creates a KDTree from a sequence of cell (x, y) co-ordinates
        using the SciPy spatial algorithm KDTree()."""
        # See also function self.sequenceOfXYExtended_old() which prepares an
        # extended sequence of cell (x, y) co-ordinates

        self.KDTree = KDTree(self.sequenceOfXYExtended_old())


    def sequenceOfXY(self):
        """Function to prepare a sequence of cell (x, y) co-ordinates
        which can be used to do queries on the KDTree."""
        # Note this function does not include the 'ghost cells'
        return zip(self.centresVec[0:self.numCells], self.centresVec[self.numCells:])


    # BIG ISSUE WITH THIS FUNCTION: Because a reduced set of adjacent ghost
    # cells is used the ids of these do not map to the main cells using the
    # modulus function:
    #   original_cellID = ghost_cellID % self.numCells
    # So I have temporarily switched back to using the old version of this
    # function below.
    def sequenceOfXYExtended(self):
        """Function to prepare an extended sequence of cell (x, y) co-ordinates
        which can be used to generate the KDTree for nearest neighbour searches
        with 'ghost cells' on all sides to create the effect of an infinite
        (tessellating) array space."""

        n = self.numCells
        w = self.width
        h = self.height

        bufferSize = max(self.avgRadius*4, \
                        self.areaRadiusFactor*self.gridSpacing)

        # Convert the x, y co-ordinates in CellArray.centresVec
        # into a 2-dimensional array suitable for use by
        # the SciPy KDTree function
        xy = np.transpose(self.centresVec.reshape((2, n)))

        # Create a logical mask of which points need replicating
        # to the left of the cell array
        iterable = ((p[0] > (w - bufferSize)) for p in xy)
        xh = np.fromiter(iterable, np.bool)

        # Create a logical mask of which points need replicating
        # to the right of the cell array
        iterable = ((p[0] < bufferSize) for p in xy)
        xl = np.fromiter(iterable, np.bool)

        # Create a logical mask of which points need replicating
        # below the cell array
        iterable = ((p[1] > (h - bufferSize)) for p in xy)
        yh = np.fromiter(iterable, np.bool)

        # Create a logical mask of which points need replicating
        # above the cell array
        iterable = ((p[1] < bufferSize) for p in xy)
        yl = np.fromiter(iterable, np.bool)

        # Create additional masks from combinations of above
        xm = np.any([xh, xl], axis=0)
        ym = np.any([yh, yl], axis=0)
        xym = np.all([xm, ym], axis=0)

        # Calculate the number of extra points that
        # will need to be added to the x-y matrix
        xn = sum(xm)
        yn = sum(ym)
        xyn = sum(xym)

        # Create a new array of sufficient size to accommodate the
        # extended set of x-y co-ordinates
        newXY = np.append(xy, np.zeros((xn + yn + xyn, 2)), 0)

        i = n

        # Construct additional arrays of the x-y co-ordinates
        # of the additional points
        test1 = xy[xl] + np.array((w, 0.0))
        test2 = xy[xh] - np.array((w, 0.0))
        test3 = xy[yl] + np.array((0.0, h))
        test4 = xy[yh] - np.array((0.0, h))

        # Copy the additional co-ordinates to the main array
        for j, el in enumerate(test1):
            newXY[i] = el
            i += 1

        for j, el in enumerate(test2):
            newXY[i] = el
            i += 1

        for j, el in enumerate(test3):
            newXY[i] = el
            i += 1

        for j, el in enumerate(test4):
            newXY[i] = el
            i += 1

        for j, el in enumerate(xm & ym):
            if el:
                newXY[i] = xy[j] + np.array((w*xl[j], h*yl[j])) - np.array((w*xh[j], h*yh[j]))
                i += 1

        return newXY


    # THIS IS THE ORIGINAL VERSION OF THE FUNCTION ABOVE THAT IS
    # INEFFICIENT BECAUSE IT EXTENDS THE AREA COVERED BY CELLS
    # MUCH FURTHER THAN IS NECESSARY (x9 number of cells)
    # Function to prepare an extended sequence of cell (x, y) co-ordinates
    # which can be used to generate the KDTree for nearest neighbour searches
    # with 'ghost cells' on all sides to create the effect of an infinite
    # (tesellating) array space.
    # HOWEVER: in OCtober 2015 I noticed that the nearest neighbour cell
    # informaiton (ids) is incorrect in the newer version above because the
    # and so switched back to using this one.
    def sequenceOfXYExtended_old(self):
        """ORIGINAL VERSION OF sequenceOfXYExtended(). Inefficienct but the
        new version does not provide correct cell ID numbers to the KD Tree
        so this version is now back in use as of October 2015."""

        n = self.numCells

        # To create the effect of an infinite tesellating array space,
        # eight additional sets of 'ghost' cells are created on all sides
        # of the real cell array area (and diagonal to it).

        # The additional 'ghost' cells are ordered in a way that makes it
        # easy to infer the original cell from the ghost cell as follows:
        #   original_cellID = ghost_cellID % self.numCells

        x = self.centresVec[0:n]
        y = self.centresVec[n:]

        # Prepare two vectors to do the x, y manipulation
        xm = np.array((-1.0, 0.0, 1.0, -1.0, 0.0, 1.0, -1.0, 0.0, 1.0)).reshape(9, 1)
        ym = np.array((-1.0, -1.0, -1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0)).reshape(9, 1)

        # Create two sets of x, y co-ordinates for the extended array grid
        xf = (x + xm*self.width).ravel()
        yf = (y + ym*self.height).ravel()

        # Create the KDTree from the sequence of combined (x, y) co-ordinates
        # using the SciPy spatial function KDTree()
        # See here for reference: http://docs.scipy.org/doc/scipy/reference/spatial.html
        return zip(xf, yf)


    def sequenceOfXYRegularGrid(self, gs):
        """Function to prepare a regular grid of co-ordinates for
        use in the cell density calculation."""

        xNum = self.width/gs
        yNum = self.height/gs
        grid = np.mgrid[0:xNum, 0:yNum]

        return zip(grid[0].ravel()*gs, grid[1].ravel()*gs)


    def findLowDensityPoint(self):
        """This function finds a random point in the cell array
        that is in an area of low cell density."""

        if self.numCells == 0:
            return [np.random.rand()*self.width, np.random.rand()*self.height]

        else:

            # Re-build the extended KDTree
            self.createKDTree()

            # Re-calculate the cell densities
            self.calculateCellDensitiesAtGridPoints()

            md = max(self.cellDensitiesAtGridPoints)

            # 'Negative' density = max density - density at each point
            # (This is a vector)
            negDensity = md - self.cellDensitiesAtGridPoints

            # Use negative densities to increase chances of random
            # point being in a low density area
            sumDensities = np.sum(negDensity)

            # Make a cumulative sum list
            cumsum = np.cumsum(negDensity)

            # Pick 5 gridpoints from the set randomly
            i = []
            for j in range(5):
                randomPoint = np.random.rand()*sumDensities
                i.append(np.searchsorted(cumsum, randomPoint))

            # Choose the gridpoint with lowest density
            k = i[np.argmin([self.cellDensitiesAtGridPoints[k] \
                    for k in [a for a in i]])]

            # Now find a local point to put the new cell

            # Pick 10 points randomly around the gridpoint
            r = []
            for j in range(10):

                x = (self.gridPoints[k][0] + (2.0*np.pi*np.random.rand() - 1.0)*self.gridSpacing) \
                         % self.width
                y = (self.gridPoints[k][1] + (2.0*np.pi*np.random.rand() - 1.0)*self.gridSpacing) \
                         % self.height

                # Radial version of same code
                # radius = self.areaRadiusFactor*self.gridSpacing*np.random.rand()
                # angle = 2.0*np.pi*np.random.rand()

                # x = (self.gridPoints[k][0] + radius*np.cos(angle)) \
                #       % self.width
                #
                # y = (self.gridPoints[k][1] + radius*np.sin(angle)) \
                #       % self.height
                #

                # Now run a nearest neighbour search
                q = self.calculateNearestCell([x, y])
                r.append([q[0], x, y])

            furthest = max(r)

            return [furthest[1], furthest[2]]


    def normalize(self):
        """keep cell centres within the array area defined
        by cellArray.width and cellArray.height."""

        # To achieve: x, y = x mod cellArray.width, y mod cellArray.height
        # use pre-built vector m (see cellArray initialization function)
        self.centresVec = self.centresVec % self.m


    def calculateCostFunction(self, x):
        """Re-calculates total cost function when given a vector
        of the x, y co-ordinates of all cells."""

        # keep cell centres within the array area defined by cellArray.width
        # and cellArray.height using: x, y = x mod cellArray.width,
        # y mod cellArray.height
        self.centresVec = x % self.m

        # Re-build the extended KDTree (decided this does not need re-building
        # every iteration)
        self.createKDTree()

        # Re-calculate the nearest neighbours and distances
        self.calculateNearestNeighbours()

        # Re-calculate the cell densities
        self.calculateCellDensitiesAtGridPoints()

        return self.costFunction()



    def costFunction(self):
        """Cost function to be optimized."""

        # If you are running a cellArray with all cells having equal radius,
        # then you can use '2.0*self.avgRadius' in the rangeFunc below instead
        # of the matrix self.nearestNeighbourGapVec and numpy
        # will broadcast the same value for the matrix operation

        stDevOfCellDensity = np.std(self.cellDensitiesAtGridPoints)

        # Cell range cost function
        return np.sum(self.sigmoidFunction(self.nearestNeighbourGapVec) \
                        /self.nearestNeighbourDistanceVec) \
                        + 100.0*stDevOfCellDensity**2


    def costFunctionDerivative(self):
        """Calculates the derivates (gradients) of the above
        cost function for all (x, y) parameters."""

        return sigmoidDerivative(self.nearestNeighbourGapVec) \
                        /self.nearestNeighbourDistanceVec


    def sigmoidFunction(self, x):
        """Sigmoid function (used as part of the cost function)."""

        return 1.0 - 1.0/(1.0 + np.exp(-x))


    def sigmoidDerivative(self, x):
        """first derivative of Sigmoid function"""

        s = self.sigmoidFunction(x)
        return -s*(1.0 - s)


    def adjustCellPositions(self, nIters):
        """Run optimization function to adjust cell positions according
        to error function."""

        # Nelder-Mead / Powell optimization function
        # Here are the results of convergence tests with 100 cells
        # and starting with random initialisation of cells.
        #
        # Powell with maximum iterations per loop: 3
        # 13:46|    0   6.710227
        # 13:49|    1   3.901632
        # 13:52|    2   3.670694
        # 13:54|    3   3.521501
        #
        # Nelder-Mead with maximum iterations per loop: 1200
        # 14:52|    0   6.710227
        # 14:53|    1   6.178420
        #   ...
        # 15:02|   10   4.404349
        #
        # Error % reduction / minute:
        #  Powell       5.9%
        #  Nelder-Mead  3.4%
        #

        res = minimize(self.calculateCostFunction, self.centresVec, \
                    method='Powell', \
                    options={'disp': False, 'maxiter': nIters} \
                    )

        # final call to errorFunction to store result in
        # self.centresVec
        return self.calculateCostFunction(res.x)


# ------------------------ GENERAL FUNCTIONS ---------------------

def overlappingAreaOfTwoCircles(r, R, d):
    """ Function to return the area of overlap of two circles
    if overlap is complete, function returns area of smallest
    circle.  If there is no overlap it returns zero."""

    # if circle r is fully within R, return area
    # of r
    if R >= (r + d):
        return np.pi*r**2

    # if circle R is fully within r, return area
    # of R
    if r >= (R + d):
        return np.pi*R**2

    # If circles do not overlap return 0
    if d >= (r + R):
        return 0.0

    # Equation for area of overlap of two circles with
    # radii, R and r, and centre-to-centre distance, d
    # Source: http://mathworld.wolfram.com/Circle-CircleIntersection.html

    return r**2*np.arccos((d**2 + r**2 - R**2)/(2.0*d*r)) + \
        R**2*np.arccos((d**2 + R**2 - r**2)/(2.0*d*R)) - \
        0.5*np.sqrt((-d + r + R)*(d + r - R)*(d - r + R)*(d + r + R))

# Vectorized version of the above function to return the
# area of overlap of two circles
vOverlappingAreaOfTwoCircles = np.vectorize(overlappingAreaOfTwoCircles)


def spreadPointsRandomly(width, height, num):
    """Function to randomly spread cells relatively evenly
    across an area.  This function first divides the area
    into a set number of sub-areas (depending on the number
    of points to spread) and then ensures they are evenly
    distributed to each area before being randomly placed
    within each area. Returns a numpy array that can be
    assigned to centresVec."""

    divs = int(num/20) + 1
    dw = width/divs
    dh = height/divs

    m = np.mgrid[0:divs, 0:divs]
    xy = zip(m[0].ravel(), m[1].ravel())
    shuffle(xy)

    l = len(xy)

    x = []
    y = []
    for i in range(num):
        next = xy[i % l]
        x.append((next[0] + np.random.rand())*dw)
        y.append((next[1] + np.random.rand())*dh)
    return np.array(x + y)

# ----------------- Graphics Window Class ----------------

class DisplayWindow:
    """DisplayWindow class"""

    def __init__(self, cellArray, w, h):
        """initialise the graphics window dimensions but don't
        open a window yet."""
        self.cellArray = cellArray
        self.width = w*gbl.scale
        self.height = h*gbl.scale
        self.circles = []
        self.labels = []
        self.areaCircles = []
        self.areaTextLabels = []
        self.window = None

    def open(self, name):
        """open a new window if one doesn't exist."""
        if self.window == None:
            self.window = gr.GraphWin(name, self.width, self.height, autoflush=False)
            self.circles = drawCircles(self.cellArray)
            for c in self.circles:
                c.draw(self.window)

    def update(self):
        """Re-draw the contents of current window"""
        if self.window != None:
            if len(self.circles) > 0:
                for c in self.circles:
                    c.undraw()
                self.circles = []
            self.circles = drawCircles(self.cellArray)
            for c in self.circles:
                c.draw(self.window)
            gr.update()
            if len(self.labels) > 0:
                self.addLabels()
            if len(self.areaCircles) > 0:
                self.addDensityAreas()

    # Add numeric labels to cells
    def addLabels(self):
        """Add numeric cell labels to current window."""
        self.cellArray.normalize()
        self.removeLabels()
        for i in range(self.cellArray.numCells):
            x = self.cellArray.centresVec[i % self.cellArray.numCells]*gbl.scale
            y = self.cellArray.centresVec[(i % self.cellArray.numCells) \
                                     + self.cellArray.numCells]*gbl.scale
            text = gr.Text(gr.Point(x, y), '{}'.format(i))
            text.draw(self.window)
            self.labels.append(text)
        gr.update()

    def removeLabels(self):
        """Remove numeric labels from cells."""
        if len(self.labels) > 0:
            for l in self.labels:
                l.undraw()
            self.labels = []
            gr.update()

    def addDensityAreas(self):
        """Add circles to show areas used by density calculation function."""
        self.cellArray.normalize()
        self.removeDensityAreas()
        nx = self.cellArray.width / self.cellArray.gridSpacing
        self.cellArray.createKDTree()
        self.cellArray.calculateCellDensitiesAtGridPoints()
        for (x, y) in self.cellArray.gridPoints:
            c = gr.Circle(gr.Point(x*gbl.scale, y*gbl.scale), \
                    self.cellArray.gridSpacing*self.cellArray.areaRadiusFactor*gbl.scale)
            # c.setFill('lightgrey')
            i = int((x / self.cellArray.gridSpacing)*nx + \
                    (y / self.cellArray.gridSpacing))
            text = gr.Text(gr.Point(x*gbl.scale + 12.0, y*gbl.scale + 12.0), \
                    "%4.2f" %  self.cellArray.cellDensitiesAtGridPoints[i])
            # '{}'.format(self.cellArray.cellDensitiesAtGridPoints[i])
            text.draw(self.window)
            self.areaTextLabels.append(text)
            c.draw(self.window)
            self.areaCircles.append(c)
        gr.update()

    def removeDensityAreas(self):
        """Remove circles showing density calculation areas."""
        if len(self.areaCircles) > 0:
            for c in self.areaCircles:
                c.undraw()
            self.areaCircles = []
            for c in self.areaTextLabels:
                c.undraw()
            self.areaTextLabels = []
            gr.update()


    def close(self):
        """Delete objects and close window"""
        # Not sure if deleting objects is needed
        # Maybe this is automatic when the window closes
        if len(self.circles) > 0:
            for c in self.circles:
                c.undraw()
            del self.circles
        if len(self.labels) > 0:
            for c in self.labels:
                c.undraw()
            del self.labels
        if len(self.areaCircles) > 0:
            for c in self.areaCircles:
                c.undraw()
            del self.areaCircles
        self.window.close()


def drawCircles(cellArray):
    """Returns a list object containing the circles to be drawn in
    graphics window."""

    circles = []
    cellArray.normalize()

    for j in range(cellArray.numCells):
        x = cellArray.centresVec[j]*gbl.scale
        y = cellArray.centresVec[j + cellArray.numCells]*gbl.scale
        c = gr.Circle(gr.Point(x, y), cellArray.radiiVec[j]*gbl.scale)
        c.setFill('lightblue')
        circles.append(c)

        # Now check for cells that overlap the boundaries
        # and draw their missing fragments on the opposite side
        flags = (x > (cellArray.width - cellArray.radiiVec[j])*gbl.scale,
                 x < cellArray.radiiVec[j]*gbl.scale,
                 y > (cellArray.height - cellArray.radiiVec[j])*gbl.scale,
                 y < cellArray.radiiVec[j]*gbl.scale)

        x2 = x
        y2 = y

        # check if part of the cell is off the edge of area boundary
        # if it is, create a copy on the other side
        if sum(flags) > 0:

            # check if cell is out of bounds R
            if flags[0]:
                x2 = x2 - cellArray.width*gbl.scale

            # check if cell is out of bounds L
            if flags[1]:
                x2 = x2 + cellArray.width*gbl.scale

            # check if cell is out of bounds T
            if flags[2]:
                y2 = y2 - cellArray.height*gbl.scale

            # check if cell is out of bounds B
            if flags[3]:
                y2 = y2 + cellArray.height*gbl.scale

            c = gr.Circle(gr.Point(x2, y2), cellArray.radiiVec[j]*gbl.scale)
            c.setFill('lightblue')
            circles.append(c)

        # if cell is out of bounds on two edges then need to create 2 extra copies
        if sum(flags) == 2:
            c = gr.Circle(gr.Point(x, y2), cellArray.radiiVec[j]*gbl.scale)
            c.setFill('lightblue')
            circles.append(c)
            c = gr.Circle(gr.Point(x2, y), cellArray.radiiVec[j]*gbl.scale)
            c.setFill('lightblue')
            circles.append(c)

    return circles


def saveDataToFile(cellArray):
    """Function to save cell co-ordinates and dimensions to text file"""

    # Save cell radii
    filename = 'radiiVec ' + datetime.datetime.now().strftime("%y%m%d%H%M") + ".txt"
    np.savetxt(filename, cellArray.radiiVec, delimiter=',')

    # Save cell co-ordinates
    filename = 'centresVec ' + datetime.datetime.now().strftime("%y%m%d%H%M") + ".txt"
    np.savetxt(filename, cellArray.centresVec, delimiter=',')

    return filename

def loadDataFromFile(cellArray, fileName):
    """Function to load cell co-ordinates from text file"""

    # Load cell co-ordinates
    cellArray.centresVec = np.loadtxt(fileName)

    # Load cell radii from corresponding file
    cellArray.radiiVec = np.loadtxt("radiiVec " + fileName[11:])

def writeToLog(message):
    """Write message to the log file and print to console."""
    text = datetime.datetime.now().strftime("%H:%M") + "| " + message
    with open(gbl.logFilename, "a") as myfile:
        myfile.write(text+"\n")
    print text

def displayConstants():
    """Display current values of constants."""
    return "Default parameters\n" + \
        ("\tSpacing disorder index(IFSD): \t%f\n" % (gbl.spacingDisorderIndex)) + \
        ("\tDensity deviation index:      \t%f\n" % (gbl.densityDeviationIndex)) + \
        ("\tDesired cell spacing:         \t%f\n" % (gbl.desiredCellSpacing)) + \
        ("\tMaximum iterations per loop:  \t%d\n" % (gbl.maxIterations)) + \
        ("\tMaximum optimisation loops:   \t%d\n" % (gbl.loopTimes)) + \
        ("\tCost goal:                    \t%f\n" % (gbl.costGoal)) + \
        ("\tLog filename: %s" % (gbl.logFilename))

def inputInteger(message, default):
    """Get an integer number from user."""
    txt = raw_input((message + " [%d]:") % (default))
    txt = txt or str(default)
    return eval(txt)

def inputFloat(message, default):
    """Get a floating point number from user."""
    txt = raw_input((message + " [%f]:") % (default))
    txt = txt or str(default)
    return eval(txt)

def inputExpression(message, default):
    """Get a text expression from user."""
    txt = raw_input((message + " [%s]:") % (default))
    txt = txt or str(default)
    return eval(txt)

def inputString(message, default):
    """Get a text string from user."""
    txt = raw_input((message + " [%s]:") % (default))
    txt = txt or str(default)
    return txt

# --------------------- START OF MAIN FUNCTION ---------------------


def main():
    """Main program code to be executed at launch."""

    writeToLog("Receptor Array Spacing Simulator".center(60, "-"))
    writeToLog("Date: %s" % datetime.datetime.now().strftime("%d.%m.%Y"))
    writeToLog("Host computer: %s" % socket.gethostname())

    sys.setrecursionlimit(5000)

    # Show constants
    writeToLog(displayConstants())

    # Initialise cell array
    cellArray = CellArray(gbl.numCells, gbl.width, gbl.height, \
                          gbl.avgRadius, gbl.gridSpacing, \
                          gbl.numNeighbours)

    text = "Cell array initialised\n" \
        + ("\tArray dimensions:             \t(%d, %d)\n" % (cellArray.width, cellArray.height)) \
        + ("\tNumber of cells:              \t%d\n" % (cellArray.numCells))  \
        + ("\tCell radius:                  \t%f\n" % (cellArray.avgRadius))  \
        + ("\tGrid spacing:                 \t%f\n" % (cellArray.gridSpacing)) \
        + ("\tNumber of neighbours:         \t%d\n" % (cellArray.numNeighbours)) \


    writeToLog(text)

    # Prepare graphics window class instance (doesn't open a window yet)
    displayWindow = DisplayWindow(cellArray, cellArray.width, \
                cellArray.height)

    # Prepare a list of menu choices

    menuList = (("i", "Initialise array with random data", initialiseCellArray),
                ("l", "Load array data from text file", loadDataFromTextfile),
                ("d", "Display cell array", displayCellArray),
                ("e", "Display cost function value", displayCost),
                ("f", "Add/remove cell ID labels to display", addIDLabels),
                ("g", "Show/hide density calculation areas", addDensityAreas),
                ("a", "Add cells to array", addCells),
                ("r", "Remove cells", removeCells),
                ("j", "Adjust cell positions and radius", adjustCells),
                ("o", "Run optimisation algorithm", runOptimization),
                ("s", "Save array data to text file", saveDataToTextfile),
                ("c", "Change constants", changeConstants),
                ("x", "Exit", exitLoop))

    # Display menu choices to user
    print "Menu choices:"
    for (i, s, f) in menuList:
        print "", i, s

    # Execute user's menu options repeatedly until exit chosen
    loop = True
    while loop:

        # Get input from user
        while True:
            userInput = raw_input("Enter your choice: ").strip()
            if userInput != "": break

        choice = False
        for (i, s, f) in menuList:
            if userInput in i:
                choice = True
                writeToLog(s)
                loop = f(cellArray, displayWindow)

        if choice == False:
            # Invalid choice. Print an error message
            print "Your menu choice was not recognized"

            # Display menu choices to user
            print "Menu choices:"
            for (i, s, f) in menuList:
                print "", i, s



    # TO DO: Save all array data?
    #    with open('cellArrayData.pik', 'wb') as f:
    #        pickle.dump([cellArray], f, -1)
    #    print "Cell array data saved to cellArrayData.pik"

    writeToLog("Program exited")




# The following functions are executed when the user chooses
# menu options in the main() function


def initialiseCellArray(cellArray, displayWindow):
    """Initialise array with a random distribution of cells"""

    # 3 options:
    # (1) Add cells using the lowDenistyPoint() method
    n = cellArray.numCells
    for i in range(n):
        newPoint = cellArray.findLowDensityPoint()
        cellArray.centresVec[i] = newPoint[0]
        cellArray.centresVec[i + n] = newPoint[1]
        if displayWindow.window != None:
            displayWindow.update()

    # (2) Using the spreadpoints function
    # cellArray.centresVec = \
    #    spreadPointsRandomly(cellArray.width, cellArray.height, cellArray.numCells)


    # (3) using a purely random distribution
    # cellArray.centresVec = np.concatenate((np.random.random_sample(NUM_CELLS)*cellArray.width,
    #                                      np.random.random_sample(NUM_CELLS)*cellArray.height),
    #                                     axis=0)

    return True



def loadDataFromTextfile(cellArray, displayWindow):
    """Load array data from textfile."""

    f = raw_input("Enter full filename: ")
    loadDataFromFile(cellArray, f)
    size = len(cellArray.centresVec)
    writeToLog("%d data points loaded from file %s" % (size, f))
    if size != cellArray.numCells*2:
        print "WARNING: cell array data loaded did not match current array size."
        cellArray.numCells = size*2

    return True


def displayCellArray(cellArray, displayWindow):
    """Display cell array in window (or update the display)"""

    if displayWindow.window == None:
        displayWindow.open("Cell Array Display Window")
    else:
        displayWindow.update()

    return True


def displayCost(cellArray, displayWindow):
    """Display cost function value and other optimization
    parameters."""

    writeToLog("%s %s %s %s %s" % ("Iter".center(4), \
                                  "Error".center(10), \
                                  "avgSpacing".center(10), \
                                  "IFSD'".center(10), \
                                  "DenStDev".center(10)))

    # Calculate cost function value
    e = cellArray.calculateCostFunction(cellArray.centresVec)

    # Update KD Tree if it isn't being done by the cost function
    # cellArray.createKDTree()

    # Re-calculate the cell densities if it isn't being done by
    # the cost function
    cellArray.calculateCellDensitiesAtGridPoints()

    # Recalculate optimisation parameters
    # stDevOfCellSpacing = np.std(cellArray.nearestNeighbourDistanceVec)
    stDevOfCellSpacing = np.sqrt(np.sum((cellArray.nearestNeighbourDistanceVec \
                            - gbl.desiredCellSpacing)**2)/cellArray.numCells)
    averageCellSpacing = np.average(cellArray.nearestNeighbourDistanceVec)
    stDevOfCellDensity = np.std(cellArray.cellDensitiesAtGridPoints)

    # Write error and optimisation data to log
    writeToLog("%4d %10.6f %10.3f %10.6f %10.6f" % \
               (0, e, averageCellSpacing, \
                (stDevOfCellSpacing/gbl.desiredCellSpacing), \
                stDevOfCellDensity))

    return True


def addIDLabels(cellArray, displayWindow):
    """Add cell ID numbers to cells in display window."""

    if displayWindow.window != None:
        if displayWindow.labels == []:
            displayWindow.addLabels()
        else:
            displayWindow.removeLabels()
    else:
        writeToLog("Display the cells first")

    return True


def addDensityAreas(cellArray, displayWindow):
    """Display the areas used by the cell density calculation
    in the cell array display window."""

    if displayWindow.window != None:
        if displayWindow.areaCircles == []:
            displayWindow.addDensityAreas()
        else:
            displayWindow.removeDensityAreas()
    else:
        writeToLog("Display the cells first")

    return True


def addCells(cellArray, displayWindow):
    """Add new cells to array in random position."""

    n = inputInteger("Enter number of cells to add", 1)
    for i in range(n):
        cellArray.addCell()
    if displayWindow.window != None:
        displayWindow.update()

    return True


def removeCells(cellArray, displayWindow):
    """Remove selected cells from array."""

    n = 1
    for i in range(n):
        a = inputInteger("Enter cell ID to remove", 1)
        cellArray.removeCell(a)
        if displayWindow.window != None:
            displayWindow.update()

    return True


def adjustCells(cellArray, displayWindow):
    """Allow user to adjust co-ordinates and radious of selected cell."""

    n = cellArray.numCells
    i = inputInteger("Enter cell ID to adjust", 1)
    x = inputFloat("Edit x co-ordinate", cellArray.centresVec[i])
    y = inputFloat("Edit y co-ordinate", cellArray.centresVec[i + n])
    r = inputFloat("Edit radius", cellArray.radiiVec[i])

    if inputString("Confirm change (x, y, r) to (%f, %f, %f)?" % (x, y, r), "yes") == "yes":
        cellArray.centresVec[i] = x
        cellArray.centresVec[i + n] = y
        cellArray.radiiVec[i] = r
        writeToLog("Cell %d (x, y, r) changed to (%f, %f, %f)" % (i, x, y, r))
    else:
        writeToLog("No changes made")

    if displayWindow.window != None:
        displayWindow.update()

    return True


def runOptimization(cellArray, displayWindow):
    """Run solver for set number of iterations."""

    gbl.loopTimes = inputInteger("Enter maximum loops", gbl.loopTimes)

    # Keep a running sum of the last 5 errors:
    qErrors = [9e9, 8e9, 7e9, 6e9, 5e9]

    writeToLog("%s %s %s %s %s"% ("Iter".center(4), \
                                  "Error".center(10), \
                                  "avgSpacing".center(10), \
                                  "IFSD'".center(10), \
                                  "DenStDev".center(10)))

    # Optimisation loop counter
    loopCounter = 0

    # Calculate initial error and
    # optimisation parameters before first iteration

    # Update KD Tree if it isn't being done by the cost function
    # cellArray.createKDTree()

    e = cellArray.calculateCostFunction(cellArray.centresVec)

    # stDevOfCellSpacing = np.std(cellArray.nearestNeighbourDistanceVec)
    stDevOfCellSpacing = np.sqrt(np.sum((cellArray.nearestNeighbourDistanceVec \
                            - gbl.desiredCellSpacing)**2)/cellArray.numCells)
    averageCellSpacing = np.average(cellArray.nearestNeighbourDistanceVec)
    stDevOfCellDensity = np.std(cellArray.cellDensitiesAtGridPoints)

    # Write initial error and optimisation data to log
    writeToLog("%4d %10.6f %10.3f %10.6f %10.6f" % \
                   (loopCounter, e, averageCellSpacing, \
                    stDevOfCellSpacing/gbl.desiredCellSpacing, \
                    stDevOfCellDensity))

    while 1:

        # Call solver sub-routine
        e = cellArray.adjustCellPositions(gbl.maxIterations)
        loopCounter += 1

        # Update KD Tree if it isn't being done by the cost function
        # cellArray.createKDTree()

        # Re-calculate the cell densities if it isn't being done by
        # the cost function
        # cellArray.calculateCellDensitiesAtGridPoints()

        # Recalculate optimisation parameters
        # stDevOfCellSpacing = np.std(cellArray.nearestNeighbourDistanceVec)
        stDevOfCellSpacing = np.sqrt(np.sum((cellArray.nearestNeighbourDistanceVec \
                     - gbl.desiredCellSpacing)**2)/cellArray.numCells)
        averageCellSpacing = np.average(cellArray.nearestNeighbourDistanceVec)
        stDevOfCellDensity = np.std(cellArray.cellDensitiesAtGridPoints)

        # Write error and optimisation data to log
        writeToLog("%4d %10.6f %10.3f %10.6f %10.6f" % \
                   (loopCounter, e, averageCellSpacing, \
                    (stDevOfCellSpacing/gbl.desiredCellSpacing), \
                    stDevOfCellDensity))

        # remove oldest error value from front of queue and
        # add latest to back of queue
        qErrors.pop(0)
        qErrors.append(e)

        # If a drawing window exists, undraw and re-draw the cells
        displayWindow.update()

		# Save parameters to text file
        f = saveDataToFile(cellArray)
        writeToLog("Data saved to file: %s" % (f))

        # Quit if error has reduced to less than the goal
        if e < gbl.costGoal:
            writeToLog("Cost goal reached.")
            break

        # Quit if current error is same as previous 5
        if all(qErrors[0] == item for item in qErrors):
            writeToLog("Failed to converge.")
            break

        # Quit if maximum iteration loops reached
        if loopCounter >= gbl.loopTimes:
            writeToLog("Maximum iteration loops reached.")
            break

    writeToLog("Iteration loops completed: %d" % (loopCounter))

    return True


def saveDataToTextfile(cellArray, displayWindow):
    """Save array data to text file"""

    f = saveDataToFile(cellArray)
    writeToLog("Data saved to file: %s" % (f))

    return True


# TO-DO:
# THIS DOESN'T WORK PROPERLY YET BECAUSE WIERD THINGS
# HAPPEN WHEN SOME OF THESE ARE CHANGED 'ON THE HOOF'
def changeConstants(cellArray, displayWindow):
    """Allow user to change current settings of constants.  WARNING:
    THIS DOESN'T WORK PROPERLY."""

    # Specify the number of neighbours to include in the cost function
    # Note: must be less than the number of cells
    gbl.numNeighbours = inputInteger( \
        "Number of neighbours to include in the cost function", gbl.numNeighbours)

    # Specify cell array dimensions
    gbl.width = inputExpression("Specify cell array dimensions - width", gbl.width)
    gbl.height = inputExpression("Specify cell array dimensions - height", gbl.height)
    if displayWindow != None:
        displayWindow.width = gbl.width
        displayWindow.height = gbl.height

    # Specify cell radius
    gbl.avgRadius = inputExpression("Specify cell radius", gbl.avgRadius)

    # Specify number of receptor cells
    gbl.numCells = inputInteger("Specify number of receptor cells", gbl.numCells)

    # Specify maximum number of optimizer iterations
    gbl.maxIterations = inputInteger( \
        "Specify maximum number of optimizer iterations", gbl.maxIterations)

    # Specify maximum number of optimizer loop times
    gbl.loopTimes = inputInteger( \
        "Specify maximum number of optimizer loop times", gbl.loopTimes)

    # Specify cost function goal
    gbl.costGoal = inputExpression("Specify cost function goal", gbl.costGoal)

    # Spacing of grid points that are used for the centres of
    # circle areas used for density calculations
    gbl.gridSpacing = inputExpression( \
        "Specify grid spacing for cell density calculation", gbl.gridSpacing)

    return True


def exitLoop(cellArray, displayWindow):
    """Exit user menu loop"""

    # If window open, close it
    if displayWindow.window != None:

        # Optional code to hold it open until user clicks with mouse
        # on window:
        #    print "Click on graphics window to close and exit"
        #    message = gr.Text(gr.Point(cellArray.width*0.5, cellArray.height*0.92), \
        #                   'Click on window to close')
        #    message.draw(win)
        #    win.getMouse() # pause for click in window

        displayWindow.close()

    return False


# ------------------------- END OF MAIN CODE ------------------------




if __name__ == '__main__':
    main()









