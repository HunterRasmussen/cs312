import random
import math

def prime_test(N, k):

	#for loop 1 takes a constant k iterations  so k time
	##for loop 2 can take infinitely long depending on the luck of the draw
	#	but probability says it will run at constant or near constant time
	# mod_exp takes
	# carmichael take
	#since carmichael is only run when the fermat fails, it will only run about
	#	50% of the time.  But since 1/2 is a constant, we drop it in the long run

	# so in total, the run time of prime_test = k*c*
	mylist = [0]
	for x in range(k):
		print(x)
		rand = random.randint(2,N-1)
		print("rand = " ,rand)
		for y in mylist:
			if y != rand:
				mylist.append(rand)
				testResult = mod_exp(rand,N-1,N)
				if testResult != 1:
					return 'composite'
				else:
					print("ENTERINT CARMICHAEL")
					carResult = is_carmichael(N,rand)
					if(carResult):
						return 'carmichael'
	return 'prime'


def mod_exp(x, y, N):

	#This method requires log y iterations
	#it requires 2 mods per iterations
	#it requires 1 multiplication

	#this is just a copy of the algorithm in the book. No explanation needed
	if y == 0: return 1
	z = mod_exp(x,math.floor(y/2),N)
	if y%2 == 0:
		temp = z*z
		return temp%N
	else:
		temp = x*z*z
		return temp%N


def probability(k):
	#the probability of picking a value that doesn't pass the primality test is at first 1/2
	# However, the chance of picking two in a row that fail is 1/2 * 1/2 = 1/4
	# Three in a row would be 1/2 * 1/2 *1/2 = 1/8self.
	# With inductive reasoning, it's not hard to see that the probability of picking all numbers
	#    that will fail is equal to 1/(2^k) where k is how many numbers picked.
	#for this project, this method runs in constant time
    return 1/pow(2,k)


def is_carmichael(N,a):

	#there are logN iterations of carmichael at worst case because N gets cut
	#	 in half each time.



	#base case
	if N/2 == 1:
		return false;
	z = mod_exp(a,N-1,N)
	if z == 1:
		return is_carmichael(N/2,a)
	if z == -1:
		return false;
	else:
		return True;
