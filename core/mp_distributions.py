def worker(path1, path2, cols, num_col, input_queue, output_queue):
	'''
	Worker function spawned as a standalone Python process by the controller function.
	Requires the following parameters:
	
	path1 		- 	File path to the first dataset (reference).
	path2 		-	File path to the second dataset (comparison).
	cols  		-	A list of columns common to both datasets. 
			  		Unique values from each column are combined to
			  		generate a multi-index.
	num_col 	-	A string with a numerical column used to generate
			  		a KDE for comparison between two datasets across
			  		each multi-index generated from cols.
	input_queue -	Multiprocessing queue with multi-index permutations.
	output_queue-	Multiprocessing queue with top N results.

	Because of how processes are spawned on Windows, each worker needs its own imports

	'''
	import pandas as pd
	import numpy as np
	from scipy.stats.kde import gaussian_kde
	import matplotlib.pyplot as plt
	import heapq

	#EACH WORKER READS IN DATA INDEPENDENTLY TO AVOID SERIALIZING IT THROUGH MULTIPROCESSING
	df1 = pd.read_csv(path1)
	df2 = pd.read_csv(path2)

	#CONVERT DATAFRAME TO A DICTIONARY FOR FASTER INDEXING AND LOOKUP
	grouped1 = df1.groupby(cols)[num_col]
	grouped2 = df2.groupby(cols)[num_col]

	d1 = {index:group.values for index, group in grouped1}
	d2 = {index:group.values for index, group in grouped2}

	def figure_prep(s1, s2):
		'''
		Given two arrays return two matplotlib figures with KDE plots.
		'''
	
		s1 = s1[~np.isnan(s1)]
		s2 = s2[~np.isnan(s2)]
		
		#special case when a series is all zeroes
		if s1.sum() == 0:
			func_1 = lambda x: np.array([0.00001] * len(x))
		else:
			func_1 = gaussian_kde(s1)

		if s1.sum() == 0:
			func_2 = lambda x: np.array([0.00001] * len(x))	
		else:
			func_2 = gaussian_kde(s2)

		
		x = np.linspace(min(s1.min(), s2.min()),
						max(s1.max(), s2.max()),
						100)
		
		x_lims = (min(x), max(x))
		y_lims = (min(func_1(x).min(), func_2(x).min()), max(func_1(x).max(), func_2(x).max()))
		
		fig_1, ax_1 = plt.subplots()
		fig_2, ax_2 = plt.subplots()
		
		ax_1.axis('off')
		ax_1.set_ylim(y_lims[0], y_lims[1])
		ax_1.set_xlim(x_lims[0], x_lims[1])
		ax_1.fill_between(x, 0, func_1(x), color='red')
		
		ax_2.axis('off')
		ax_2.set_ylim(y_lims[0], y_lims[1])
		ax_2.set_xlim(x_lims[0], x_lims[1])
		ax_2.fill_between(x, 0, func_2(x), color='red')
		
		plt.close(fig='all')
		
		return fig_1, fig_2

	def image_diff(fig_A, fig_B):
		'''
		Given two matplotlib figures, output % difference from vectorized comparison.
		'''
		white = (255, 255, 255)
		red = (255, 0, 0)
		
		fig_A.canvas.draw()
		img_1 = np.frombuffer(fig_A.canvas.tostring_rgb(), dtype=np.uint8).reshape(-1, 3)
		
		fig_B.canvas.draw()
		img_2 = np.frombuffer(fig_B.canvas.tostring_rgb(), dtype=np.uint8).reshape(-1, 3)
		
		#1020 is reference area (red + red); 1530 is difference (red + white or white + red)
		result = (np.sum(np.stack((np.sum(img_1, axis=1), np.sum(img_2, axis=1)), axis=-1).sum(axis=1) == 1020) / 
				np.sum(np.stack((np.sum(img_1, axis=1), np.sum(img_2, axis=1)), axis=-1).sum(axis=1) != 1530))

		return round(result * 100, 2)

	#CREATE A HEAP QUEUE FOR PERFORMANCE BOOST! Keep top 5 permutations
	h = [(0, '_')] * 5

	while True:

		permut = input_queue.get()
		if permut is None:
			break

		#itertools.product PRODUCES ALL POSSIBLE COMBINATIONS EVEN WHEN THEY ARE NOT VALID
		try:
			if (d1[permut].shape[0] >= 10) & (d2[permut].shape[0] >= 10) & (d1[permut].sum() != 0) & (d2[permut].sum() !=0):

				heapq.heappushpop(h, (image_diff(*figure_prep(d1[permut], d2[permut])), permut))

		except KeyError:
			pass

	output_queue.put(h)

def controller(path1, path2, cols, num_col):
	'''
	Main function / process in charge of Multiprocessing. 
	Spawns worker processes to parallelize the generation and
	differencing of KDE plots for each combination of given 
	columns from two datasets being compared.
	'''

	import pandas as pd
	import numpy as np
	import itertools
	import multiprocessing as mp
	import logging
	import time
	import heapq
	import os

	cpu_num = os.cpu_count()

	mpl = mp.log_to_stderr()
	mpl.setLevel(logging.WARNING)

	df1 = pd.read_csv(path1)
	df2 = pd.read_csv(path2)

	all_permuts = itertools.product(*[np.intersect1d(df1[x].unique(), df2[x].unique()) for x in cols])

	output_queue = mp.Queue()
	input_queue = mp.Queue()

	#Load permutations into the input queue
	for permut in all_permuts:
		input_queue.put(permut)

	#Add end signals
	for i in range(cpu_num):
		input_queue.put(None)

	args = (path1, path2, cols, num_col, input_queue, output_queue)
	
	#Define worker processes (1 per CPU core)
	processes = [mp.Process(target=worker, args=args) for i in range(cpu_num)]

	for p in processes:
		p.start()

	for p in processes:
		p.join()

	result_heapq = [(0, '_')] * 5		

	result = []
	while not output_queue.empty():
		result.append(output_queue.get())

	for x in itertools.chain(*result):
		heapq.heappushpop(result_heapq, x)
		
	return(result_heapq)
		
if __name__=="mp_distributions":
	controller(path1, path2, cols, num_col)