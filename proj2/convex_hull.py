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

	def compute_hull(self,points):
		#print("starting compute hull, number of points is:")
		#print(len(points))
		if len(points) > 3:
			m = math.floor(len(points)/2)
			lefthalf = points[:m]
			righthalf = points[m:]
			left = self.compute_hull(lefthalf)
			right = self.compute_hull(righthalf)
			#these will contain the  points that no longer belong in the hull
			pointsInLeftToRemove = []
			pointsInRightToRemove = []
			#tangents is a pair of points
			print('Line 41 and left type is')
			print(type(left))
			print('line 43 and right type is')
			print(type(right))
			topTangent = self.findTopTangent(left,right,pointsInLeftToRemove,pointsInRightToRemove)
			botTangent = self.findBotTangent(left,right,pointsInLeftToRemove,pointsInRightToRemove)
			tangents = []
			tangents.append(QLineF(topTangent[0],topTangent[1]))
			tangents.append(QLineF(botTangent[0],botTangent[1]))
			leftMostInRightHull = right[getLeftMost(right)]
			rightMostInLeftHull = left[getRightMost(left)]
			rightMostFoundTwice = foundTwiceinList(pointsInLeftToRemove,rightMostInLeftHull)
			leftMostFoundTwice = foundTwiceinList(pointsInRightToRemove,leftMostInRightHull)
			for i in pointsInLeftToRemove:
				for j in range(0,len(left)):
					if j < len(left) and left[j] == i:
						if left[j] == rightMostInLeftHull:
							if rightMostFoundTwice == True:
								left.pop(j)
						else:
							left.pop(j)
			for i in pointsInRightToRemove:
				for j in range(0,len(right)):
					if j < len(right) and right[j] == i:
						if right[j] == leftMostInRightHull:
							if leftMostFoundTwice == True:
								right.pop(j)
						else:
							right.pop(j)
			self.show_tangent.emit(tangents,(0,0,0))
			hull = combineHalves(left,right,topTangent,botTangent)

			return hull
		else:
			hull = makeHull(points)
			polygon = []
			for i in range(0, len(hull)):
				if i == len(hull)-1:
					polygon.append(QLineF(hull[i],hull[0]))
				else:
					polygon.append(QLineF(hull[i],hull[i+1]))
			print('printing Hull and hull has length of:')
			print(len(hull))
			self.show_hull.emit(polygon,(255,0,0))
			return hull

	def findTopTangent(self,leftHull, rightHull,pointsInLeftToRemove,pointsInRightToRemove):
		leftMostIndex = getLeftMost(rightHull)
		rightMostIndex = getRightMost(leftHull)
		print('line 147')
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
		previousRightHullIndex = leftMostIndex
		currentLeftHullIndex = rightMostIndex
		currentRightHullIndex = leftMostIndex
		while leftCanMove or rightCanMove:
			#print('line 164')
			#moveLeft until it can't move anymore
			while leftCanMove:
				#print('line 167')
				#get the next point counterClockwise from current point
				if currentLeftHullIndex == 0:
					currentLeftHullIndex = len(leftHull)-1
				else:
					currentLeftHullIndex -= 1
				#currentLeftHullIndex = moveLeftCounterClockwise(previousLeftHullIndex, leftHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				#is the new slope better than previous slope
				if tempSlope < currentslope:
					currentslope = tempSlope
					#since we found a better point, we know the previous point
					# won't be in our hull unless it is the original start point,
					# in which case it might be the point used by the bottom tangent
					print('putting the following index onto Points in left to remove')
					print(previousLeftHullIndex)
					pointsInLeftToRemove.append(leftHull[previousLeftHullIndex])
					previousLeftHullIndex = currentLeftHullIndex
					leftCanMove = True
					rightCanMove = True

				else:
					leftCanMove = False
					#move back to the one we know works as a potential tangent
					currentLeftHullIndex = previousLeftHullIndex
			#move around Right Hull until it can't move anymore
			while rightCanMove:
				#print('line 195')
				#get next point clockwise from currentPoint
				if currentRightHullIndex == len(rightHull)-1:
					currentRightHullIndex = 0
				else:
					currentRightHullIndex += 1
				#currentRightHullIndex = moveRightClockwise(previousRightHullIndex, rightHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				if tempSlope > currentslope:
					print('line 207')
					print('putting the following index onto Points in right to remove')
					print(previousRightHullIndex)
					pointsInRightToRemove.append(rightHull[previousRightHullIndex])
					previousRightHullIndex = currentRightHullIndex
					rightCanMove = True
					leftCanMove = True

				else:
					rightCanMove = False
					currentRightHullIndex = previousRightHullIndex

		return [leftHull[currentLeftHullIndex], rightHull[currentRightHullIndex]]

	def findBotTangent(self,leftHull, rightHull, pointsInLeftToRemove,pointsInRightToRemove):
		#print('line 219')
		leftMostIndex = getLeftMost(rightHull)
		rightMostIndex = getRightMost(leftHull)
		#this is used to make sure we are moving clockwise or counterClockwise.
		#slope = (y2-y1)/(x2-x1)
		deltaY = rightHull[leftMostIndex].y()-leftHull[leftMostIndex].y()
		deltaX = rightHull[leftMostIndex].x()-leftHull[leftMostIndex].x()
		currentslope =	deltaY/deltaX
		#represents if the given side has a potential for moving around the hull more
		leftCanMove = True
		rightCanMove = True
		previousLeftHullIndex = rightMostIndex
		previousRightHullIndex = leftMostIndex
		currentLeftHullIndex = rightMostIndex
		currentRightHullIndex = leftMostIndex
		while leftCanMove or rightCanMove:
			#print('line 241')
			#moveLeft until it can't move anymore
			while leftCanMove:
				#print('line 244 and currentLeftHullIndex is:')
				#print(currentLeftHullIndex)
				if currentLeftHullIndex == len(leftHull)-1:
					currentLeftHullIndex = 0
				else:
					currentLeftHullIndex += 1
				#currentLeftHullIndex = moveLeftClockwise(previousLeftHullIndex, leftHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				#print('line 255 and tempslope is')
				#print(tempSlope)
				#print('line 257 and currentSlope is')
				#print(currentslope)
				#is the new slope better than previous slope
				if tempSlope > currentslope:
					currentslope = tempSlope
					print('line 207')
					print('putting the following index onto Points in left to remove')
					print(previousLeftHullIndex)
					pointsInLeftToRemove.append(leftHull[previousLeftHullIndex])
					previousLeftHullIndex = currentLeftHullIndex
					leftCanMove = True
					rightCanMove = True
				else:
					leftCanMove = False
					#move back to the one we know works as a potential tangent
					currentLeftHullIndex = previousLeftHullIndex
			while rightCanMove:
				#print('line 266')
				#get next point clockwise from currentPoint
				if currentRightHullIndex == 0:
					currentRightHullIndex = len(rightHull)-1
				else:
					currentRightHullIndex -=1
				#currentRightHullIndex = moveRightCounterClockwise(previousRightHullIndex, rightHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				if tempSlope > currentslope:
					currentSlope = tempSlope
					print('putting the following index onto Points in left to remove')
					print(previousRightHullIndex)
					pointsInRightToRemove.append(rightHull[previousRightHullIndex])
					previousRightHullIndex = currentRightHullIndex
					rightCanMove = True
					leftCanMove = True

				else:
					rightCanMove = False
					currentRightHullIndex = previousRightHullIndex
		return [leftHull[currentLeftHullIndex],rightHull[currentRightHullIndex]]


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
		self.compute_hull(hullPoints)
		# TODO: COMPUTE THE CONVEX HULL USING DIVIDE AND CONQUER

		t4 = time.time()
		USE_DUMMY = False
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





		#returns a hull that starts at the leftmostPoint and moves
		# clockwise around through the points if there are three.
		# otherwise, it just returns the two points
def makeHull(points):

	if len(points) == 3:
		toReturn = [0,0,0]
		print("lenght of the ToReturn list on line 118:")
		print(len(toReturn))
		print("length of the points passed in")
		print(len(points))
		toReturn[0] = points[0]
		slopeA = (points[1].y() - points[0].y())/(points[1].x() - points[0].x())
		slopeB = ((points[1].y() - points[0].y())/(points[1].x() - points[0].x()))

		if slopeB > slopeA:
			toReturn[1] = points[2]
			toReturn[2] = points[1]
		else:
			toReturn[1] = points[1]
			toReturn[2] = points[2]
		return toReturn

	else:
		return points





def getLeftMost(hull):
	#print('line 281')
	#print(type(hull))
	mostLeftX = 1.5
	leftMostIndex = -1
	for i in range(0,len(hull)):
		if hull[i].x() < mostLeftX:
			mostLeftX = hull[i].x()
			leftMostIndex = i

	#print('line 294')
	return leftMostIndex


def getRightMost(hull):
	mostRightX = -1.5
	rightMostIndex = -1
	for i in range(0,len(hull)):
		if hull[i].x() > mostRightX :
			rightMostIndex = i
			mostRightX = hull[i].x()

	return rightMostIndex

	#topTangent and botTangent are arrays with two valuesself.
	#the first value is the point of the left hull where the tangent connects
	#the second value is the point of the right hull where the tangent connects
def combineHalves(leftHalf, rightHalf, topTangent, botTangent):
	#print('starting combine halves')

	print(topTangent[0].x(),topTangent[0].y())
	toReturn = []
	foundTopTangent = False
	foundBotTangent = False
	i = 0
	j = 0
	for k in range (0,len(rightHalf)):
		if rightHalf[k] == topTangent[1]:
			j = k
			break

	#move around left until you hit the index where top tangent connects
	while foundTopTangent == False:
		#print('line 335')
		toReturn.append(leftHalf[i])
		i+=1
		if leftHalf[i] == topTangent[0]:
			foundTopTangent = True
	#move clockwise around right half until you hit where bot tangent connects
	while foundBotTangent == False:

		#print('line 339')
		toReturn.append(rightHalf[j])
		if j == len(rightHalf)-1 and len(rightHalf) > 2:
			j = 0
		else:
			j +=1
	for k in range(i,len(leftHalf)):
		if leftHalf[k] == botTangent[0]:
			i = k
			break
	#finish moving around the bottom of the left hull from where the
	# bot tangent connects to the the starting (leftMost) point
	while i != len(leftHalf):
		#print('line 350')
		toReturn.append(leftHalf[i])
		i+=1

	#print('leaving combine halves')
	return toReturn

def foundTwiceinList(points, pointToCheck):
	foundOnce = False
	foundTwice = False
	for i in points:
		if i == pointToCheck:
			if foundOnce == True:
				foundTwice = True
			else:
				foundOnce = True
	return foundTwice



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
	#print (left[0].x())
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
