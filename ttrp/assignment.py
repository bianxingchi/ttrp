#!/usr/bin/env python
# coding=utf-8

from readdata import ReadData
from math import hypot

class Assignment:
    def __init__(self):
        self.one = ReadData("TTRP_01.txt")
        self.truck_num = 5
        self.trailer_num = 3

    def costs_all(self):
        dists_di = []
        # n = 0
        for i in self.one.get_locations():
            # (1)仓库到客户 i 的距离，存储为索引和距离的列表
            dist_di = hypot(float(self.one.depot_loc[0]) - float(i[1][0]), 
                            float(self.one.depot_loc[1]) - float(i[1][1]))
            dists_di.append([i[0], float(dist_di)])
            # n += 1 # 保证索引从 0 开始
        # print(dists_di)
        # return dists_di

    # def seed_sets(self):
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
            cus = self.one.get_locations()
            for i in seed_set:
                for j in cus:
                    if j[0] == i:
                        cus.remove(j)
            # print("初始的 cus 长度:", len(cus))
            while len(seed_set) < self.truck_num:
                dists_sum = []
                for i in cus:
                    dist_ipsum = 0.0
                    # ind_i = one.get_locations().index(i)
                    dist_i = dists_di[i[0]][1]
                    # print(dist_i)
                    for pseed in seed_set:
                        dist_ip = hypot(float(i[1][0]) - float(self.one.get_locations()[pseed][1][0]), 
                                        float(i[1][1]) - float(self.one.get_locations()[pseed][1][1]))
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
        # return seed_sets

    # def costs_all(self):
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
                    dist_is = hypot(float(self.one.get_locations()[i[0]][1][0]) - float(self.one.get_locations()[seed][1][0]), 
                                    float(self.one.get_locations()[i[0]][1][1]) - float(self.one.get_locations()[seed][1][1]))
                    dist_sd = hypot(float(self.one.get_locations()[seed][1][0]) - float(self.one.depot_loc[0]), 
                                    float(self.one.get_locations()[seed][1][1]) - float(self.one.depot_loc[1]))
                    cost_ij = dist_id + dist_is + dist_sd # 这里对每个路线下的客户 i 计算了一次 d_ij
                    cost.append(cost_ij)
                # print(cost)
                # print()
                costs.extend(cost)
            costs_all.append(costs)
            # print("应该是十组之一", len(costs)) # 长度为（剔除了路线点）客户数
        # print(len(costs_all)) # 10组
        return costs_all

if __name__ == "__main__":
    A = Assignment()
    print(A.costs_all()[0], len(A.costs_all()), len(A.costs_all()[0]))
