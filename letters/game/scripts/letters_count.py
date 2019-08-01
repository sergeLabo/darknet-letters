#!/usr/bin/env python3
# -*- coding: utf8 -*-


from operator import itemgetter


"""
10 parttions
1 partition
[[1,1], [1,2],  ... [1, 127],
[2,1]
...
...
[127,1], ...........[127,127]]

"""


count = {'font_0_p': 3982, 'font_0_H': 2204, 'font_0_L': 2053, 'font_0_T': 7774, 'font_0_d': 1139, 'font_0_h': 850, 'font_0_i': 1205, 'font_0_o': 1913, 'font_0_g': 1621, 'font_0_c': 1224, 'font_0_f': 1163, 'font_0_n': 1345, 'font_1_h': 592, 'font_1_p': 1556, 'font_1_H': 1122, 'font_1_L': 1246, 'font_1_T': 3924, 'font_2_h': 410, 'font_2_p': 1278, 'font_2_G': 130, 'font_2_L': 185, 'font_2_T': 3485, 'font_1_G': 235, 'font_2_H': 191, 'font_2_g': 762, 'font_1_j': 627, 'font_1_q': 952, 'font_2_j': 581, 'font_2_i': 671, 'font_0_b': 1237, 'font_1_e': 445, 'font_2_e': 961, 'font_2_q': 1725, 'font_2_d': 766, 'font_1_i': 820, 'font_0_j': 1323, 'font_0_m': 735, 'font_1_g': 1105, 'font_2_f': 163, 'font_0_q': 1585, 'font_1_o': 825, 'font_3_f': 265, 'font_3_m': 607, 'font_3_T': 1126, 'font_0_r': 1530, 'font_2_r': 320, 'font_2_b': 471, 'font_1_c': 514, 'font_1_m': 1082, 'font_1_F': 388, 'font_1_R': 786, 'font_1_f': 318, 'font_1_n': 801, 'font_7_b': 57, 'font_7_r': 57, 'font_7_G': 57, 'font_7_N': 57, 'font_0_J': 378, 'font_0_O': 169, 'font_8_c': 28, 'font_8_n': 28, 'font_8_H': 105, 'font_8_L': 105, 'font_8_T': 105, 'font_0_K': 1111, 'font_4_c': 72, 'font_4_p': 212, 'font_4_L': 367, 'font_4_T': 796, 'font_8_d': 28, 'font_8_o': 77, 'font_4_h': 121, 'font_4_o': 545, 'font_8_j': 42, 'font_4_f': 56, 'font_4_d': 9, 'font_4_i': 18, 'font_8_e': 7, 'font_7_j': 176, 'font_7_p': 114, 'font_7_T': 269, 'font_7_c': 39, 'font_7_e': 28, 'font_7_f': 11, 'font_0_S': 702, 'font_1_b': 372, 'font_0_e': 957, 'font_0_l': 137, 'font_0_E': 753, 'font_0_P': 636, 'font_1_E': 160, 'font_1_P': 168, 'font_0_I': 141, 'font_1_I': 156, 'font_1_l': 111, 'font_2_o': 1081, 'font_2_E': 493, 'font_2_P': 582, 'font_9_h': 27, 'font_9_m': 222, 'font_9_H': 330, 'font_9_L': 681, 'font_9_T': 681, 'font_7_m': 155, 'font_7_H': 9, 'font_7_L': 130, 'font_9_f': 195, 'font_7_F': 38, 'font_9_c': 72, 'font_9_n': 108, 'font_7_J': 17, 'font_7_K': 17, 'font_9_E': 344, 'font_9_B': 7, 'font_3_d': 18, 'font_3_n': 253, 'font_3_H': 492, 'font_3_L': 469, 'font_2_c': 601, 'font_2_n': 531, 'font_4_j': 391, 'font_4_H': 109, 'font_3_b': 191, 'font_3_i': 191, 'font_3_j': 95, 'font_3_l': 76, 'font_3_g': 193, 'font_4_g': 19, 'font_0_R': 1319, 'font_0_F': 244, 'font_0_Q': 644, 'font_1_d': 221, 'font_1_D': 418, 'font_2_D': 1241, 'font_2_R': 1342, 'font_3_p': 378, 'font_3_D': 369, 'font_3_R': 380, 'font_3_c': 275, 'font_0_D': 608, 'font_3_e': 114, 'font_5_d': 23, 'font_5_q': 83, 'font_5_D': 120, 'font_5_R': 137, 'font_5_e': 21, 'font_5_p': 130, 'font_5_g': 28, 'font_5_b': 15, 'font_5_i': 14, 'font_0_N': 79, 'font_0_C': 83, 'font_0_B': 344, 'font_0_G': 116, 'font_2_s': 300, 'font_2_t': 129, 'font_2_Q': 80, 'font_1_S': 146, 'font_2_C': 81, 'font_1_J': 37, 'font_1_K': 85, 'font_2_J': 44, 'font_1_B': 133, 'font_1_C': 116, 'font_1_r': 146, 'font_2_F': 64, 'font_1_N': 29, 'font_1_M': 2, 'font_2_B': 38, 'font_1_O': 22, 'font_1_Q': 106, 'font_7_h': 16, 'font_7_l': 33, 'font_7_S': 33, 'font_2_K': 382, 'font_2_O': 7, 'font_2_S': 57, 'font_2_I': 35, 'font_2_M': 1, 'font_7_i': 17, 'font_2_m': 245, 'font_0_s': 122, 'font_1_s': 3, 'font_0_M': 5, 'font_9_i': 168, 'font_9_p': 346, 'font_9_b': 1, 'font_9_q': 5, 'font_9_g': 55, 'font_9_e': 123, 'font_9_d': 4, 'font_3_o': 190, 'font_3_h': 79, 'font_3_q': 144, 'font_3_F': 17, 'font_3_S': 30, 'font_6_e': 3, 'font_6_n': 8, 'font_6_K': 8, 'font_6_T': 8, 'font_7_g': 3, 'font_7_E': 3, 'font_6_c': 5, 'font_4_K': 56, 'font_5_n': 1, 'font_5_F': 25, 'font_5_T': 1, 'font_3_r': 20, 'font_3_Q': 62, 'font_3_P': 51, 'font_3_J': 6, 'font_3_O': 17, 'font_3_E': 23, 'font_3_I': 19, 'font_4_B': 14, 'font_5_h': 45, 'font_5_I': 13, 'font_5_Q': 37, 'font_3_G': 10, 'font_5_J': 7, 'font_5_P': 7, 'font_3_C': 22, 'font_5_C': 32, 'font_5_S': 32, 'font_4_q': 39, 'font_3_M': 2, 'font_5_G': 7, 'font_4_F': 4, 'font_5_j': 14, 'font_4_J': 30, 'font_4_D': 25, 'font_5_f': 15}


def analyse():

    by_key = {k: count[k] for k in sorted(count)}
    by_value = {k: v for k,v in sorted(count.items(), key=itemgetter(1))}
    print(by_key)
    print(by_value)

if __name__ == '__main__':
    analyse()
