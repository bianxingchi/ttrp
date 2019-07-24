#!/usr/bin/env python
# coding=utf-8

from descent import Descent
from copy import deepcopy
import random

class Tabu(Descent):
    # def __init__(self):
    #     self.primer = Descent().improvement()

    # return a list stored all root nodes
    # def connectors(self, ):
    #     pass

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
        print("tr:", tr)
        print("pv:", pv)
        print("main_tours:", main_tours)
        print("split_sub_tours:", split_sub_tours, "\n")
        
        tr_len = len(tr)
        pv_len = len(pv)
        mt_len = len(main_tours)
        sst_len = len(split_sub_tours)
        a_tour = tr + pv + main_tours
        b_tour = tr + pv + main_tours + split_sub_tours
        # tabu_list = tabu # 👀003√ 唉，这已经是第三个可能的地方了

        n = 0 # max n is len(a_tour)
        for route_r in a_tour:
            n += 1
            r_obj = self.tour_length(route_r) # for comparation
            # tabu_list = [] # 👀002√ 对一个 route_r 来说，存储已经发生过的移动 (i,k,l)
            list_size = 5 # assign diffrtent number to size
            found = False # 如果在 INS 达到时，还没发现新解，就要更新 i_factor
            for cus in route_r:
                if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                    continue
                pi = random.choice([5, 6, 7, 8, 9, 10]) # pi is the searching times
                # print("Route_R:", route_r)
                print("Cus_i:", cus)
                # print("TR:", tr)
                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                # 👀 return all the possible movement (maybe not feasible) 这儿只是某一个 cus 的邻域
                # neighbors = self.opt_neighbors(cus, route_r, tr, pv, main_tours, split_sub_tours) # 本想用这种写法的
                neighborhood = []
                if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                    continue
                for route_s in b_tour:
                    if route_s == route_r or ((self.one.get_types()[cus] == 1 and (route_s in pv or route_s in main_tours)) or route_s == []):
                        continue
                    # for every customer only search pi times (the number of S is pi)
                    # pi 一定要满吗？还是说找到新解就结束当前遍历？
                    pi -= 1
                    if pi < 0:
                        break # stop current iteration and return to another cus
                    if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                        continue
                    penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] -
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                    theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                    temp_r = deepcopy(route_r)
                    temp_s = deepcopy(route_s)
                    # INPUT: temp_r temp_s OUTPUT: cr, cs
                    move = self.move(temp_r, temp_s, cus)
                    difference = self.tour_length(move[0]) + self.tour_length(move[1]) - self.tour_length(route_r) - self.tour_length(route_s)
                    immediate_obj = current_obj + difference
                    # otb = False # means that this movement's value is satisfied
                    # if immediate_obj - best_obj >= factor * best_obj:
                        # otb = True
                    # if theta_s <= penalty_s and ((penalty_r < theta_r) or (otb is False)):
                    if theta_s <= penalty_s and ((penalty_r < theta_r) or (immediate_obj - best_obj <= factor * best_obj)):    
                        if (move not in tabu_list) and (immediate_obj < current_obj):
                            # tabu_list.append(cus, )
                            print("Route_S matched:", route_s)
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
                            loops += 1
                            # break
                            print("CURRENT solution:", current_solution)
                            print("Current length:", current_obj)
                            return current_solution, factor, loops, tabu_list
                          
                            # return tr, pv, main_tours, split_sub_tours, True
                    elif n == len(a_tour):
                        # print("end1 is {end} n is {nn}".format(end = len(a_tour), nn = n))
                        # return tr, pv, main_tours, split_sub_tours, False
                        # 这里应该是通用写法，而不是只按照 0.01 的方式更新。在 diver 阶段就变了
                        # 这里的 i_factor 在最外部能否被接收，因为这里仍然处于最内的循环
                        # 0 means intensification; 1 means diversification
                        if search_type == 0:
                            factor += 0.01
                            print("→ factor updated:", factor)
                            print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list
                        elif search_type == 1:
                            factor += 0.05
                            print("→ factor updated:", factor)
                            print("No changed solution:", current_solution)
                            return current_solution, factor, loops, tabu_list


                '''    
                        iter_inten += 1
                        if immediate_obj < best_obj:
                            best_obj = immediate_obj
                        
                        elif (move in tabu_list) and (immediate_obj < best_obj) and (immediate_obj < current_obj):
                            

                    
                    neighborhood.append(move)

                    
                    
                
                
                candidate = neighbors[0] # from the best one ??? 参考的 OR 那本书

                penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                 self.one.get_demands()[cus]), 0)
                theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)

                penalty_s = max((self.tour_demand(route_s) +
                                     self.one.get_demands()[cus] -
                                     self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)

                # if candidate value < best_obj: # from the very beginning, best_obj is the length of primer
                # if candidate value < current_solution:
                    # tabu list record the (i,k,l)
                    # but candidate do not have any info about (i,k,l)
                    # 待写
                otb = False
                if obj - best_obj >= i_factor * best_obj:
                    otb = True
                if theta_s <= penalty_s and ((penalty_r < theta_r) or M IS NOT OTB
                if candidate in tabu_list:
                    if candidate value < best_obj: # meet AC
                        tabu_list.append(this movement i,k,l)
                        current_solution = candidate solution
                        best_obj = candidate value
                        inter_inten += 1 # ???
                        go ahead to next move ?
                    else:
                        candidate = neighbors[index(candidate) + 1] # try next
                        continue
                else: # not in tabu list
                    tabu_list.append(this movement i,k,l)
                    current_solution = candidate solution
                    if candidate value < best_obj:
                        best_obj = candidate value
                    inter_inten += 1 # ???
                    go ahead to next move ?
                
                
                # else: # candidate not better than the solution now
                #     update tabu_list
                #     update best_solution_ever
                #     update best_obj

                does neighbors[0] meet the tabu restriction
                    if yes: then finish one iteration
                    continue search new neighbors based on new trial solution
                    if not: increase i_factor by 0.01
                '''

    # sub-tours part
    def opt2(self, ):
        pass
    
    # two-point tabu search improvement
    def tpt(self, ):
        pass

    '''
    # get a trial customer's neighborhood by opt
    # 配合单独的 neighbors 写法的
    def opt_neighbors(self, cus, route_r, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        neighborhood = []
        if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
            continue
        for route_s in b_tour:
            if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                continue
            temp_r = deepcopy(route_r)
            temp_s = deepcopy(route_s)
            # INPUT: temp_r temp_s OUTPUT: cr, cs
            move = self.move(temp_r, temp_s, cus)
            difference = self.tour_length(move[0]) + self.tour_length(move[1]) - self.tour_length(route_r) - self.tour_length(route_s)
            immediate_obj = current_obj + difference
            neighborhood.append(move)
            
        return neighborhood # ranked from best to worst 待写一个排序

    # get a trial customer's neighborhood by tpt
    def tpt_neighbors(self, cus_i, route_r, tr, pv, main_tours, split_sub_tours):
        b_tour = tr + pv + main_tours + split_sub_tours
        neighborhood = []
        if cusi in self.connectors(main_tours, split_sub_tours) or cusi == 'a':
            continue
        for route_s in b_tour:
            if route_s == route_r:
                continue
            elif (self.one.get_types()[cusi] == 1) & (route_s in (pv or main_tours)):
                continue
            for cusj in route_s:
                if cusj in self.connectors(main_tours, split_sub_tours) or cusj == 'a':
                    continue
                elif (self.one.get_types()[cusj] == 1) & (route_s in (pv or main_tours)):
                    continue

                temp_r = deepcopy(route_r)
                temp_s = deepcopy(route_s)
                move1 = self.move(temp_r, temp_s, cusi)
                move2 = self.move(temp_s, temp_r, cusj) # only use move2's result, bcz it's exchange
    '''

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
        print("↓"*20)
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
        '''
        current_solution = primer # primer as initial solution
        current_obj = self.solution_length(primer)
        best_obj = self.solution_length(primer) # a solution's length not a route
        best_solution_ever = primer
        '''
        # pi = random.choice([5, 6, 7, 8, 9, 10]) # pi is the searching times
        is_moving = True # 当时写这个是干嘛？
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
            print("LOOP times:", loop_times)
            
            # print("TR-算子前：", tr)
            # self.opt1(tr, pv, main_tours, split_sub_tours, i_factor, primer)
            # self.opt1(i_factor, loop_times, current_solution, tabu_list)
            four_args = self.opt1(i_factor, loop_times, current_solution, tabu_list, 0)
            current_solution = four_args[0]
            i_factor = four_args[1]
            loop_times = four_args[2]
            tabu_list = four_args[3]
            print("// OUTside current solution:", current_solution)
            print("/// OUTside i_factor:", i_factor)
            print("-------"*10, "\n")
            # current_solution = self.opt1(i_factor, loop_times, primer)
            if i_factor > 0.1: # 这儿能接收到在变化的 i_factor 吗？ INS-2
                break

        # loop_times == 0 means no move accured at intensification stage
        if loop_times > 0:
            # do descent & 2-opt, then check GLS
            improved_solution = self.inner_improve(current_solution[0], current_solution[1], current_solution[2], current_solution[3])
            if GLS satisfied:
                return final_solution # searching function stop here

        loop2_times = 0
        d_factor = 0.1
        tabu_list2 = [] # 👄004 哈哈，又是一个位置
        while loop2_times < K: # K is the biggest loop INS-1
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
            print("LOOP2 times:", loop2_times)
            
            # print("TR-算子前：", tr)
            # self.opt1(tr, pv, main_tours, split_sub_tours, d_factor, primer)
            # self.opt1(d_factor, loop2_times, current_solution, tabu_list)
            four_args = self.opt1(d_factor, loop2_times, current_solution, tabu_list, 1)
            current_solution = four_args[0]
            d_factor = four_args[1]
            loop2_times = four_args[2]
            tabu_list = four_args[3]
            print("// OUTside current solution:", current_solution)
            print("/// OUTside d_factor:", d_factor)
            print("-------"*10, "\n")
            # current_solution = self.opt1(d_factor, loop2_times, primer)
            if d_factor > 0.1: # 这儿能接收到在变化的 d_factor 吗？ INS-2
                break

        '''
        while loop_times < K:
            # choose three movements randomly
            # if choice == 0:
            #     excute the code here (opt1)
            # elif choice == 1:
            #     excute the code here (opt2)
            # else:
            #     excute the code here (tpt)
            print("LOOP times:", loop_times)
            i_factor = 0.01
            
            # current_solution = input_solution # primer as initial solution
            current_obj = self.solution_length(current_solution)
            best_obj = self.solution_length(current_solution) # a solution's length not a route
            best_solution_ever = current_solution
            
            tr = current_solution[0]
            pv = current_solution[1]
            main_tours = current_solution[2]
            split_sub_tours = current_solution[3]
            print("tr:", tr)
            print("pv:", pv)
            print("main_tours:", main_tours)
            print("split_sub_tours:", split_sub_tours, "\n")
            
            tr_len = len(tr)
            pv_len = len(pv)
            mt_len = len(main_tours)
            sst_len = len(split_sub_tours)
            a_tour = tr + pv + main_tours
            b_tour = tr + pv + main_tours + split_sub_tours
            # tabu_list = [] # 👀003 唉，这已经是第三个可能的地方了

            n = 0 # max n is len(a_tour)
            for route_r in a_tour:
                n += 1
                r_obj = self.tour_length(route_r) # for comparation
                tabu_list = [] # 👀002√ 对一个 route_r 来说，存储已经发生过的移动 (i,k,l)
                list_size = 5 # assign diffrtent number to size
                found = False # 如果在 INS 达到时，还没发现新解，就要更新 i_factor
                for cus in route_r:
                    if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                        continue
                    pi = random.choice([5, 6, 7, 8, 9, 10]) # pi is the searching times
                    print("Route_R:", route_r)
                    print("Cus_i:", cus)
                    print("TR:", tr)
                    penalty_r = max((self.penalty(route_r, tr, pv, main_tours, split_sub_tours) -
                                    self.one.get_demands()[cus]), 0)
                    theta_r = self.penalty(route_r, tr, pv, main_tours, split_sub_tours)
                    # 👀 return all the possible movement (maybe not feasible) 这儿只是某一个 cus 的邻域
                    # neighbors = self.opt_neighbors(cus, route_r, tr, pv, main_tours, split_sub_tours) # 本想用这种写法的
                    neighborhood = []
                    if cus in self.connectors(main_tours, split_sub_tours) or cus == 'a':
                        continue
                    for route_s in b_tour:
                        # for every customer only search pi times (the number of S is pi)
                        # pi 一定要满吗？还是说找到新解就结束当前遍历？
                        pi -= 1
                        if pi < 0:
                            break # stop current iteration and return to another cus
                        if route_s == route_r or (self.one.get_types()[cus] == 1 & (route_s in pv or route_s in main_tours)):
                            continue
                        penalty_s = max((self.tour_demand(route_s) +
                                        self.one.get_demands()[cus] -
                                        self.tour_cap(route_s, tr, pv, main_tours, split_sub_tours)), 0)
                        theta_s = self.penalty(route_s, tr, pv, main_tours, split_sub_tours)
                        temp_r = deepcopy(route_r)
                        temp_s = deepcopy(route_s)
                        # INPUT: temp_r temp_s OUTPUT: cr, cs
                        move = self.move(temp_r, temp_s, cus)
                        difference = self.tour_length(move[0]) + self.tour_length(move[1]) - self.tour_length(route_r) - self.tour_length(route_s)
                        immediate_obj = current_obj + difference
                        # otb = False # means that this movement's value is satisfied
                        # if immediate_obj - best_obj >= factor * best_obj:
                            # otb = True
                        # if theta_s <= penalty_s and ((penalty_r < theta_r) or (otb is False)):
                        if theta_s <= penalty_s and ((penalty_r < theta_r) or (immediate_obj - best_obj <= i_factor * best_obj)):    
                            if (move not in tabu_list) and (immediate_obj < current_obj):
                                # tabu_list.append(cus, )

                                print("→ MOVE occured")
                                node_k = self.get_root(route_s, main_tours, split_sub_tours)
                                inx_l = self.route_inx(route_s, tr, pv, main_tours, split_sub_tours)
                                if len(tabu_list) > list_size:
                                    tabu_list.pop(-1)
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
                                loop_times += 1
                                # break
                                print("CURRENT solution:", current_solution, "\n")
                                return current_solution
                            
                                # return tr, pv, main_tours, split_sub_tours, True
                        elif n == len(a_tour):
                            # print("end1 is {end} n is {nn}".format(end = len(a_tour), nn = n))
                            # return tr, pv, main_tours, split_sub_tours, False
                            # 这里应该是通用写法，而不是只按照 0.01 的方式更新。在 diver 阶段就变了
                            # 这里的 i_factor 在最外部能否被接收，因为这里仍然处于最内的循环
                            i_factor += 0.01    

            print("// OUTside current solution:", current_solution)
            if i_factor == 0.1: # 这儿能接收到在变化的 i_factor 吗？ INS-2
                break
            
            

            
            # if a new better solution appears in above stage
            # perform descent to the new better solution and check DES
            # if not, then just pass?
            # input: a solution; output: a better solution
            if is_moving is True:
                inner_des = self.inner_improve(tr, pv, cv)
            
            # apply 2-opt clean-up and check GLS
            clean_up = Descent.two_opt(inner_des)
            # GLS 执行了30次；并连续10次未出现新的最优解
            if sth == 30 and sth == 10:
                return final_solution # THIS IS THE END
            
            # perform the diversification stage
            # to the best solution obtained so far and check DIS
            d_factor = 0.1
            iter_diver = 0
            if iter_diver < pi:
                目前的问题在于，各种更新要怎么组织：
                    比如更新 i_factor 和 d_factor，还要更新 tabu list，
                    更新 pi，更新 K，
                    更新...

            HOW TO RESTART from intensification?
            '''

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
    t = Tabu()
    print("\n")
    print(t.searching())



'''
candidate = self.opt_neighbors()[0] # the best one
if candidate < best_obj:
    if candidate in tabu_list:
        if candidate meet AC:
            update tabu_list
            update best_solution_ever
            update best_obj
        else:
            pass ? or continue next candidate?
    else: # not in tabu list
        update tabu_list
        update best_solution_ever
        update best_obj
else: # candidate not better than the solution now
    update tabu_list
    update best_solution_ever
    update best_obj
'''