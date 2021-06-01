import numpy as np
import sys
import pandas as pd
from scipy.sparse.linalg import svds

def RMSE(test, pred):
    result = 0
    for i in range(len(test)):
        user, item, rating = test.iloc[i]
        result += (rating - pred.loc[user][item])**2
    result /= len(test)
    result = result**(1/2)
    return result

# main start!!!!!
train_filename = 'u5.base'#sys.argv[1]
test_filename = 'u5.test'#sys.argv[2]
output_filename = train_filename + "_prediction.txt"#u1+"_prediction.txt"

#data load.
df_train = pd.read_csv('./data-2/'+train_filename, sep="\t", engine='python', encoding="cp949",
                       names=["user_id","item_id","rating","time_stamp"])
df_test = pd.read_csv('./data-2/'+test_filename, sep="\t", engine='python', encoding="cp949",
                      names=["user_id","item_id","rating","time_stamp"])

#data setting. time_stamp 는 필요 x
df_train = df_train.drop("time_stamp", 1)
df_test = df_test.drop("time_stamp", 1)
output_df = df_test.copy()

# item*user로 이루어진 행렬 생성
user_id = df_train["user_id"].unique()
user_id.sort()
train_item = list(df_train["item_id"].unique())
test_item = list(df_test["item_id"].unique())
total_item = list(set(train_item + test_item))
total_item.sort()
df_base = pd.DataFrame(data=None, columns=total_item, index = user_id)

# 각 영화에 대한 평균 값으로 빈 칸 들을 채움
for item in total_item:
    item_df = df_train[df_train["item_id"] == item]
    df_base.loc[:,item] = df_base.loc[:,item].fillna(df_train[df_train["item_id"] == item]["rating"].mean())

# 각 유저의 영화에 부여하는 점수의 평균 값을 빈칸들에 더하고, user`s mean + movie`s mean의 평균으로 빈 칸을
# 채움으로써 정보를 이용함.
for user in user_id:
    user_df = df_train[df_train["user_id"] == user]
    df_base.loc[user] = df_base.loc[user].fillna(df_train[df_train["user_id"] == user]["rating"].mean())
    df_base.loc[user] = (df_train[df_train["user_id"] == user]["rating"].mean() + df_base.loc[user])/2
    for item in user_df["item_id"].unique():
        df_base.loc[user,item] = user_df[user_df["item_id"]==item].iloc[0,2]

matrix_list = np.array(df_base.values.tolist())
matrix_list = matrix_list.astype(float)
user_rating_mean = np.mean(matrix_list, axis = 1)
matrix_list = matrix_list - user_rating_mean.reshape(-1,1)
K = 1
min_k = 0
min_rmse = 1000
min_df = None
chk = 0
while(K < 943):
    chk += 1
    U, S, Vt = svds(matrix_list, k = K)
    S = np.diag(S)
    result = U@S@Vt + user_rating_mean.reshape(-1,1)
    result = np.where(result < 1.5, 1, result)
    result = np.where(result >= 4.5, 5, result)
    result = np.around(result)
    result = pd.DataFrame(result, columns=total_item, index = user_id)
    cur_rmse = RMSE(df_test, result)
    if cur_rmse < min_rmse:
        min_rmse = cur_rmse
        min_k = K
        min_df = result
        chk = 0
    if K < 10:
        K += 1
    else:
        K += 10
    if chk > 10:
        break
    
for i in range(len(output_df)):
    us, it, not_use = output_df.iloc[i]
    output_df.iloc[i][2] = min_df.loc[us][it]

output_df.to_csv('./test/'+output_filename, sep='\t',header=None, index=False)
