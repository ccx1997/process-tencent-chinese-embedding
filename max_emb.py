import os
from tqdm import tqdm
import numpy as np

m = 0
j=0
with open("/home/dataset/ChineseEmbedding/Tencent_AILab_ChineseEmbedding.txt",'r') as fr:
	con = fr.readlines()[1:]

	for i in tqdm(con):
		word = i.strip().split(' ')
		emb = np.array(i.strip().split(' ')[1:], dtype=np.float32) #list(map(float, a)#
		v = max(abs(emb))
		if m<v:
			m = v
			#print(word)

	print('max value',m)
	#print(j)
