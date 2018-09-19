import random



def prime_test(N, k):
    # You will need to implements this function and change the return value.

    # To generate random values for a, you will most likley want to use
    # random.randint(low,hi) which gives a random integer between low and
    #  hi, inclusive.

	# Remember to ensure that all of your random values are unique

    # Should return one of three values: 'prime', 'composite', or 'carmichael'

	mylist = [0]
	for x in range(k):
		print("In my range for loop and x = ")
		print(x)
		rand = random.randint(2,N-1)
		print(rand)
		print("HEYYYYYYYY")
		
		for y in myList:
			print("in the y list for loop")
			if y == rand:
				doNothing = 0
			else:
				mylist.append(rand)
				testResult = mod_exp(rand,N-1,N)
				if testResult != 1:
					print('returning composite')
					return 'composite'


	#Test Carmichael
	print('returning prime')
	return 'prime'


def mod_exp(x, y, N):

	if y == 0: return 1
	z = mod_exp(x,(y/2).floor,N)
	if y%2 == 0:
		return pow(z,z,N)
	else:
		return x*pow(z,z,N)


def probability(k):
	#the probability of picking a value that doesn't pass the primality test is at first 1/2
	# However, the chance of picking two in a row that fail is 1/2 * 1/2 = 1/4
	# Three in a row would be 1/2 * 1/2 *1/2 = 1/8self.
	# With inductive reasoning, it's not hard to see that the probability of picking all numbers
	#    that will fail is equal to 1/(2^k) where k is how many numbers picked.
	#for this project, this method runs in constant time
    return 1/pow(2,k)


def is_carmichael(N,a):
    # You will need to implements this function and change the return value.

	return False
