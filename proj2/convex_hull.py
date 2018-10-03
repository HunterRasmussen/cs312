#!/usr/bin/python3
# why the shebang here, when it's imported?  Can't really be used stand alone, right?  And fermat.py didn't have one...
# this is 4-5 seconds slower on 1000000 points than Ryan's desktop...  Why?

import math
import copy
from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QThread, pyqtSignal
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QThread, pyqtSignal
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time



class ConvexHullSolverThread(QThread):
	def __init__( self, unsorted_points,demo):
		self.points = unsorted_points
		self.pause = demo
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	show_hull = pyqtSignal(list,tuple)
	display_text = pyqtSignal(str)

# some additional thread signals you can implement and use for debugging, if you like
	show_tangent = pyqtSignal(list,tuple)
	erase_hull = pyqtSignal(list)
	erase_tangent = pyqtSignal(list)


	def run( self):
		assert( type(self.points) == list and type(self.points[0]) == QPointF )

		n = len(self.points)
		print( 'Computing Hull for set of {} points'.format(n) )

		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		#sortedPoints = sorted(self.points , key = lambda k: [k[0],k[1]])
		mergeSort(self.points,0,n-1)
		t2 = time.time()
		print('Time Elapsed (Sorting): {:3.3f} sec'.format(t2-t1))
		print('printing all the points in order returned from merge sort')
		for i in range (0,len(self.points)-1):
			print(self.points[i].x())

		hullPoints = copy.deepcopy(self.points)										#Big-oh(n) where n is the number of poitns
		t3 = time.time()
		compute_hull(hullPoints)
		# TODO: COMPUTE THE CONVEX HULL USING DIVIDE AND CONQUER

		t4 = time.time()

		USE_DUMMY = True
		if USE_DUMMY:
			# this is a dummy polygon of the first 3 unsorted points
			polygon = [QLineF(self.points[i],self.points[(i+1)%3]) for i in range(3)]

			# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
			# object can be created with two QPointF objects corresponding to the endpoints
			assert( type(polygon) == list and type(polygon[0]) == QLineF )
			# send a signal to the GUI thread with the hull and its color
			self.show_hull.emit(polygon,(255,0,0))

		else:
			# TODO: PASS THE CONVEX HULL LINES BACK TO THE GUI FOR DISPLAY
			pass

		# send a signal to the GUI thread with the time used to compute the hull
		self.display_text.emit('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
		print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))


def compute_hull(points):
	print("starting compute hull, number of points is:")
	print(len(points))
	if len(points) > 3:
		m = math.floor(len(points)/2)
		lefthalf = points[:m]
		righthalf = points[m:]
		left = compute_hull(lefthalf)
		right = compute_hull(righthalf)
		pointsToRemove  = []
		#tangents is a pair of points
		topTangent = findTopTangent(left,right,pointsToRemove)
		botTangent = findBotTangent(left,right,pointsToRemove)

		return left+right
	return points


def findTopTangent(leftHull, rightHull,pointsToRemove):
	leftMostIndex = getLeftMost(rightHull)
	rightMostIndex = getRightMost(leftHull)
	#this is used to make sure we are moving clockwise or counterClockwise.
	#Clockwise can be defined as increasing x values and values of y that are greater than the start point's y
	rightHullOriginalY = rightHull[leftMostIndex].y()
	leftHullOriginalY = leftHull[rightMostIndex].y()
	#slope = (y2-y1)/(x2-x1)
	deltaY = rightHull[leftMostIndex].y()-leftHull[leftMostIndex].y()
	deltaX = rightHull[leftMostIndex].x()-leftHull[leftMostIndex].x()
	currentslope =	deltaY/deltaX
	#represents if the given side has a potential for moving around the hull more
	leftCanMove = True
	rightCanMove = True
	previousLeftHullIndex = rightMostIndex
	previousRightHulllIndex = leftMostIndex
	currentLeftHullIndex = rightMostIndex
	currentRightHullIndex = leftMostIndex
	while leftCanMove or rightCanMove:
		#moveLeft until it can't move anymore
		while leftCanMove:
			#get the next point counterClockwise from current point
			currentLeftHullIndex = moveLeftCounterClockwise(previousLeftHullIndex, leftHullOriginalY)
			#calculate slope
			deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
			deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
			tempSlope = deltaY/deltaX
			#is the new slope better than previous slope
			if tempSlope < slope:
				slope = tempSlope
				#since we found a better point, we know the previous point
				# won't be in our hull unless it is the original start point,
				# in which case it might be the point used by the bottom tangent
				if previousLeftHullIndex != rightMostIndex:
					pointsToRemove.append(previousLeftHullIndex)
				previousLeftHullIndex = currentLeftHullIndex
				leftCanMove = True
				rightCanMove = True

			else:
				leftCanMove = False
				#move back to the one we know works as a potential tangent
				currentLeftHullIndex = previousLeftHullIndex
		#move around Right Hull until it can't move anymore
		while rightCanMove:
			#get next point clockwise from currentPoint
			currentRightHullIndex = moveRightClockwise(previousRightHulllIndex, rightHullOriginalY)
			#calculate slope
			deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
			deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
			tempSlope = deltaY/deltaX
			if tempSlope > slope:
				if previousRightHulllIndex != leftMostIndex:
					pointsToRemove.append(previousRightHulllIndex)
				previousRightHulllIndex = currentRightHullIndex
				rightCanMove = True
				leftCanMove = True

			else:
				rightCanMove = False
				currentRightHullIndex = previousRightHulllIndex



def findBotTangent(leftHull, rightHull, pointsToRemove):
	leftMostIndex = getLeftMost(rightHull)
	rightMostIndex = getRightMost(leftHull)
	#this is used to make sure we are moving clockwise or counterClockwise.
	#Clockwise can be defined as increasing x values and values of y that are greater than the start point's y
	#since the hulls should contain only the outside points from the original set of pointsToRemove
	# we can  look at the next point safely as long as it isn't below the original y value.
	rightHullOriginalY = rightHull[leftMostIndex].y()
	leftHullOriginalY = leftHull[rightMostIndex].y()
	#slope = (y2-y1)/(x2-x1)
	deltaY = rightHull[leftMostIndex].y()-leftHull[leftMostIndex].y()
	deltaX = rightHull[leftMostIndex].x()-leftHull[leftMostIndex].x()
	currentslope =	deltaY/deltaX


def getLeftMost(hull):
	print(type(hull))
	mostLeftX = 1.5
	leftMostIndex = -1
	for i in range(0,len(hull)):
		if hull[i].x() < mostLeftX:
			mostLeftX = hull[i].x()
			leftMostIndex = i

	return leftMostIndex


def getRightMost(hull):
	mostRightX = -1.5
	rightMostIndex = -1
	for i in range(0,len(hull)):
		if hull[i].x() > mostRightX :
			rightMostIndex = i
			mostRightX = hull[i].x()

	return rightMostIndex
#  d+c(hull)
#  if hull size == 1
#
#  else
#	cut hull in half
#	lefthull = d+c(lefthalf of cut);
#   rightHull = d+c(rightHalf of cut);
#
#	new LIST
#   topTangent = find topTangent(leftHull, rightHull, LIST);
#   botTangent = find botTangent(leftHull, rightHull LIST);
#   return remove any unecessary POINTS(leftHull,rightHull,topTangent,botTangent)
#		/* returns a pair of points*/
#	findTopTangent(leftHull,rightHull){
#		leftPoint = grap rightmost point in lefthull
#		rightPoint = grab leftmost point in righthull
#		moveleft = true;
#       moveright = true;
#		current slope = slope between leftPoint and rightPoint;
#     while(moveleft || moveright){
#			//if the left moved last
#         if(moveleft)
#			temp = get next point above on right;
#			tempslope = slope between temp and leftPoint
#			if tempslope > current slope:
#				currentslope = tempslope;
#				removePoint from LeftHull;
#				rightPoint = temp;
#				//we reset the moves.  Each time we move, we have to check both sides can't move.
#				moveLeft = true;
#				moveRight = true;
#			else:
#				moveLeft = false;
#		  else if(moveRight):
#			 temp = get next point above on the left;
#			  tempSlope = the slope between temp and right point
#			  if tempSlope < currentslopeL:
#				remove point from rightHull
#				currentslope = tempslope;
#				left point = temp;
#				//reset the moves
#			  else:
#				moveright = false;
#
#

def mergeSort(points, leftIndex, rightIndex):
	if leftIndex < rightIndex:
		m = math.floor((leftIndex + rightIndex)/2)
		print(m)
		mergeSort(points,leftIndex,m)
		mergeSort(points,m+1,rightIndex)
		merge(points,leftIndex,m,rightIndex)

def merge(points, leftIndex, middleIndex, rightIndex):

	leftArraySize = middleIndex - leftIndex + 1
	rightArraySize = rightIndex - middleIndex

	#tempArrays
	left = [0] * (leftArraySize)
	right = [0] * rightArraySize

	#copy data into appropriate arrays
	for i in range(0, leftArraySize):
		left[i] = points[leftIndex+i]

	for j in range(0,rightArraySize):
		right[j] = points[middleIndex+1+j]

	i = 0
	j = 0
	k = leftIndex
	print (left[0].x())
	while i < leftArraySize and j < rightArraySize:
		if left[i].x() < right[j].x() :
			points[k] = left[i]
			i+=1
		elif left[i].x() > right[j].x():
			points[k] = right[j]
			j +=1
		#x's are same, compare y values
		else:
			if left[i].y() < right[j].y() :
				points[k] = left[i]
				i+=1
			else:
				points[k] = rght[j]
				j +=1
		k+=1

	while i<leftArraySize:
		points[k]=left[i]
		i+=1
		k+=1

	while j < rightArraySize:
		points[k] = right[j]
		j+=1
		k+=1
