#!/usr/bin/env python
# coding=utf-8

from readdata import ReadData
from math import hypot
import cplex

one = ReadData("TTRP_01.txt")
truck_num = 5
trailer_num = 3

dists_di = []
n = 0
for i in one.get_locations():
    # (1)仓库到客户 i 的距离，存储为索引和距离的列表
    dist_di = hypot(float(one.depot_loc[0]) - float(i[1][0]), 
                    float(one.depot_loc[1]) - float(i[1][1]))
    dists_di.append([n, float(dist_di)])
    n += 1 # 保证索引从 0 开始
# print(dists_di)

# 按照与仓库的距离选 first 种子点，选10次，拿到索引
rank_dist = sorted(dists_di, key=lambda dist_di: dist_di[1])
seeds1_ind = []
dist_ds = [] # (2)存储仓库到种子点的距离值
for i in range(10):
    seeds1_ind.append(rank_dist[i][0])
    dist_ds.append(rank_dist[i][1])
# print(seeds1_ind)
# print(dist_ds)


# 选种子点集合，这部分可能在计算上有错误...
# 选择种子点，组成 seed set，根据 1st 种子点的不同，有不同的 seed set
seed_sets = []
cus_sets = []
for seed1 in seeds1_ind:
    seed_set = [seed1]
    # seed_set = [45, 10]
    # print("初始种子点:", seed_set)
    dists = []
    cus = one.get_locations()
    for i in seed_set:
        for j in cus:
            if j[0] == i:
                cus.remove(j)
    # print("初始的 cus 长度:", len(cus))
    while len(seed_set) < truck_num:
        dists_sum = []
        for i in cus:
            dist_ipsum = 0.0
            # ind_i = one.get_locations().index(i)
            dist_i = dists_di[i[0]][1]
            # print(dist_i)
            for pseed in seed_set:
                dist_ip = hypot(float(i[1][0]) - float(one.get_locations()[pseed][1][0]), 
                                float(i[1][1]) - float(one.get_locations()[pseed][1][1]))
                dist_ipsum += dist_ip
                # print(dist_ip)
                # print("ipsum:", dist_ipsum)
            dist_isum = dist_i + dist_ipsum
            dists_sum.append([i[0], dist_isum])
        # print(len(dists_sum))
        rank_sum = sorted(dists_sum, key=lambda dist_sum:dist_sum[1])
        # print(rank_sum)
        seed_set.append(rank_sum[0][0])
        for i in cus:
            if i[0] == rank_sum[0][0]:
                cus.remove(i)
        # print("这里是cus:", len(cus))
    # print(seed_set)
    seed_sets.append(seed_set)
    # print("last cus", len(cus))
    cus_sets.append(cus)
# print(len(cus_sets)) # 10组
# print(cus_sets) # 10组 每组是除了种子点的其余点
# print(seed_sets) # 10组 每组5个值（跟卡车数或者说路线数相同）

# 求解指派花费 d_ij 这里的 j 是卡车数，也其实是路径数
# cost_ij = dists_id + dist_is + dist_sd
costs_ij = []
# i 到种子点（五个索引的集合）
costs_all = []
for t in range(10):
    costs = []
    # for i in cus_sets[t]:
    #     dist_id = hypot(float(i[1][0]) - float(one.depot_loc[0]), 
    #                     float(i[1][1]) - float(one.depot_loc[1]))
    for i in dists_di:
        dist_id = i[1]
        cost = []
        for seed in seed_sets[t]:
            # dist_is = hypot(float(i[1][0]) - float(one.get_locations()[seed][1][0]), 
            #                 float(i[1][1]) - float(one.get_locations()[seed][1][1])) # 客户到各个路线的种子点的距离
            dist_is = hypot(float(one.get_locations()[i[0]][1][0]) - float(one.get_locations()[seed][1][0]), 
                            float(one.get_locations()[i[0]][1][1]) - float(one.get_locations()[seed][1][1]))
            dist_sd = hypot(float(one.get_locations()[seed][1][0]) - float(one.depot_loc[0]), 
                            float(one.get_locations()[seed][1][1]) - float(one.depot_loc[1]))
            cost_ij = dist_id + dist_is + dist_sd # 这里对每个路线下的客户 i 计算了一次 d_ij
            cost.append(cost_ij)
        # print(cost)
        # print()
        costs.extend(cost)
    costs_all.append(costs)
    # print("应该是十组之一", len(costs)) # 长度为（剔除了路线点）客户数
# print(len(costs_all)) # 10组
'''

'''
# 建立 cplex 模型
M = cplex.Cplex()
M.objective.set_sense(M.objective.sense.minimize)

my_obj = costs_all[0]
# print(my_obj)
my_rhs = [1.0] * one.customer_num + [one.truck_cap + one.trailer_cap] * trailer_num + [one.truck_cap] * (truck_num - trailer_num)


# 存储变量 x_ji
xji = []
for i in range(truck_num):
    # xi = []
    for j in range(one.customer_num):
        # xi.append("x{}_{}".format(i + 1, j + 1))
        xji.append("x{}_{}".format(j + 1, i + 1))
    # xij.append(xi)
# print(xji) # 一组一组的 j
# 存储变量 x_ij
xij = []
for i in range(one.customer_num):
    # xi = []
    for j in range(truck_num):
        # xi.append("x{}_{}".format(i + 1, j + 1))
        xij.append("x{}_{}".format(i + 1, j + 1))
# print(xij) # 一组一组的 i
# 存储行名 ri
# ri = []
# for i in range(truck_num):
#     ri.append("r{}".format(i + 1))
# print(ri)
my_rownames = []
for i in range(one.customer_num + truck_num):
    my_rownames.append("r{}".format(i + 1))
# print(my_rownames)
# print()

# constraints_sense = "E" * truck_num + "LL" * truck_num
constraints_sense = "E" * one.customer_num + "L" * trailer_num + "L" * (truck_num - trailer_num)
# print(len(xij))
# print(xij[:(trailer_num * one.customer_num)])

row_1 = []
for i in range(one.customer_num):
    row = [xij[i * truck_num : (i + 1) * truck_num], [1.0] * truck_num]
    row_1.append(row)
# print(row_1)
# print(row)
# print()

row_2 = []
for j in range(trailer_num):
    row = [xji[j * one.customer_num : (j + 1) * one.customer_num], one.get_demands()] # ⚡ one.get_demands()
    row_2.append(row)
# print(row_2)
# print(row)
# print()

row_3 = []
for j in range(trailer_num, truck_num):
    row = [xji[j * one.customer_num : (j + 1) * one.customer_num], one.get_demands()]
    row_3.append(row)
# print(row_3)

# print(len(my_obj))
# M.variables.add(obj=my_obj, types="B" * one.customer_num * truck_num, names=xij) # 松弛前，没有整数解
M.variables.add(obj=my_obj, names=xij)
rows = row_1 + row_2 + row_3
M.linear_constraints.add(lin_expr=rows, rhs=my_rhs, senses=constraints_sense, names = my_rownames)

M.solve()
M.write("test.lp")
print("Solution status :", M.solution.get_status())
print("Solution Value = ", M.solution.get_objective_value())
print("X's Value = ", M.solution.get_values())
