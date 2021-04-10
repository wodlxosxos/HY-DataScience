import numpy as np
import sys
import pandas as pd

def info(df_label, data_count):
    result = 0
    for row_count in df_label.to_list():
        p = row_count/data_count
        result -= p*np.log2(p)
        
    return result


def info_gain(df, div_column):
    # label의 name과 총 data 개수 도출
    label = df.columns[-1]
    data_count = df.shape[0]
    # label과 관련된 개수 정보 추출.
    label_group = df.groupby(label).size()

    #info(D) 값 도출
    info_D = info(label_group, data_count)
    
    #info A (D) 값 도출
    info_aD = 0
    div_label_group = df.groupby(div_column).size()
    div_row_name = div_label_group.index.to_list()
    # div_column에 존재하는 value들(div_row_name)에 따라 나누어 info를 구한다.
    for row_name in div_row_name:
        div_data_count = div_label_group.loc[row_name]
        info_aD += ((div_data_count/data_count)*
                    info(df[df[div_column] == row_name].groupby(label).size(),div_data_count))

    # splitInfo A (D) 값 도출
    split_info = info(div_label_group ,data_count)
    return (info_D - info_aD)/split_info

# -----------------------------------------여까진 문제 없는 것으로 보임.

def build_dt(df, dt_model, column_name_list, new_standard):
    global label_list
    
    max_gain = -10
    max_gain_column = ''
    if df.shape[0] >= 6:
        for div_name in column_name_list:
            tmp_info_gain = info_gain(df, div_name)
            if tmp_info_gain > max_gain:
                max_gain = tmp_info_gain
                max_gain_column = div_name
    
    if (len(column_name_list) == 0) or (max_gain == 0) or (df.shape[0] < 6):
        # 현재 df에서 majority voting을 통해 뽑은 것.
        get_label = df.groupby(df.columns[-1]).size().sort_values(ascending=False).index[0]
        #-------
        dt_model[get_label].append(new_standard)
        #---------------
        #del_label_df = df.drop([df.columns[-1]], axis=1).drop_duplicates()
        #if df.shape[0] == 1:
        #    dt_model[get_label].append(df.iloc[:].values[0:-1].tolist())
        #elif df.shape[0] > 1:
        #    dt_model[get_label] += df.iloc[:].values[:,0:-1].tolist()
    else:
        column_name_list.remove(max_gain_column)
        for div_row_name in set(df[max_gain_column].values):
            tmp_standard = new_standard.copy()
            tmp_standard[max_gain_column] = div_row_name
            build_dt(df[df[max_gain_column] == div_row_name], dt_model, column_name_list.copy(),
                     tmp_standard)


# main start!!!!!
train_filename = sys.argv[1]
test_filename = sys.argv[2]
output_filename = sys.argv[3]

#train_filename = "dt_train1.txt"
#test_filename = "dt_test1.txt"
#output_filename = "dt_result1.txt"

df_train = pd.read_csv('./data/'+train_filename, sep="\t", engine='python', encoding="cp949")
df_test = pd.read_csv('./data/'+test_filename, sep="\t", engine='python', encoding="cp949")

column_name_list = list(df_train.columns)
column_name_list.pop()

label_list = list(np.unique(df_train[df_train.columns[-1]].values))
dt_model = {}
for tmp_label in label_list:
    dt_model[tmp_label] = []
    
build_dt(df_train, dt_model, column_name_list, {})

total_nan = 0
#test data 전처리
for column_name in column_name_list:
    print(set(df_test[column_name].values), set(df_train[column_name].values))
    rest = set(df_test[column_name].values) - set(df_train[column_name].values)
    if len(rest) > 0:
        for rest_column_name in rest:
            total_nan += 1
            df_test[df[column_name] == rest_column_name] = df_train.groupby(
                column_name).size().sort_values(ascending=False).index[0]


df_test[df_train.columns[-1]] = ""
for i in range(df_test.shape[0]):
    for tmp_label in label_list:
        tmp_df_test = df_test.iloc[i]
        chk = 1
        for standard in dt_model[tmp_label]:
            chk2 = True
            for key in standard.keys():
                if standard[key] != tmp_df_test[key]:
                    chk2 = False
                    break
            if chk2:
                df_test[df_train.columns[-1]].iloc[i] = tmp_label
                break

df_test.to_csv(output_filename, sep='\t', index=False)
