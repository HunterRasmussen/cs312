#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import math
import time

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass


# This is the method called by the GUI.  _sequences_ is a list of the ten sequences, _table_ is a
# handle to the GUI so it can be updated as you find results, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
# how many base pairs to use in computing the alignment

	def align( self, sequences, table, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length

		# Creates a list containing 5 lists, each of 8 items, all set to 0
		#w = 8  w is column
		#h = 5; h is row
		#Matrix = [[0 for x in range(w)] for y in range(h)]
		# Matrix[0][0] = 1
		# Matrix[6][0] = 3 # error! range...
		# Matrix[0][6] = 3 # valid
        #
		# print Matrix[0][0] # prints 1
		# x, y = 0, 6
		# print Matrix[x][y] # prints 3; be careful with indexing




		# code for printing out the matrix
		# for i in range(seq2Length):
		# 	for j in range(seq1Length):
		# 		print(results[i][j], end = ' ')
		# 	print('')

		#for each pair of sequences
		for i in range(len(sequences)):
			jresults = []
			for j in range(len(sequences)):
				if banded:
					hi = 0
				else:
					seq1Length = len(sequences[i])
					seq2Length = len(sequences[j])
					#sequence 1 is the column/spans the top of the table
					#sequence 2 is the row / spans the side of the table
					#make all cells have a value 0
					results = [[0 for x in range(seq1Length)] for y in range(seq2Length)]
					pointers = [[0 for x in range(seq1Length)] for y in range(seq2Length)]

					cost = 0
					#populate 1st row with multiples of five
					for k in range(seq1Length):
						results[0][i] = cost
						cost += 5

					cost = 0
					#populate 1st column with multiples of 5
					for k in range(seq2Length):
						results[i][0] = cost
						cost +=5


					#calculate cost for the rest
					for l in range(seq2Length):
						for m in range(seq1Length):
							

				if(j < i):
					s = {}
				else:
###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
					score = i+j;
					alignment1 = 'abc-easy  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i+1,
						len(sequences[i]), align_length, ',BANDED' if banded else '')
					alignment2 = 'as-123--  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j+1,
						len(sequences[j]), align_length, ',BANDED' if banded else '')
###################################################################################################
					s = {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}
					table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
					table.repaint()
				jresults.append(s)
			results.append(jresults)
		return results
