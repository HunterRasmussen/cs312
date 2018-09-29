#!/usr/bin/python3
# why the shebang here, when it's imported?  Can't really be used stand alone, right?  And fermat.py didn't have one...
# this is 4-5 seconds slower on 1000000 points than Ryan's desktop...  Why?


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
		t2 = time.time()
		print('Time Elapsed (Sorting): {:3.3f} sec'.format(t2-t1))

		t3 = time.time()
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



		#  d+c(hull)
		#  if hull size == 1
		#
		#  else
		#	cut hull in half
		#	lefthull = d+c(lefthalf of cut);
		#   rightHull = d+c(rightHalf of cut);
		#
		#   topTangent = find topTangent(leftHull, rightHull);
		#   botTangent = find botTangent(leftHull, rightHull);
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
		#		removePoints(pair of top points, pair of bottom points)
		#
		#
