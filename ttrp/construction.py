#!/usr/bin/env python
# coding=utf-8

# 这一步利用启发式算法生成路径，complete 路径的稍复杂些
# 或许要画个图出来

from readdata import ReadData
from model import Model
from math import hypot, ceil
from operator import itemgetter
import random

class Construction:
    def __init__(self):
        self.AM = Model().solve() # return the values of the model, list
        self.one = ReadData("TTRP_01.txt")
        self.truck_num = 5
        self.trailer_num = 3
        self.all_locations = [['a', ['30.0', '40.0']]] + self.one.get_locations()

    # 计算两点之间的距离
    def compute_dist(self, i, j):
        for node in self.all_locations:
            if i == node[0]:
                cord_i = node[1]
            if j == node[0]:
                cord_j = node[1]
        dist_ij = hypot(float(cord_i[0]) - float(cord_j[0]),
                        float(cord_i[1]) - float(cord_j[1]))
        return dist_ij
    
    # get the five tours
    def get_tours(self):
        seqs = []
        for i in range(self.truck_num):
            seq = range(i, self.one.customer_num * self.truck_num, self.truck_num)
            seqs.append(seq)
        tours = []
        for seq in seqs:
            tour = []
            for index in seq:
                if self.AM[index] > 0.5:
                    tour.append((ceil((index + 1) / self.truck_num)) - 1) # for a standard index
            tour.append('a') # 把仓库的索引加进去（代码写的稀烂）
            tours.append(tour)
        return tours
    
    # find the closest neighbor to a given node in the tour
    def closest_neighbor(self, current_tour, node):
        dists = {}
        for cus in current_tour:
            if cus == node:
                continue
            dist = self.compute_dist(node, cus)
            dists.update({cus: dist})
        return sorted(dists.items(), key=itemgetter(1))[0][0]

    # add node k between node i and node j
    def add(self, i, j, k):
        return self.compute_dist(i, k) + self.compute_dist(k, j) - self.compute_dist(i, j)
    
    def add_closest_to_tour(self, current_tour, tour):
        best_cost, new_tour = float('inf'), None
        for k in current_tour:
            if k in tour:
                continue
            for index in range(len(tour) - 1):
                cost = self.add(tour[index], tour[index + 1], k)
                if cost < best_cost:
                    best_cost = cost
                    new_tour = tour[:index + 1] + [k] + tour[index +1:]
        return new_tour
                
    # def cheapest_insertion(self, current_tour):
    def cheapest_insertion(self, current_tour):
        # print("cheapest current tour", current_tour)
        # print(len(current_tour))
        # fuck = len(current_tour)
        # current_tour = self.get_tours()[0]
        # for tour in self.get_tours():
        if len(current_tour) == 2:
            return current_tour
        elif len(current_tour) == 1:
            return []
        starter = random.choice(current_tour)
        # print(starter)
        tour, tours = [starter], []
        neighbor = self.closest_neighbor(current_tour, starter)
        tour.append(neighbor) # 这里有了第一个 [i, j]
        # print(tour)
        while len(tour) != len(current_tour):
        # while len(tour) != fuck:    
            tour = self.add_closest_to_tour(current_tour, tour)
            tours.append(tour)
            # print(tour)
        return tour

    def tour_insertion(self):
        # for tour in self.get_tours():
        return self.cheapest_insertion(self.get_tours()[0])

    def check_route(self, tour):
        # type_list = []
        # for tour in self.get_tours():
        types = []
        for cus in tour:
            if cus == 'a':
                types.append(2)
            else:
                types.append(self.one.get_types()[cus])
            # type_list.append(types)
        return types

    def tour_length(self, tour):
        tour_length = 0.0
        if len(tour) == 0:
            return tour_length
        elif len(tour) == 1:
            return tour_length
        elif len(tour) == 2:
            return self.compute_dist(tour[0], tour[1])
        else:
            for i in range(len(tour) - 1):
                tour_length += self.compute_dist(tour[i], tour[i + 1])
            tour_length += self.compute_dist(tour[0], tour[-1]) # because it's a circle
            return tour_length

    def pure_truck(self):
        pure_truck = []
        for route in self.get_tours()[self.trailer_num:]:
            tour = self.cheapest_insertion(route)
            # pure_truck.append([tour, self.tour_length(tour)])
            pure_truck.append(tour)
        return pure_truck

    def pure_vehicle(self):
        pure_vehicle = []
        for tour in self.get_tours()[:self.trailer_num]:
            if 1 not in self.check_route(tour):
                pure_vehicle.append(tour)
        return pure_vehicle

    def main_sub(self):
        mains_subs = []
        for tour in self.get_tours()[:self.trailer_num]:
            if 1 in self.check_route(tour):
                init_main, init_sub = [], []
                for cus in tour:
                    if cus == 'a':
                        init_main.append(cus)
                    elif self.one.get_types()[cus] == 0:
                        init_main.append(cus)
                    else:
                        init_sub.append(cus)
                mains_subs.append([init_main, init_sub])
        return mains_subs

    def sub_num(self, s):
        sub_demands = 0.0
        for cus in s:
             sub_demands += self.one.get_demands()[cus] # s 中的索引和 get_demands 中的一样吗❓
        return ceil(sub_demands / self.one.truck_cap)

    # def complete_tour(self, ms):
    def complete_tour(self, ms):
        main_tour = self.cheapest_insertion(ms[0])
        # 储存所有的子路径
        # 如果只有一个子路径，查询为 subs[0]
        subs = []
        temp_s = ms[1]
        for i in range(self.sub_num(ms[1])):
            sub_demands = 0.0
            s = []
            for cus in temp_s:
                sub_demands += self.one.get_demands()[cus]
                if sub_demands < self.one.truck_cap:
                    s.append(cus)
            subs.append(s)
            # 这里是移除上面循环中符合条件的客户
            temp_s = [x for x in temp_s if x not in s]

        sub_tour = []
        for sub in subs:
            # 连接点不能是仓库，所以是 [:-1]
            connector = self.closest_neighbor(ms[0][:-1], sub[0])
            sub.append(connector)
            sub_tour.append(self.cheapest_insertion(sub))
        # complete_tours = [main_tour, sub_tour, self.tour_length(main_tour) + self.tour_length(sub_tour)]
        complete_tours = [main_tour, sub_tour]
        return complete_tours

    def all_complete_tour(self):
        complete_tours = []
        for ms in self.main_sub():
            complete_tours.append(self.complete_tour(ms))
        return  complete_tours

    '''
    def connectors(self):
        connectors = []
        for seqs in self.all_complete_tour():
            for cusi in seqs[0]:
                # sub-tour is a list of all sub-tours
                for single_tour in seqs[1]:
                    if cusi in single_tour:
                        connectors.append(cusi)
        return connectors
    '''

    def all_route(self):
        return self.pure_truck(), self.pure_vehicle(), self.all_complete_tour()
        
if __name__ == "__main__":
    c = Construction()
    # print(c.all_route())
    # print(c.tour_length())
    print(c.pure_truck(), "\n")
    print(c.pure_vehicle(), "\n")
    print(c.all_complete_tour())
    # print(len(c.all_complete_tour()), "\n")
    # print(c.connectors())