#!/usr/bin/env python
# coding=utf-8

from assignment import Assignment
import cplex

class Model:
    def __init__(self):
        # 建立 cplex 模型
        self.A = Assignment()
        self.M = cplex.Cplex()
        self.M.objective.set_sense(self.M.objective.sense.minimize)

        self.my_obj = self.A.costs_all()[0]
        # print(my_obj)
        self.my_rhs = [1.0] * self.A.one.customer_num + [self.A.one.truck_cap + self.A.one.trailer_cap] * self.A.trailer_num + [self.A.one.truck_cap] * (self.A.truck_num - self.A.trailer_num)

    def xji(self):
        # 存储变量 x_ji
        xji = []
        for i in range(self.A.truck_num):
            # xi = []
            for j in range(self.A.one.customer_num): # self.A.one 这儿有三层引用，会不会是因为这个造成的缓慢
                # xi.append("x{}_{}".format(i + 1, j + 1))
                xji.append("x{}_{}".format(j + 1, i + 1))
            # xij.append(xi)
        # print(xji) # 一组一组的 j
        # 存储变量 x_ij
        return xji

    def xij(self):
        xij = []
        for i in range(self.A.one.customer_num):
            # xi = []
            for j in range(self.A.truck_num):
                # xi.append("x{}_{}".format(i + 1, j + 1))
                xij.append("x{}_{}".format(i + 1, j + 1))
        # print(xij) # 一组一组的 i
        # 存储行名 ri
        # ri = []
        # for i in range(truck_num):
        #     ri.append("r{}".format(i + 1))
        # print(ri)
        return xij

    def my_rownames(self):
        my_rownames = []
        for i in range(self.A.one.customer_num + self.A.truck_num):
            my_rownames.append("r{}".format(i + 1))
        # print(my_rownames)
        # print()
        return my_rownames

    def constraints_sense(self):
        # constraints_sense = "E" * truck_num + "LL" * truck_num
        constraints_sense = "E" * self.A.one.customer_num + "L" * self.A.trailer_num + "L" * (self.A.truck_num - self.A.trailer_num)
        # print(len(xij))
        # print(xij[:(trailer_num * one.customer_num)])
        return constraints_sense

    def rows(self):
        row_1 = []
        for i in range(self.A.one.customer_num):
            row = [self.xij()[i * self.A.truck_num : (i + 1) * self.A.truck_num], [1.0] * self.A.truck_num]
            row_1.append(row)
        # print(row_1)
        # print(row)
        # print()

        row_2 = []
        for j in range(self.A.trailer_num):
            row = [self.xji()[j * self.A.one.customer_num : (j + 1) * self.A.one.customer_num], self.A.one.get_demands()] # ⚡ one.get_demands()
            row_2.append(row)
        # print(row_2)
        # print(row)
        # print()

        row_3 = []
        for j in range(self.A.trailer_num, self.A.truck_num):
            row = [self.xji()[j * self.A.one.customer_num : (j + 1) * self.A.one.customer_num], self.A.one.get_demands()]
            row_3.append(row)
        # print(row_3)

        rows = row_1 + row_2 + row_3
        return rows

    def solve(self):
        # print(len(my_obj))
        # M.variables.add(obj=my_obj, types="B" * one.customer_num * truck_num, names=xij) # 松弛前，没有整数解
        self.M.variables.add(obj=self.my_obj, names=self.xij())
        
        self.M.linear_constraints.add(lin_expr=self.rows(), rhs=self.my_rhs, senses=self.constraints_sense(), names = self.my_rownames())

        self.M.solve()
        self.M.write("test2.lp")
        # print("Solution status :", M.solution.get_status())
        # print("Solution Value = ", M.solution.get_objective_value())
        # print("X's Value = ", M.solution.get_values())
        return self.M.solution.get_values() #, self.xij()
        

if __name__ == "__main__":
    m = Model()
    print(len(m.solve()))
    print(m.solve())
