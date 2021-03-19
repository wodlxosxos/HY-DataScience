from itertools import combinations
import sys

#편의를 위해 element가 1개인 frequent를 먼저 구한 후, element가 2개인 것을 apriori함수를 이용하여 구했습니다.
def apriori(total_item_set, min_sup, transaction_list):
    item_number = 1
    while(1):        
        #기존의 candidate를 비우고, item_number+1개의 원소를 갖는 candidate을 뽑는다.
        sorted_total_item = sorted(total_item_set[item_number - 1])
        candidate_item_set = []
        for first_src in sorted_total_item:
            for second_src in sorted_total_item:
                tmp_union_set = sorted(list(set().union(first_src, second_src)))
                if ((len(tmp_union_set) == item_number+1) and
                    (tmp_union_set not in candidate_item_set)):
                    candidate_item_set.append(tmp_union_set)

        # 1차 candidate에서 전 단계의 item_set에 자신의 하위 조합이 하나라도 없는
        # 경우 delete
        for candidate in candidate_item_set:
            child_list = list(combinations(candidate,item_number))
            no_qualify = True
            for child in child_list:
                if child not in sorted(total_item_set[item_number-1]):
                    no_qualify = False
                    break
            if no_qualify == False:
                del candidate_item_set[candidate_item_set.index(candidate)]

        # 더 이상 candidate가 없을 때 함수 종료.
        if len(candidate_item_set) == 0:
            break
        
        #출현 빈도 조회하여 frequent_item_set에 저장.
        frequent_item_set = {}
        for transaction in transaction_list:
            for src in candidate_item_set:
                src = tuple(src)
                if len(set().union(src, transaction)) == len(transaction):
                    if src in frequent_item_set:
                        frequent_item_set[src] += 1
                    else:
                        frequent_item_set[src] = 1

        # support값을 못 넘길 시 frequent목록에서 제외.
        for key in tuple(frequent_item_set.keys()):
            if frequent_item_set[key] < min_sup :
                del frequent_item_set[key]
        
        total_item_set.append(frequent_item_set.copy())
        item_number += 1

def association(total_item_set, transaction_num):
    result_str = ""
    for i in range(1, len(total_item_set)):
        for item in total_item_set[i]:
            for size in range(1, i+1):
                tmp_comb = list(combinations(item, size))
                for left_item in tmp_comb:
                    right_item = list(item).copy()
                    right_item = tuple([x for x in right_item if x not in left_item])
                    set_left_item = set(left_item)
                    set_right_item = set(right_item)
                    support = format((total_item_set[i][item]/transaction_num)*100, ".2f")
                    confidence = format((total_item_set[i][item]/total_item_set[len(set_left_item)-1][left_item])*100, ".2f")
                    result_str += f"{set_left_item}\t{set_right_item}\t"+support+"\t"+ confidence +"\n"
    return result_str.rstrip("\n")

if __name__ == "__main__":
    min_sup = int(sys.argv[1])
    filename = sys.argv[2]
    output_filename = sys.argv[3]

    min_sup = 100/min_sup
    f = open("./" + filename,'r')
    total_list = f.readlines()

    transaction_list = []

    for src in total_list:
        line = src.replace("\n","").split('\t')
        transaction_list.append(list(map(int, line)))

    transaction_num = len(total_list)

    if len(transaction_list) > 0:
        #apriori 1: item 1개인 set 구하기
        total_item_set = []
        item_set = {}
        for transaction in transaction_list:
            for src in transaction:
                src = tuple([src])
                if src in item_set:
                    item_set[src] += 1
                else:
                    item_set[src] = 1
        
        #min_sup = sum(item_set.values())/20
        min_frequency = len(transaction_list)/min_sup

        for key in list(item_set.keys()):
            if item_set[key] < min_frequency :
                del item_set[key]
        
        total_item_set.append(item_set)
        
        #apriori 2: item 2개인 set부터 반복
        apriori(total_item_set, min_frequency, transaction_list)

        #association rule : output 작성.
        result_str = association(total_item_set, transaction_num)

        output_file = open("./"+output_filename, 'w')
        output_file.write(result_str)

        f.close()
        output_file.close()
