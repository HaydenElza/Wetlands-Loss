import multiprocessing,random

def worker(num):
	"""thread worker function"""
	x = random.randint(1,10000)
	print 'Worker:', num ,"\t",
	for y in range(0,x): print y,
	print ""
	return

print "Before main"


jobs = []
for i in range(10):
	p = multiprocessing.Process(target=worker, args=(i,))
	jobs.append(p)
	p.start()
	p.join()


print "After main"