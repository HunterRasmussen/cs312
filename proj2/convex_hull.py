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
		self.erase_hull.emit(points)
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
			topTangent = self.findTopTangent(left,right,pointsInLeftToRemove,pointsInRightToRemove)
			botTangent = self.findBotTangent(left,right,pointsInLeftToRemove,pointsInRightToRemove)
			tangents = []
			tangents.append(QLineF(topTangent[0],topTangent[1]))
			tangents.append(QLineF(botTangent[0],botTangent[1]))
			leftMostInRightHull = right[getLeftMost(right)]
			rightMostInLeftHull = left[getRightMost(left)]
			#rightMostFoundTwice = foundTwiceinList(pointsInLeftToRemove,rightMostInLeftHull)
			#leftMostFoundTwice = foundTwiceinList(pointsInRightToRemove,leftMostInRightHull)
			#for i in pointsInLeftToRemove:
			#	for j in range(0,len(left)):
			#		if j < len(left) and left[j] == i:
			#			if left[j] == rightMostInLeftHull:
			#				if rightMostFoundTwice == True:
			#					left.pop(j)
			#			else:
			#				left.pop(j)
			#for i in pointsInRightToRemove:
			#	for j in range(0,len(right)):
			#		if j < len(right) and right[j] == i:
			#			if right[j] == leftMostInRightHull:
			#				if leftMostFoundTwice == True:
			#					right.pop(j)
			#			else:
			#				right.pop(j)
			#self.show_tangent.emit(tangents,(0,0,0))
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
			#self.show_hull.emit(polygon,(255,0,0))
			return hull

	def findTopTangent(self,leftHull, rightHull,pointsInLeftToRemove,pointsInRightToRemove):
		leftMostIndex = getLeftMost(rightHull)
		rightMostIndex = getRightMost(leftHull)
		#this is used to make sure we are moving clockwise or counterClockwise.
		#Clockwise can be defined as increasing x values and values of y that are greater than the start point's y
		rightHullOriginalY = rightHull[leftMostIndex].y()
		leftHullOriginalY = leftHull[rightMostIndex].y()
		#slope = (y2-y1)/(x2-x1)
		deltaY = rightHull[leftMostIndex].y()-leftHull[rightMostIndex].y()
		deltaX = rightHull[leftMostIndex].x()-leftHull[rightMostIndex].x()
		currentslope =	deltaY/deltaX
		#print('starting slope.  That is the, the slope between the leftMost and RightMost: ', currentslope)
		#print('starting leftPoint: ', leftHull[rightMostIndex].x(), leftHull[rightMostIndex].y())
		#print('starting rightPoint: ', rightHull[leftMostIndex].x(), rightHull[leftMostIndex].y())
		#represents if the given side has a potential for moving around the hull more
		leftCanMove = True
		rightCanMove = True
		previousLeftHullIndex = rightMostIndex
		previousRightHullIndex = leftMostIndex
		currentLeftHullIndex = rightMostIndex
		currentRightHullIndex = leftMostIndex
		Xchange = 0
		Ychange = 0
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
				#print('currentLeftPoint ',leftHull[currentLeftHullIndex].x(),leftHull[currentLeftHullIndex].y())
				#print('currentRightPoint',rightHull[currentRightHullIndex].x(),rightHull[currentRightHullIndex].y())
				Ychange = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				Xchange = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				#print('ychange =',Ychange)
				#print('xchange = ',Xchange)
				tempSlope = Ychange/Xchange
				#print('line 121 tempSlope',tempSlope)
				#is the new slope better than previous slope
				if tempSlope < currentslope:
					currentslope = tempSlope
					#print('found a better slope on left side')
					#print('slope: ', currentslope)
					#print(" left Point:" , leftHull[currentLeftHullIndex].x(), leftHull[currentLeftHullIndex].y())
					#print('right point: ', rightHull[currentRightHullIndex].x(), rightHull[currentRightHullIndex].y())
					#since we found a better point, we know the previous point
					# won't be in our hull unless it is the original start point,
					# in which case it might be the point used by the bottom tangent

					tangentLine = []
					self.erase_tangent.emit(tangentLine)
					tangentLine.append(QLineF(leftHull[currentLeftHullIndex],rightHull[currentRightHullIndex]))
					self.show_tangent.emit(tangentLine,(0,255,0))
					#print('putting the following index onto Points in left to remove')
					#print(previousLeftHullIndex)
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
					currentslope = tempSlope
					#print('found a better slope on right side')
					#print('slope: ', currentslope)
					#print(" left Point:" , leftHull[currentLeftHullIndex].x(), leftHull[currentLeftHullIndex].y())
					#print('right point: ', rightHull[currentRightHullIndex].x(), rightHull[currentRightHullIndex].y())
					#print('line 207')
					#print('putting the following index onto Points in right to remove')
					#print(previousRightHullIndex)
					tangentLine = []
					self.erase_tangent.emit(tangentLine)
					tangentLine.append(QLineF(leftHull[currentLeftHullIndex],rightHull[currentRightHullIndex]))
					self.show_tangent.emit(tangentLine,(0,255,0))
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
		deltaY = rightHull[leftMostIndex].y()-leftHull[rightMostIndex].y()
		deltaX = rightHull[leftMostIndex].x()-leftHull[rightMostIndex].x()
		currentslope =	deltaY/deltaX
		print('currentLeftPoint ',leftHull[rightMostIndex].x(),leftHull[rightMostIndex].y())
		print('currentRightPoint',rightHull[leftMostIndex].x(),rightHull[leftMostIndex].y())
		print('original slope', currentslope)
		#print('starting slope.  That is the, the slope between the leftMost and RightMost: ', currentslope)
		#print('starting leftPoint: ', leftHull[rightMostIndex].x(), leftHull[rightMostIndex].y())
		#print('starting rightPoint: ', rightHull[leftMostIndex].x(), rightHull[leftMostIndex].y())
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
				print('currentLeftPoint ',leftHull[currentLeftHullIndex].x(),leftHull[currentLeftHullIndex].y())
				print('currentRightPoint',rightHull[currentRightHullIndex].x(),rightHull[currentRightHullIndex].y())
				#currentLeftHullIndex = moveLeftClockwise(previousLeftHullIndex, leftHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				print('line 227 tempSlope',tempSlope)
				#print('line 255 and tempslope is')
				#print(tempSlope)
				#print('line 257 and currentSlope is')
				#print(currentslope)
				#is the new slope better than previous slope
				if tempSlope > currentslope:
					currentslope = tempSlope
					#print('found a better slope on left side')
					#print('slope: ', currentslope)
					#print(" left Point:" , leftHull[currentLeftHullIndex].x(), leftHull[currentLeftHullIndex].y())
					#print('right point: ', rightHull[currentRightHullIndex].x(), rightHull[currentRightHullIndex].y())
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
				print('currentLeftPoint ',leftHull[currentLeftHullIndex].x(),leftHull[currentLeftHullIndex].y())
				print('currentRightPoint',rightHull[currentRightHullIndex].x(),rightHull[currentRightHullIndex].y())
				#currentRightHullIndex = moveRightCounterClockwise(previousRightHullIndex, rightHullOriginalY)
				#calculate slope
				deltaY = rightHull[currentRightHullIndex].y() - leftHull[currentLeftHullIndex].y()
				deltaX = rightHull[currentRightHullIndex].x() - leftHull[currentLeftHullIndex].x()
				tempSlope = deltaY/deltaX
				print('line 261currentslope ',currentslope)
				print('line 262 tempSlope',tempSlope)
				if tempSlope < currentslope:
					currentslope = tempSlope
					#print('found a better slope on right side')
					#print('slope: ', currentslope)
					#print(" left Point:" , leftHull[currentLeftHullIndex].x(), leftHull[currentLeftHullIndex].y())
					#print('right point: ', rightHull[currentRightHullIndex].x(), rightHull[currentRightHullIndex].y())
					tangentLine = []
					self.erase_tangent.emit(tangentLine)
					tangentLine.append(QLineF(leftHull[currentLeftHullIndex],rightHull[currentRightHullIndex]))
					self.show_tangent.emit(tangentLine,(0,255,0))
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
		for i in range (0,len(self.points)):
			print(self.points[i].x())

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
def makeHull(points):

	if len(points) == 3:
		print('heyo')
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

def getLeftMost(hull):

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

	#topTangent and botTangent are arrays with two valuesself.
	#the first value is the point of the left hull where the tangent connects
	#the second value is the point of the right hull where the tangent connects

def combineHalves(leftHalf, rightHalf, topTangent, botTangent):
	print('printing left hull')
	for i in leftHalf:
		print (i.x(),i.y())
	print('printing right hull')
	for i in rightHalf:
		print (i.x(), i.y())
	print('Top tangent leftPoint: ', topTangent[0].x(),topTangent[0].y())
	print('Top tangent rightPoint ', topTangent[1].x(),topTangent[1].y())
	print('Bot Tangent leftPoint', botTangent[0].x(),botTangent[0].y())
	print('Bot Tangent rightPoint', botTangent[1].x(),botTangent[1].y())

	toReturn = []
	foundTopTangent = False
	foundBotTangent = False
	i = 0
	j = 0
	for k in range (0,len(rightHalf)):
		#index where the top tangent is in the rightHalf array
		if rightHalf[k] == topTangent[1]:
			j = k
			break

	#move around left until you hit the index where top tangent connects
	while foundTopTangent == False:

		toReturn.append(leftHalf[i])
		if leftHalf[i] == topTangent[0]:
			foundTopTangent = True
		i+=1
	#move clockwise around right half until you hit where bot tangent connects
	while foundBotTangent == False:
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
	print('lin422')
	for k in range(len(leftHalf)-1, 0,-1):
		print('line 424')
		if leftHalf[k] == botTangent[0]:
			i = k
			print('line 425 and k and i = : ',k,i)
			break
	#finish moving around the bottom of the left hull from where the
	# bot tangent connects to the the starting (leftMost) point
	while i != len(leftHalf):
		toReturn.append(leftHalf[i])
		i+=1
	print()
	print()
	print()
	print('printing the combined hull')
	for i in toReturn:
		print (i.x())

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
