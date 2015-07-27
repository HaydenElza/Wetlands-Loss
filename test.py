import multiprocessing,random,time

iteration = 10

def worker(num):
	"""thread worker function"""
	x = random.randint(1,10)
	time.sleep(x)
	vars()["foo"+str(num)] = 1
	print 'Worker:', num ,"sleep:",x,"foo:",vars()["foo"+str(num)]
	return

print "Before main"

jobs = []
for i in range(iteration):
	p = multiprocessing.Process(target=worker, args=(i,))
	jobs.append(p)
	p.start()
	#p.join()

print "After main"