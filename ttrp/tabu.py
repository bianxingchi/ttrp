#!/usr/bin/env python
# coding=utf-8

from descent import Descent
from innerdescent import Innerdescent
from copy import deepcopy
import random
import time

class Tabu(Descent):
    # get the root node k of input route
    def get_root(self, tour, main_routes, sub_routes):
        if 'a' in tour:
            k = 'a'
        else:
            connectors = self.connectors(main_routes, sub_routes)
            for node in tour:
                if node in connectors:
                    k = node
        return k

    # get a route's index
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

    # compute all routes' length
    def solution_length(self, solution):
        length = 0.0
        for route_list in solution:
            for route in route_list:
                length += self.tour_length(route)
        return length
    
    # one-point tabu search improvement
    # non-sub-tours part
    # def opt1(self, tr, pv, main_tours, split_sub_tours, factor, input_solution):
    def opt1(self, factor, loops, input_solution, tabu_list, search_type):
        current_solution = input_solution # primer as initial solution
        current_obj = self.solution_length(input_solution)
        best_obj = self.solution_length(input_solution) # a solution's length not a route
        best_solution_ever = input_solution
        
        tr = current_solution[0]
        pv = current_solution[1]
        main_tours = current_solution[2]
        split_sub_tours = current_solution[3]
        print("TABU opt1 part ===========")
        # print("tr:", tr)
        # print("pv:", pv)
        # print("main_tours:", main_tours)
        # print("split_sub_tours:", split_sub_tours, "\n")
        
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        a_tour = tr + pv + main_tours
        b_tour = tr + pv + main_tours + split_sub_tours
        # tabu_list = tabu # 👀003√ 唉，这已经是第三个可能的地方了

        n = 0 # count customer visited
        for route_r in a_tour:
            # print("len(a_tour) & n:", len(a_tour), n)
            r_obj = self.tour_length(route_r) # for comparation
            # tabu_list = [] # 👀002√ 对一个 route_r 来说，存储已经发生过的移动 (i,k,l)
            list_size = 5 # assign diffrtent number to size
            found = False # 如果在 INS 达到时，还没发现新解，就要更新 i_factor
            for cus in route_r:
                n += 1
                # print("Cus_i (tabu.opt1):", cus) # 🚨 频繁打印位
                if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                    # print("{} skiped".format(cus))
                    if n == sum([len(x) for x in a_tour]):
                        if search_type == 0:
                            print("↘ snap 010")
                            factor += 0.01
                            print("→ i_factor updated:", factor)
                            # print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list
                        elif search_type == 1:
                            print("↘ snap 011")
                            factor += 0.05
                            print("→ d_factor updated:", factor)
                            # print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list
                    else:
                        continue
                # print("Route_R:", route_r)
                # print("TR:", tr)
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                # 👀 return all the possible movement (maybe not feasible) 这儿只是某一个 cus 的邻域
                # neighbors = self.opt_neighbors(cus, route_r, tr, pv, main_tours, split_sub_tours) # 本想用这种写法的
                neighborhood = []
                if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                    # print("{} skiped".format(cus))
                    continue
                pi = random.choice([5, 6, 7, 8, 9, 10]) # pi is the searching times
                if pi >= len(b_tour):
                    pi = len(b_tour) - 1
                # print("↘B_tour:", b_tour)
                # print("PI initial:", pi)
                for route_s in b_tour:
                    pi -= 1
                    # print("Route_S:", route_s)
                    # for every customer only search pi times (the number of S is pi)
                    # pi 一定要满吗？还是说找到新解就结束当前遍历？
                    # print("route_s have searched {time} times".format(time = pi))
                    # ❌❌❌
                    if pi < 0 and n == sum([len(x) for x in a_tour]):
                        print("↘ ViSiTeD AlL CuStOmEr (in b_tour)")
                        if search_type == 0:
                            print("THIS is intensification stage")
                            factor += 0.01
                            print("→ i_factor updated:", factor)
                            # print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list
                        elif search_type == 1:
                            print("THIS is diversification stage")
                            factor += 0.05
                            print("→ d_factor updated:", factor)
                            # print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list
                    elif pi < 0:
                        # print("↘ route_s searched PI times")
                        break # stop current iteration and return to another cus

                    if route_s == route_r or ((self.one.get_types()[cus] == 1 and (route_s in pv or route_s in main_tours)) or route_s == []):
                        # print("routeS {} skiped".format(route_s))
                        # print(pi, n, sum([len(x) for x in a_tour]))
                        continue
                    if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                        # print("↘001")
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] -
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    # INPUT: temp_r temp_s OUTPUT: cr, cs
                    move = self.move(temp_r, temp_s, cus)
                    # 这里的比较是否不严谨，因为可能造成除交换的两条路径之外的其他路径的变化
                    # ❓❓❓
                    difference = self.tour_length(move[0]) + self.tour_length(move[1]) - self.tour_length(route_r) - self.tour_length(route_s)
                    immediate_obj = current_obj + difference
                    # otb = False # means that this movement's value is satisfied
                    # if immediate_obj - best_obj >= factor * best_obj:
                        # otb = True
                    # if theta_s <= penalty_s and ((penalty_r < theta_r) or (otb is False)):
                    # print("↘GAP of best:", immediate_obj - best_obj)
                    # print("↘GAP of factor:", factor * best_obj)
                    # ===========================================================
                    # 这里的判定判定判定条件是否有问题，因为 d_factor 下走不动
                    # ❌❌❌❌❌❌
                    # if theta_s <= penalty_s and ((penalty_r < theta_r) or (immediate_obj - best_obj <= factor * best_obj)) and (move not in tabu_list) and (immediate_obj < current_obj):
                    #     print(theta_s <= penalty_s, ((penalty_r < theta_r) or (immediate_obj - best_obj <= factor * best_obj)), (move not in tabu_list), (immediate_obj < current_obj))
                    # print(penalty_s <= 0, (penalty_r <= 0 or (immediate_obj - best_obj <= factor * best_obj)), (move not in tabu_list), (immediate_obj < current_obj))
                    # if penalty_s <= 0 and penalty_r <= 0 and (immediate_obj - best_obj <= factor * best_obj) and (move not in tabu_list):
                    # if (theta_s <= penalty_s) and ((penalty_r < theta_r) or (immediate_obj - best_obj <= factor * best_obj)) and ((move not in tabu_list) or (move in tabu_list and immediate_obj < best_obj)) and (immediate_obj < current_obj):
                    if (theta_s <= penalty_s) and ((penalty_r < theta_r) or (immediate_obj - best_obj <= factor * best_obj)) and ((move not in tabu_list) or (move in tabu_list and immediate_obj < best_obj)) and penalty_s <= 0 and penalty_r <= 0:
                        # tabu_list.append(cus, )
                        # print("Route_S matched:", route_s)
                        print("→ MOVE occured")
                        node_k = self.get_root(route_s, main_tours, split_sub_tours)
                        inx_l = self.route_inx(route_s, tr, pv, main_tours, split_sub_tours)
                        if len(tabu_list) > list_size:
                            tabu_list.pop(0)
                        tabu_list.append((cus, node_k, inx_l))

                        current_obj = immediate_obj
                        # update current solution
                        # then prepare for next interation
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
                        
                        current_solution = [tr, pv, main_tours, split_sub_tours] # 在这更新的要让上面的 a_tour 接收到并且基于新的 current_solution 重新开始搜索
                        if current_obj < best_obj:
                            best_obj = current_obj
                        loops += 1
                        # break
                        print("CURRENT solution:", current_solution)
                        print("Current length:", current_obj)
                        return current_solution, factor, loops, tabu_list
                          
                            # return tr, pv, main_tours, split_sub_tours, True
                    elif n == sum([len(x) for x in a_tour]):
                        # print("↘ ViSiTeD AlL CuStOmEr")
                        # print("end1 is {end} n is {nn}".format(end = len(a_tour), nn = n))
                        # return tr, pv, main_tours, split_sub_tours, False
                        # 这里应该是通用写法，而不是只按照 0.01 的方式更新。在 diver 阶段就变了
                        # 这里的 i_factor 在最外部能否被接收，因为这里仍然处于最内的循环
                        # 0 means intensification; 1 means diversification
                        if search_type == 0:
                            factor += 0.01
                            print("→ i_factor updated:", factor)
                            # print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list
                        elif search_type == 1:
                            factor += 0.05
                            print("→ d_factor updated:", factor)
                            # print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list

    # sub-tours part
    def opt2(self, ):
        pass
    
    # two-point tabu search improvement
    def tpt(self, ):
        pass

    # searching part
    # set K as 10/20/30/40/50, K is the search times
    def searching(self):
        # primer = Descent().improvement()
        # primer = self.improvement()
        current_solution = self.improvement()
        print("======="*10)
        print("PRIMER:", current_solution, "\n")
        print("PRIMER's length:", self.solution_length(current_solution))
        print()
        print("↘"*20)
        # tr = primer[0]
        # pv = primer[1]
        # main_tours = primer[2]
        # split_sub_tours = primer[3]
        # print("tr:", tr)
        # print("pv:", pv)
        # print("main_tours:", main_tours)
        # print("split_sub_tours:", split_sub_tours, "\n")

        # apply the intensification stage to solution
        # and check INS 💔 I DO NOT KNOW HOW TO APPLY THIS INS
        # pi = random.choice([5, 6, 7, 8, 9, 10]) # pi is the searching times
        # is_moving = True # 当时写这个是干嘛？
        loop_times = 0
        K = 50 # K can be 10/20/30/40/50
        i_factor = 0.01
        tabu_list = [] # 👄004 哈哈，又是一个位置
        i_times = 0
        d_times = 0
        id_times = 0
        
        while loop_times < K: # K is the biggest loop INS-1
            # iter_inten = 0
            # if iter_inten <= pi:
                # tabu_list = [] # 👀001 这里不应该放禁忌表吧，太外层了
                # choose one of the movement strategy
            
            # ch = random.choice([1, 2])
            # if ch == 1: # use opt
            #     # ??? this one first
            #     self.opt1(tr, pv, main_tours, split_sub_tours, factor, pi)
            #     # then sub_tour part???
            #     self.opt2()
            # elif ch == 2: # choose tpt_neighbors
            #     self.tpt()
            # print("LOOP times:", loop_times)
            
            # print("TR-算子前：", tr)
            # self.opt1(tr, pv, main_tours, split_sub_tours, i_factor, primer)
            # self.opt1(i_factor, loop_times, current_solution, tabu_list)
            four_args = self.opt1(i_factor, loop_times, current_solution, tabu_list, 0)
            current_solution = four_args[0]
            i_factor = four_args[1]
            loop_times = four_args[2]
            tabu_list = four_args[3]
            # print("// OUTside current solution:", current_solution)
            # print("/// OUTside i_factor:", i_factor)
            print("-------"*10, "\n")
            # current_solution = self.opt1(i_factor, loop_times, primer)
            if i_factor > 0.1: # 这儿能接收到在变化的 i_factor 吗？ INS-2
                i_times += 1
                break

        # loop_times == 0 means no move accured at intensification stage
        if loop_times > 0:
            d_times += 1
            print("进入 inten 阶段的 inner-descent")
            # do descent & 2-opt, then check GLS
            improved_solution = Innerdescent().inner_improve(current_solution[0], current_solution[1], current_solution[2], current_solution[3])
            print("迭代次数统计：", i_times + d_times)
            # ❗ ❗ ❗
            # if i_times + d_times + id_times > 30:
            if i_times + d_times > 3:
                print("ALL DONE ! ! ! ! ! !")
                return improved_solution
            # print("→ Not set GLS & return directly ↓")
            # return improved_solution

            else:
                print("操！")
                self.diversification(current_solution)
        

    def diversification(self, current_solution):
        
        loop2_times = 0
        d_factor = 0.1
        tabu_list2 = [] # 👄004 哈哈，又是一个位置
        i_times = 0
        d_times = 0
        id_times = 0
        
        # ============================================
        # DIVER part
        while loop2_times < 1: # K is the biggest loop INS-1
            d_times += 1
            # iter_inten = 0
            # if iter_inten <= pi:
                # tabu_list2 = [] # 👀001 这里不应该放禁忌表吧，太外层了
                # choose one of the movement strategy
            
            # ch = random.choice([1, 2])
            # if ch == 1: # use opt
            #     # ??? this one first
            #     self.opt1(tr, pv, main_tours, split_sub_tours, factor, pi)
            #     # then sub_tour part???
            #     self.opt2()
            # elif ch == 2: # choose tpt_neighbors
            #     self.tpt()
            # print("LOOP2 times:", loop2_times)
            
            # print("TR-算子前：", tr)
            # self.opt1(tr, pv, main_tours, split_sub_tours, d_factor, primer)
            # self.opt1(d_factor, loop2_times, current_solution, tabu_list2)
            four_args = self.opt1(d_factor, loop2_times, current_solution, tabu_list2, 1)
            print("/ four args:", four_args)
            current_solution = four_args[0]
            d_factor = four_args[1]
            loop2_times = four_args[2]
            tabu_list2 = four_args[3]
            print("// OUTside current solution:", current_solution)
            # print("/// OUTside d_factor:", d_factor)
            print("-------"*10, "\n")
            # current_solution = self.opt1(d_factor, loop2_times, primer)
            # if d_factor > 0.1: # 这儿能接收到在变化的 d_factor 吗？ INS-2
            #     break

        # =======================================================
        # restart from intensification    
        loop_times = 0
        K = 50 # K can be 10/20/30/40/50
        i_factor = 0.01
        tabu_list = [] # 👄004 哈哈，又是一个位置
        while loop_times < K: # K is the biggest loop INS-1
            # iter_inten = 0
            # if iter_inten <= pi:
                # tabu_list = [] # 👀001 这里不应该放禁忌表吧，太外层了
                # choose one of the movement strategy
            
            # ch = random.choice([1, 2])
            # if ch == 1: # use opt
            #     # ??? this one first
            #     self.opt1(tr, pv, main_tours, split_sub_tours, factor, pi)
            #     # then sub_tour part???
            #     self.opt2()
            # elif ch == 2: # choose tpt_neighbors
            #     self.tpt()
            # print("LOOP times:", loop_times)
            
            # print("TR-算子前：", tr)
            # self.opt1(tr, pv, main_tours, split_sub_tours, i_factor, primer)
            # self.opt1(i_factor, loop_times, current_solution, tabu_list)
            four_args = self.opt1(i_factor, loop_times, current_solution, tabu_list, 0)
            current_solution = four_args[0]
            i_factor = four_args[1]
            loop_times = four_args[2]
            tabu_list = four_args[3]
            print("// OUTside current solution:", current_solution)
            # print("/// OUTside i_factor:", i_factor)
            print("-------"*10, "\n")
            # current_solution = self.opt1(i_factor, loop_times, primer)
            if i_factor > 0.1: # 这儿能接收到在变化的 i_factor 吗？ INS-2
                i_times += 1
                break

        # loop_times == 0 means no move accured at intensification stage
        if loop_times > 0:
            d_times += 1
            # do descent & 2-opt, then check GLS
            print("进入 diver 部分的 inner-descent 阶段")
            improved_solution = Innerdescent().inner_improve(current_solution[0], current_solution[1], current_solution[2], current_solution[3])
            # ❗ ❗ ❗
            # if i_times + d_times + id_times > 30 and no_move_times > 10:
            # if i_times + d_times + id_times > 30:
            print("迭代次数统计：", i_times + d_times)
            if i_times + d_times > 3:
                print("ALL DONE ! ! ! ! ! !")
                
                return improved_solution
            else:
                print("操！")
                self.diversification(current_solution)
            # print("→ Not set GLS & return directly (after diversification) ↓")
            # return improved_solution
        
    def run(self):
        count = 0
        while count < 10:
            self.searching()
            count += 1
            return 
        while count < 20:
            self.searching()
            count += 1
            return 
        while count < 30:
            self.searching()
            count += 1
            return 
        while count < 40:
            self.searching()
            count += 1
            return 
        while count < 50:
            self.searching()
            count += 1
            return 

if __name__ == "__main__":
    start_time = time.time()
    t = Tabu()
    print("\n")
    print(t.searching())
    print("--- %s seconds ---" % (time.time() - start_time))
