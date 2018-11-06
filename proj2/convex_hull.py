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

	def compute_hull(self,points):												# Since this is a recursive function that cuts the problem in
																				# half each time, it will execute a maximum of log(n) times
																				#where log(n) is the number of points to start
																				#then, accounting for each of the method calls in the method
																				# gives us bigO(n+n+n)*bigO(log(n)) = bigO(3nlog(n))
																				#    = bigO(nlog(n))
																				#The total space complexity is bigO(2n) because there is
																				#the starting array of points, then an array that gets made
																				#for the set of points that make up the hull
																				#this second set could contain all the original points
																				#in a worst case scenario so ultimately bigO(n)
		if len(points) > 3:														#
			m = math.floor(len(points)/2)										#
			lefthalf = points[:m]												# time = O(n) space = bigO(1/2n)
			righthalf = points[m:]												# time = O(n) space = bigO(1/2n)
			left = self.compute_hull(lefthalf)
			right = self.compute_hull(righthalf)
			#these will contain the  points that no longer belong in the hull
			pointsInLeftToRemove = []
			pointsInRightToRemove = []
			#tangents is a pair of points
			topTangent = self.findTopTangent(left,right,						#time = bigO(n) space = bigO(1)
			pointsInLeftToRemove,pointsInRightToRemove)
			botTangent = self.findBotTangent(left,								#time = bigO(n) space = bigO(1)
			right,pointsInLeftToRemove,pointsInRightToRemove)
			hull = combineHalves(left,right,topTangent,botTangent)				#time = bigO(n) space = bigO(n)
			return hull
		else:
			hull = makeHull(points)												#constant bigO(1)
			return hull

	def findTopTangent(self,leftHull, rightHull,								#TotalTime Complexity = bigO(n) + bigO(n) + bigO(n)
	pointsInLeftToRemove,pointsInRightToRemove):								#TotalSpace Complexity = big. There aren't any things greater
																				# than individual points stored or a slope used in this
																				#and it doesn't ever change from iteration to iteration
		leftMostIndex = getLeftMost(rightHull)									#bigO(n)
		rightMostIndex = getRightMost(leftHull)									#bigO(n)
		#this is used to make sure we are moving clockwise
		# or counterClockwise.
		#Clockwise can be defined as increasing x values
		# and values of y that are greater than the start point's y
		rightHullOriginalY = rightHull[leftMostIndex].y()						#
		leftHullOriginalY = leftHull[rightMostIndex].y()						#(1)
		#slope = (y2-y1)/(x2-x1)
		deltaY = rightHull[leftMostIndex].y()-leftHull[rightMostIndex].y()		#
		deltaX = rightHull[leftMostIndex].x()-leftHull[rightMostIndex].x()		#
		currentslope =	deltaY/deltaX											#
		leftCanMove = True														#
		rightCanMove = True														#
		previousLeftHullIndex = rightMostIndex									#
		previousRightHullIndex = leftMostIndex
		currentLeftHullIndex = rightMostIndex
		currentRightHullIndex = leftMostIndex
		while leftCanMove or rightCanMove:										#this can iterate n+m times in theory.  n and m are the Number
																				# of points in the leftHull and RightHull.  Let n be bigger of
																				# the two.  That makse this loop
																				#bigO(2n) = bigO(n)
			#moveLeft until it can't move anymore
			while leftCanMove:													#in worse case can happen for all points of leftHull
																				# therefore bigO(n)
				#get the next point counterClockwise from current point
				if currentLeftHullIndex == 0:									#
					currentLeftHullIndex = len(leftHull)-1						#
				else:
					currentLeftHullIndex -= 1									#
				#calculate slope
				Ychange = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y() #
				Xchange = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x() #
				tempSlope = Ychange/Xchange										#
				#is the new slope better than previous slope
				if tempSlope < currentslope:									#
					currentslope = tempSlope									#
					previousLeftHullIndex = currentLeftHullIndex				#
					leftCanMove = True											#
					rightCanMove = True											#

				else:
					leftCanMove = False											#
					#move back to the one we know works as a potential tangent
					currentLeftHullIndex = previousLeftHullIndex				#
			#move around Right Hull until it can't move anymore
			while rightCanMove:													#worst case scenario is every point so
																				# bigO(n)
				#get next point clockwise from currentPoint
				if currentRightHullIndex == len(rightHull)-1:					#
					currentRightHullIndex = 0									#
				else:
					currentRightHullIndex += 1									#
				#currentRightHullIndex = moveRightClockwise(previousRightHullIndex, rightHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y() #
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x() #
				tempSlope = deltaY/deltaX										#
				if tempSlope > currentslope:									#
					currentslope = tempSlope									#
					tangentLine = []											#
					previousRightHullIndex = currentRightHullIndex				#
					rightCanMove = True											#
					leftCanMove = True

				else:
					rightCanMove = False
					currentRightHullIndex = previousRightHullIndex

		return [leftHull[currentLeftHullIndex], rightHull[currentRightHullIndex]]

	def findBotTangent(self,leftHull, rightHull,								#See "findTopTangent" for bigO.  They're the same
	 pointsInLeftToRemove,pointsInRightToRemove):
		leftMostIndex = getLeftMost(rightHull)
		rightMostIndex = getRightMost(leftHull)
		#this is used to make sure we are moving clockwise or counterClockwise.
		#slope = (y2-y1)/(x2-x1)
		deltaY = rightHull[leftMostIndex].y()-leftHull[rightMostIndex].y()
		deltaX = rightHull[leftMostIndex].x()-leftHull[rightMostIndex].x()
		currentslope =	deltaY/deltaX
		#represents if the given side has a potential for moving around the hull more
		leftCanMove = True
		rightCanMove = True
		previousLeftHullIndex = rightMostIndex
		previousRightHullIndex = leftMostIndex
		currentLeftHullIndex = rightMostIndex
		currentRightHullIndex = leftMostIndex
		while leftCanMove or rightCanMove:
			#moveLeft until it can't move anymore
			while leftCanMove:
				if currentLeftHullIndex == len(leftHull)-1:
					currentLeftHullIndex = 0
				else:
					currentLeftHullIndex += 1
				#currentLeftHullIndex = moveLeftClockwise(previousLeftHullIndex, leftHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				#is the new slope better than previous slope
				if tempSlope > currentslope:
					currentslope = tempSlope
					previousLeftHullIndex = currentLeftHullIndex
					leftCanMove = True
					rightCanMove = True
				else:
					leftCanMove = False
					#move back to the one we know works as a potential tangent
					currentLeftHullIndex = previousLeftHullIndex
			while rightCanMove:
				#get next point clockwise from currentPoint
				if currentRightHullIndex == 0:
					currentRightHullIndex = len(rightHull)-1
				else:
					currentRightHullIndex -=1
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				if tempSlope < currentslope:
					currentslope = tempSlope
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
	#	print('printing all the points in order returned from merge sort')
	#	for i in range (0,len(self.points)):
	#		print(self.points[i].x(),"  ",self.points[i].y())

		hullPoints = copy.deepcopy(self.points)										#Big-oh(n) where n is the number of poitns
		t3 = time.time()
		finishedHull = self.compute_hull(hullPoints)
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
			hullLines = []
			for i in range(0, len(finishedHull)):
				if i == len(finishedHull)-1:
					hullLines.append(QLineF(finishedHull[i],finishedHull[0]))
				else:
					hullLines.append(QLineF(finishedHull[i],finishedHull[i+1]))
			self.show_hull.emit(hullLines,(0,0,255))

		# send a signal to the GUI thread with the time used to compute the hull
		self.display_text.emit('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
		print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))





	#returns a hull that starts at the leftmostPoint and moves
	# clockwise around through the points if there are three.
	# otherwise, it just returns the two points
def makeHull(points):															#time complexity = constant.
																				# because this method only gets called on the base
																				#case for compute_hull.  So at most, there are 3 points
																				#min 2 points.
																				#Space complexity = constant for the same reasons

	if len(points) == 3:
		toReturn = [0,0,0]
		toReturn[0] = points[0]
		slopeA = (points[1].y() - points[0].y())/(points[1].x() - points[0].x())
		slopeB = ((points[2].y() - points[0].y())/(points[2].x() - points[0].x()))

		if slopeB > slopeA:
			toReturn[1] = points[2]
			toReturn[2] = points[1]
		else:
			toReturn[1] = points[1]
			toReturn[2] = points[2]
		return toReturn

	else:
		#there is no clockwise or counterClockwise for 2 points
		return points

def getLeftMost(hull):															#bigO(n) because it can iterate through potentially everyPoint
	mostLeftX = 1.5																# before finding the most extreme.  N is the number of points in hull
	leftMostIndex = -1
	for i in range(0,len(hull)):
		if hull[i].x() < mostLeftX:
			mostLeftX = hull[i].x()
			leftMostIndex = i
	return leftMostIndex

def getRightMost(hull):															#same bigO as getLeftMost()
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

def combineHalves(leftHalf, rightHalf, topTangent, botTangent):					#space complexity = bigO(2n) where n is the number of points
																				# in left half or right half (whichever is bigger)
																				#because we end up with an array with all the points on the hull
																				#which in worst case, could be each of the original points
																				# time complexity: I have 2 for loops and 2 while loops that all run
																				#at bigO(n) which makes bigO(4n)
																				# therefore time complexity = bigO(n)
	toReturn = []
	foundTopTangent = False
	foundBotTangent = False
	i = 0
	j = 0
	foundTheTopTangentInRightHull = False
	for k in range (0,len(rightHalf)):											#timecomplexity = bigO(n) where n is the number of
																				#points in righthalf
		#index where the top tangent is in the rightHalf array					# because it could not find a tangent until the very end

		if rightHalf[k] == topTangent[1]:
			j = k
			foundTheTopTangentInRightHull = True
			break
	#move around left until you hit the index where top tangent connects
	while foundTopTangent == False:												#bigO(n) as we could travel all the way around
																				# and not find the tangent until the very end of the half

		toReturn.append(leftHalf[i])
		if leftHalf[i] == topTangent[0]:
			foundTopTangent = True
		i+=1
	#move clockwise around right half until you hit where bot tangent connects
	while foundBotTangent == False:												#bigO(n) as we could travel all the way around
																				# and not find the tangent until the end of the half
		toReturn.append(rightHalf[j])
		if rightHalf[j] == botTangent[1]:
			foundBotTangent = True
		if j == len(rightHalf)-1:
			j = 0
		else:
			j+=1

	#find index for bot tangent on left
	#go backwards through the list because most likely, the bot Tangent is
	#on the bottom of the hull/closer to the end of the list
	foundTangent = False
	for k in range(len(leftHalf)-1, 0,-1):										#bigO(n) for the same reasons as up above
		if leftHalf[k] == botTangent[0]:
			i = k
			foundTangent = True
			break
	#finish moving around the bottom of the left hull from where the
	# bot tangent connects to the the starting (leftMost) point
	if foundTangent == True:
		#toReturn.append(leftHalf[0])
		while i != len(leftHalf):												#bigO(n) because we might have to travel all the way around
																				# the half of the hull until we reach the end.
			toReturn.append(leftHalf[i])
			i+=1
	return toReturn

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
