#!/usr/bin/env python
# coding=utf-8

from descent import Descent
import random
# import A B C D # 这里考虑到要不要写一个 base 代码

class Tabu:
    def __init__(self):
        self.primer = Descent().improvement()
    
    # one-point tabu search mprovement
    def opt1(self, tr, pv, main_tours, split_sub_tours, factor, pi):
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        a_tour = tr + pv + main_tours
        b_tour = tr + pv + main_tours + split_sub_tours
        # print("b_tour of opd1:", b_tour)
        n = 0
        for route_r in a_tour:
            n += 1
            # print("R:", route_r)
            r_obj = self.tour_length(route_r)   # 看这里看这里
            best_obj = deepcopy(r_obj)          # 看这里看这里
            # pi = random.choice([5, 6, 7, 8, 9, 10])
            tabu_list = []

            for cus in route_r:
                candidates = None
                # print("I:", cus)
                if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                    continue
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                for route_s in b_tour:
                    # print("S:", route_s)
                    if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] -
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                    if (route_s in split_sub_tours) & (penalty_s > 0):
                    # if (route_s in split_sub_tours) & (theta_s > 0):
                        continue
                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    move = self.move(temp_r, temp_s, cus)
                    obj = self.tour_length(move[0])
                    # 待定义：best_obj
                    otb = False
                    # best_obj 怎么能这么写呢，肯定是搞错了
                    # 全局的 best_obj 是针对所有路径长度的，而不是 route_s 单独一条
                    if obj - best_obj >= i_factor * best_obj:
                        otb = True
                    if (penalty_s <= theta_s) & ((penalty_r < theta_r) or (otb == False)): # then(I'm not sure here)
                        if ((move not in tabu_list) or ((move in tabu_list) & (obj < best_obj))) & (obj < r_obj):
                            node_k = self.get_root(route_s, main_tours, split_sub_tours)
                            inx_l = self.route_inx(route_s, tr, pv, main_tours, split_sub_tours)
                            if len(tabu_list) > pi:
                                tabu_list.pop(-1)
                            tabu_list.append((cus, node_k, inx_l))
                            best_obj = obj
                            # a valid move is an iteration

                            for n, i in enumerate(b_tour):
                                if i == route_r:
                                    b_tour[n] = move[0]
                            for n, i in enumerate(b_tour):
                                if i == route_s:
                                    b_tour[n] = move[1]
                            if tr_len == 0:
                                tr = []
                            else:
                                tr = b_tour[:tr_len]
                            if pv_len == 0:
                                pv = []
                            else:
                                pv = b_tour[tr_len:tr_len + pv_len]
                            if mt_len == 0:
                                main_tours = []
                            else:
                                main_tours = b_tour[tr_len + pv_len:tr_len + pv_len + mt_len]
                            if sst_len == 0:
                                split_sub_tours = []
                            else:
                                split_sub_tours = b_tour[tr_len + pv_len + mt_len:]

                            # return tr, pv, main_tours, split_sub_tours, True # 看这里看这里看这里看这里
                    elif n == len(a_tour):
                        # False means no move occured in opt1
                        # print("end1 is {end} n is {nn}".format(end = len(a_tour), nn = n))
                        return tr, pv, main_tours, split_sub_tours, False

    def opt2(self, tr, pv, main_tours, split_sub_tours, factor):
        pass

    def tpt(self, tr, pv, main_tours, split_sub_tours, factor):
        pass
    
    def connectors(self, main_routes, sub_routes):
        connectors = []
        for route_i in main_routes:
            for cus_i in route_i:
                for route_j in sub_routes:
                    for cus_j in route_j:
                        if cus_i == cus_j:
                            connectors.append(cus_i)
        return connectors
    
    # get root node k
    def get_root(self, tour, main_routes, sub_routes):
        if 'a' in tour:
            k = 'a'
        else:
            connectors = self.connectors(main_routes, sub_routes)
            for node in tour:
                if node in connectors:
                    k = node
        return k

    def route_inx(self, route, tr, pv, main_tours, split_sub_tours):
        if route in tr:
            inx = 10 + tr.index(route)
        elif route in pv:
            inx = 20 + pv.index(route)
        elif route in main_tours:
            inx = 30 + main_tours.index(route)
        elif route in split_sub_tours:
            inx = 40 + split_sub_tours.index(route)
        return inx

    def searching(self):
        print("PRIMER:", self.primer)
        tr = self.primer[0]
        pv = self.primer[1]
        main_tours = self.primer[2]
        split_sub_tours = self.primer[3]
        print(tr, pv, main_tours, split_sub_tours)

        i_factor = 0.01
        pi = random.choice([5, 6, 7, 8, 9, 10])
        is_moving = True
        is_end = False # for global check

        while is_end == False:
            # stage1 intensification
            # K up to 50
            while i_factor < 0.1:
                step_one = self.opt1(tr, pv, main_tours, split_sub_tours, i_factor, pi)
                step_two = self.opt2(step_one[0], step_one[1], step_one[2], step_one[3], i_factor, pi)
                step_three = self.tpt(step_two[0], step_two[1], step_two[2], step_two[3], i_factor, pi)
                if (step_one == None) & (step_two == None) & (step_three == None):
                    i_factor += 0.01
                if (step_one == None) & (step_two == None) & (step_three == None) & (i_factor == 0.1):
                    is_moving = False
                # pi -= 1

            # stage2 descent improvement
            if is_moving == True:
                inner_des = Descent.inner_improve(step_three[0], step_three[1], step_three[2], step_three[3])
                # 当移动五次，就停下来如何？这个停止条件要定义在 inner_improve 内部

                # stage3 local clean-up and check GLS
                # inten\descen\diver 连续30次（至少），同时连续10次迭代没有出现新的更优解
                clean_up = Descent.two_opt(inner_des)
                stage1 & stage2 & stage4 performed 30 times && 10 times no move excuted:
                    is_end = True
                    return FINAL_SOLUTION

                # stage4 diversification
                # K up to 50
                d_factor = 0.1
                pi = random.choice([5, 6, 7, 8, 9, 10])
                # recieve the result from clean_up
                step_one = self.opt1(clean_up[0], clean_up[1], clean_up[2], clean_up[3], d_factor, pi)
                step_two = self.opt2(step_one[0], step_one[1], step_one[2], step_one[3], d_factor, pi)
                step_three = self.tpt(step_two[0], step_two[1], step_two[2], step_two[3], d_factor, pi)
                if (step_one == None) & (step_two == None) & (step_three == None):
                    d_factor += 0.05
                if (step_one == None) & (step_two == None) & (step_three == None) & (i_factor == 0.1):
                    is_moving = False
                
                # restart from stage1
                i_factor = 0.01

            else:
                # K up to 50
                d_factor = 0.1
                pi = random.choice([5, 6, 7, 8, 9, 10])
                # recieve the result from clean_up
                step_one = self.opt1(clean_up[0], clean_up[1], clean_up[2], clean_up[3], d_factor, pi)
                step_two = self.opt2(step_one[0], step_one[1], step_one[2], step_one[3], d_factor, pi)
                step_three = self.tpt(step_two[0], step_two[1], step_two[2], step_two[3], d_factor, pi)
                if (step_one == None) & (step_two == None) & (step_three == None):
                    d_factor += 0.05
                if (step_one == None) & (step_two == None) & (step_three == None) & (i_factor == 0.1):
                    is_moving = False
                
                # restart from stage1
                i_factor = 0.01


if __name__ == "__main__":
    t = Tabu()
    # print(t.opt1)
    print(t.searching())