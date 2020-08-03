"""Get a lexicon, a dictionary convenient to look up which is split by the lengths of the words
num_per_len.json: {'1': ..., '2':, ......}
lexicon.json: {'all': ['a', ...]}
detail_i: lmdb directory storing words with size=i and the corresponding embedding, where the content is
        {'1_word': 'a', '1_emb': emb, ...} in encoded form.
"""
import os 
import collections
import json
import lmdb
import time


root = '/home/dataset/ChineseEmbedding/'
file_name = 'Tencent_AILab_ChineseEmbedding.txt'
file_path = os.path.join(root, file_name)

max_length = 14
f_detail = [os.path.join(root, 'detail_'+str(i+1)) for i in range(max_length)]
envs = [lmdb.open(fi, map_size=1099511627776) for fi in f_detail]
details = [env.begin(write=True) for env in envs]
f_num = os.path.join(root, 'num_per_len.json')
f_lexicon = os.path.join(root, 'lexicon.json')
lexicon = {'all': []}

print("Start reading {0}...".format(file_name))
time0 = time.time()

f_anomaly = os.path.join(root, 'anomaly_rec.txt')
record_anomaly = open(f_anomaly, 'w', encoding='utf-8')
f = open(file_path, 'r')
line = f.readline()
line = line.strip().split()
num_total, emb_size = int(line[0]), int(line[1])
print("The word embedding size is {0}.".format(emb_size))
cnt = 0
number = collections.defaultdict(int)
for line in f:
    cnt += 1
    if cnt % 200 == 0:
        dtime = time.time() - time0
        minutes = int(dtime)//60
        seconds = int(dtime - 60 * minutes)
        print('\r{0} words has been scaned, {1}min{2}s has been used...'.format(cnt, minutes, seconds), end='', flush=True)
    # print(line)
    # time.sleep(10)
    line = line.strip('\n').split(' ')
    word = line[0]
    # print(word)
    length = len(word)
    emb = line[1:]
    if length == 1:
        lexicon['all'].append(word)
    elif length > max_length:
        continue 
    elif any((sym in word) for sym in[',', '·', ':', '.', '&']):
        continue
    if len(emb) != emb_size:
        records = 'Embedding size is expected to be {0}, but got{1} --- when cnt={2}!'.format(emb_size, len(emb), cnt)
        record_anomaly.writelines(records + '\n')
        print('\n' + records)
        continue
    number[length] += 1
    wordKey = str(number[length]) + '_word'
    embKey = str(number[length]) + '_emb'
    details[length-1].put(wordKey.encode(), word.encode())
    details[length-1].put(embKey.encode(), str(emb).encode())

print('\n')
f.close()
record_anomaly.close()
for i in range(len(envs)):
	details[i].commit()
	envs[i].close()
print("There are {0} characters in the lexicon!".format(len(lexicon['all'])))
print("[length-num_words]:")
print(number)
print("{0}/{1} words scanned".format(cnt, num_total))
# There are 22751 characters in the lexicon!
# [length-num_words]:
# defaultdict(<class 'int'>, {4: 1968079, 1: 22751, 2: 2031081, 3: 2031553, 5: 895928, 7: 351637, 6: 677812, 8: 215757, 10: 93700, 9: 142510, 13: 20483, 11: 48557, 14: 14890, 12: 35451})
with open(f_lexicon, 'w', encoding='utf-8') as f:
    json.dump(lexicon, f, ensure_ascii=False)
with open(f_num, 'w', encoding='utf-8') as f:
    json.dump(number, f, ensure_ascii=False)
