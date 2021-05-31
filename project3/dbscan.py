import numpy as np
import pandas as pd
import sys
from collections import deque

def dist(x1,y1,x2,y2):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)


filename = sys.argv[1]
n = int(sys.argv[2])
Eps = int(sys.argv[3])
MinPts = int(sys.argv[4])

base_df = pd.read_csv("./data-3/" + filename, sep='\t', engine='python', names=[
    'id','x','y'])
id_list = base_df["id"].unique()
base_df = pd.DataFrame(data=base_df.iloc[:,1:3], columns=['x','y'], index=id_list)

id_list = deque(id_list)
id_chk = {}
for i in id_list:
    id_chk[i] = 1
q = id_list.popleft()
id_chk[q] = 0
x,y = base_df.loc[q]
queue = deque([[q,x,y]])

result = []
cluster = []
not_border = []
while(1):
    chk = []
    cur_id, x, y = queue.popleft()
    if len(cluster) == 0:
        cluster.append(cur_id)
    
    cur_df = base_df[(abs(base_df["x"] - x) <= Eps) & (abs(base_df["y"] - y) <= Eps)]
    
    for j in cur_df.index:
        x2, y2 = cur_df.loc[j]
        if dist(x,y,x2,y2) <= Eps:
            chk.append([j,x2,y2])
    
    if len(chk) >= MinPts:
        for t in chk:
            if id_chk[t[0]] == 1:
                id_chk[t[0]] = 0
                id_list.remove(t[0])
                queue.append(t)
            cluster.append(t[0])
        not_border.append(cur_id)
    
    if len(id_list) == 0:
        result.append(cluster)
        break
    if len(queue) == 0:
        cluster = list(set(cluster))
        result.append(cluster)
        if len(cluster) >= MinPts:
            base_df = base_df.drop(not_border)
        cluster = []
        not_border = []
        tmp_id = id_list.popleft()
        id_chk[tmp_id] = 0
        tmp_x, tmp_y = base_df.loc[tmp_id]
        queue.append([tmp_id, tmp_x, tmp_y])

s_result = sorted(result, key=lambda x:len(x), reverse=True)[0:n]
name = filename[0:6]
for i in range(n):
    f = open('./test-3/'+name+'_cluster_'+str(i)+'.txt', 'w')
    result_df = pd.DataFrame(s_result[i])
    result_df.to_csv('./test-3/'+name+'_cluster_'+str(i)+'.txt', header=None, index=False)

