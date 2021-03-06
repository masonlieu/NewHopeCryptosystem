# Final Project PMAT 429
# Author: Mason Lieu
# ID: 10110089
# Date: April 13th, 2018
# Description: - This is a NewHope implementation according to the specifications in the supporting documents
# of the NIST proposed post-quantum cryptosystem: https://csrc.nist.gov/Projects/Post-Quantum-Cryptography/Round-1-Submissions
# - Creates the public and private keys, encrypts and decrypts a 32-byte message
#
# To run: python main.py <debug>


import logging
import os
import sys
import hashlib
import random
from logging import debug, warning, info
import datetime as dt

NEWHOPE_N = 1024      # Security level of 233 (sect. 1.3 of NewHope supporting document)
NEWHOPE_N_INV = 12277   # inverse of n
NEWHOPE_7N_4 = 1792     # 7n/4
NEWHOPE_3N_8 = 384      # 3n/4
NEWHOPE_Q = 12289     # Smallest prime st. q = 1 (mod 2n) so that NTT can be realized efficiently (sect. 1.3)
NEWHOPE_K  =8         # Distribution of RLWE secret using centered binomial distribution of parameter k=8 (sect. 1.3)
NEWHOPE_ROOT = 10302    # square root of nth root of unity
SQUEEZE_BLOCK_SIZE = 168    # block size of SHAKE output

# # Precomputed powers of nth root of unity
# psi_bitrev = [8193, 493, 6845, 9908, 1378, 10377, 7952, 435, 10146, 1065, 404, 7644, 1207, 3248, 11121, 5277, 2437, 3646, 2987, 6022, 9867, 6250, 10102, 9723, 1002, 7278, 4284, 7201,
#     875, 3780, 1607, 4976, 8146, 4714, 242, 1537, 3704, 9611, 5019, 545, 5084, 10657, 4885, 11272, 3066, 12262, 3763, 10849, 2912, 5698, 11935, 4861, 7277, 9808, 11244, 2859,
#     7188, 1067, 2401, 11847, 390, 11516, 8511, 3833, 2780, 7094, 4895, 1484, 2305, 5042, 8236, 2645, 7875, 9442, 2174, 7917, 1689, 3364, 4057, 3271, 10863, 4654, 1777, 10626,
#     3636, 7351, 9585, 6998, 160, 3149, 4437, 12286, 10123, 3915, 7370, 12176, 4048, 2249, 2884, 1153, 9103, 6882, 2126, 10659, 3510, 5332, 2865, 9919, 9320, 8311, 9603, 9042,
#     3016, 12046, 9289, 11618, 7098, 3136, 9890, 3400, 2178, 1544, 5559, 420, 8304, 4905, 476, 3531, 9326, 4896, 9923, 3051, 3091, 81, 1000, 4320, 1177, 8034, 9521, 10654, 11563,
#     7678, 10436, 12149, 3014, 9088, 5086, 1326, 11119, 2319, 11334, 790, 2747, 7443, 3135, 3712, 1062, 9995, 7484, 8736, 9283, 2744, 11726, 2975, 9664, 949, 7468, 9650, 7266,
#     5828, 6561, 7698, 3328, 6512, 1351, 7311, 8155, 5736, 722, 10984, 4043, 7143, 10810, 1, 8668, 2545, 3504, 8747, 11077, 1646, 9094, 5860, 1759, 8582, 3694, 7110, 8907, 11934,
#     8058, 9741, 9558, 3932, 5911, 4890, 3637, 8830, 5542, 12144, 5755, 7657, 7901, 11029, 11955, 9863, 10861, 1696, 3284, 2881, 7197, 2089, 9000, 2013, 729, 9048, 11809, 2842,
#     11267, 9, 6498, 544, 2468, 339, 1381, 2525, 8112, 3584, 6958, 4989, 10616, 8011, 5374, 9452, 12159, 4354, 9893, 7837, 3296, 8340, 7222, 2197, 118, 2476, 5767, 827, 8541,
#     11336, 3434, 3529, 2908, 12071, 2361, 1843, 3030, 8174, 6147, 9842, 8326, 576, 10335, 10238, 10484, 9407, 11836, 5908, 418, 3772, 7515, 5429, 7552, 10996, 12133, 2767, 3969,
#     8298, 6413, 10008, 2031, 5333, 10800, 9789, 10706, 5942, 1263, 49, 5915, 10806, 11939, 10777, 1815, 5383, 3202, 4493, 6920, 10232, 1975, 8532, 2925, 347, 4754, 1858, 11863,
#     8974, 9551, 5868, 9634, 5735,11566, 12115, 10596, 3009, 6190, 11994, 6523, 652, 3762, 9370, 4016, 4077, 8561, 4049, 5990, 11130, 11143, 948, 325, 1404, 6992, 6119, 8333,
#     10929, 1200, 5184, 2555, 6122, 1594, 10327, 7183, 5961, 2692, 12121, 4298, 3329, 5919, 4433, 8455,7032, 1747, 3123, 3054, 6803, 5782, 10723, 9341, 2503, 683, 2459, 3656,
#     64, 4240, 3570, 835, 6065, 4046, 11580, 10970, 3150, 10331, 4322, 2078, 1112, 4079, 11231, 441, 922, 1050, 4536, 6844, 8429, 2683, 11099, 3818, 6171, 8500, 12142, 6833, 4449,
#     4749, 6752, 7500, 7822, 8214, 6974, 7965, 7373, 2169, 522, 5079, 3262, 10316, 6715, 1278, 9945, 3514, 11248, 11271, 5925, 468, 3988, 382, 11973, 5339, 6843, 6196, 8579, 2033,
#     8291, 1922, 3879, 11035, 973, 6854, 10930, 5206, 6760, 3199, 56, 3565, 654, 1702, 10302, 5862, 6153, 5415, 8646, 11889, 10561, 7341, 6152, 7232, 4698, 8844, 4780, 10240, 4912,
#     1321, 12097, 7048, 2920, 3127, 4169, 11502, 3482, 11279, 5468, 5874, 11612, 6055, 8953, 52, 3174, 10966, 9523, 151, 2127, 3957, 2839, 9784, 6383, 1579, 431, 7507, 5886, 3029,
#     6695, 4213, 504, 11684, 2302, 8689, 9026, 4624, 6212, 11868, 4080, 6221, 8687, 1003, 8757, 241, 58, 5009, 10333, 885, 6281, 3438, 9445, 11314, 8077, 6608, 3477, 142, 1105,
#     8841, 343, 4538, 1908, 1208, 4727, 7078, 10423, 10125, 6873, 11573, 10179, 416, 814, 1705, 2450, 8700, 717, 9307, 1373, 8186, 2429, 10568, 10753, 7228, 11071, 438, 8774, 5993,
#     3278, 4209, 6877, 3449, 1136, 3708, 3238, 2926, 1826, 4489, 3171, 8024, 8611, 1928, 464, 3205, 8930, 7080, 1092, 10900, 10221, 11943, 4404, 9126, 4032, 7449, 6127, 8067, 10763,
#     125, 540, 8921, 8062, 612, 8051, 12229, 9572, 9089, 10754, 10029, 68, 6453, 7723, 4781, 4924, 1014, 448, 3942, 5232, 1327, 8682, 3744, 7326, 3056, 9761, 5845, 5588, 412, 7187,
#     3975, 4883, 3087, 6454, 2257, 7784, 5676, 1417, 8400, 11710, 5596, 5987, 9175, 2769, 5966, 212, 6555, 11113, 5508, 11014, 1125, 4860, 10844, 1131, 4267, 6636, 2275, 9828, 5063,
#     4176, 3765, 1518, 8794, 4564, 10224, 5826, 3534, 3961, 4145, 10533, 506, 11034, 6505, 10897, 2674, 10077, 3338, 9013, 3511, 6811, 11111, 2776, 1165, 2575, 8881, 10347, 377,
#     4578, 11914, 10669, 10104, 392, 10453, 425, 9489, 193, 2231, 6197, 1038, 11366, 6204, 8122, 2894, 3654, 10975, 10545, 6599, 2455, 11951, 3947, 20, 5002, 5163, 4608, 8946, 8170,
#     10138, 1522, 8665, 10397, 3344, 5598, 10964, 6565, 11260, 1945, 11041, 9847, 7174, 4939, 2148, 6330, 3959, 5797, 4913, 3528, 8054, 3825, 8914, 9998, 4335, 8896, 9342, 3982,
#     6680, 11653, 7790, 6617, 1737, 622, 10485, 10886, 6195, 7100, 1687, 406, 12143, 5268, 9389, 12050, 994, 7735, 5464, 7383, 4670, 512, 364, 9929, 3028, 5216, 5518, 1226, 7550,
#     8038, 7043, 7814, 11053, 3017, 3121, 7584, 2600, 11232, 6780, 12085, 5219, 1409, 9600, 4605, 8151, 12109, 463, 8882, 8308, 10821, 9247, 10945, 9806, 2054, 6203, 6643, 3120,
#     6105, 8348, 8536, 6919, 8753, 11007, 8717, 9457, 2021, 9060, 4730, 3929, 10583, 3723, 845, 1936, 7, 5054, 3154, 3285, 4360, 3805, 11522, 2213, 4153, 12239, 12073, 5526, 769,
#     4099, 3944, 5604, 5530, 11024, 9282, 2171, 3480, 7434, 8520, 3232, 11996, 9656, 1406, 2945, 5349, 7207, 4590, 11607, 11309, 5202, 844, 7082, 4050, 8016, 9068, 9694, 8452, 7000,
#     5662, 567, 2941, 8619, 3808, 4987, 2373, 5135, 63, 7605, 3360, 11839, 10345, 578, 6921, 7628, 510, 5386, 2622, 7806, 5703, 10783, 9224, 11379, 5900, 4719, 11538, 3502, 5789,
#     10631, 5618, 826, 5043, 3090, 10891, 9951, 7596, 2293, 11872, 6151, 3469, 4443, 8871, 1555, 1802, 5103, 1891, 1223, 2334, 7878, 1590, 881, 365, 1927, 11274, 4510, 9652, 2946,
#     6828, 1280, 614, 10918, 12265, 7250, 6742, 9804, 11385, 2276, 11307, 2593, 879, 7899, 8071, 3454, 8531, 3795, 9021, 5776, 1849, 7766, 7988, 457, 8, 530, 9663, 7785, 11511, 3578,
#     7592, 10588, 3466, 8972, 9757, 3332, 139, 2046, 2940, 10808, 9332, 874, 2301, 5650, 12119, 150, 648, 8000, 9982, 9416, 2827, 2434, 11498, 6481, 12268, 9754, 11169, 11823, 11259,
#     3821, 10608, 2929, 6263, 4649, 6320, 9687, 10388, 502, 5118, 8496, 6226, 10716, 8443, 7624, 6883, 9269, 6616, 8620, 5287, 944, 7519, 6125, 1882, 11249, 10254, 5410, 1251, 1790,
#     5275, 8449, 10447, 4113, 72, 2828, 4352, 7455, 2712, 11048, 7911, 3451, 4094, 6508, 3045, 11194, 2643, 1783, 7211, 4974, 7724, 9811, 9449, 3019, 4194, 2730, 6878, 10421, 2253,
#     4518, 9195, 7469, 11129, 9173, 12100, 1763, 2209, 9617, 5170, 865, 1279, 1694, 10759, 8420, 4423, 10555, 3815, 5832, 10939]
# psi_bitrev_inv = [8193, 11796, 2381, 5444, 11854, 4337, 1912, 10911, 7012, 1168, 9041, 11082, 4645, 11885, 11224, 2143, 7313, 10682, 8509, 11414, 5088, 8005, 5011, 11287, 2566, 2187, 6039, 2422,
#     6267, 9302, 8643, 9852, 8456, 3778, 773, 11899, 442, 9888, 11222, 5101, 9430, 1045, 2481, 5012, 7428, 354, 6591, 9377, 1440, 8526, 27, 9223, 1017, 7404, 1632, 7205, 11744, 7270,
#     2678, 8585, 10752, 12047, 7575, 4143, 8758, 11813, 7384, 3985, 11869, 6730, 10745, 10111, 8889, 2399, 9153, 5191, 671, 3000, 243, 9273, 3247, 2686, 3978, 2969, 2370, 9424, 6957,
#     8779, 1630, 10163, 5407, 3186, 11136, 9405, 10040, 8241, 113, 4919, 8374, 2166, 3, 7852, 9140, 12129, 5291, 2704, 4938, 8653, 1663, 10512, 7635, 1426, 9018, 8232, 8925, 10600, 4372,
#     10115, 2847, 4414, 9644, 4053, 7247, 9984, 10805, 7394, 5195, 9509, 953, 3748, 11462, 6522, 9813, 12171, 10092, 5067, 3949, 8993, 4452, 2396, 7935, 130, 2837, 6915, 4278, 1673, 7300,
#     5331, 8705, 4177, 9764, 10908, 11950, 9821, 11745, 5791, 12280, 1022, 9447, 480, 3241, 11560, 10276, 3289, 10200, 5092, 9408, 9005, 10593, 1428, 2426, 334, 1260, 4388, 4632, 6534,
#     145, 6747, 3459, 8652, 7399, 6378, 8357, 2731, 2548, 4231, 355, 3382, 5179, 8595, 3707, 10530, 6429, 3195, 10643, 1212, 3542, 8785, 9744, 3621, 12288, 1479, 5146, 8246, 1305, 11567,
#     6553, 4134, 4978, 10938, 5777, 8961, 4591, 5728, 6461, 5023, 2639, 4821, 11340, 2625, 9314, 563, 9545, 3006, 3553, 4805, 2294, 11227, 8577, 9154, 4846, 9542, 11499, 955, 9970, 1170,
#     10963, 7203, 3201, 9275, 140, 1853, 4611, 726, 1635, 2768, 4255, 11112, 7969, 11289, 12208, 9198, 9238, 2366, 7393, 2963, 11184, 12147, 8812, 5681, 4212, 975, 2844, 8851, 6008, 11404,
#     1956, 7280, 12231, 12048, 3532, 11286, 3602, 6068, 8209, 421, 6077, 7665, 3263, 3600, 9987, 605, 11785, 8076, 5594, 9260, 6403, 4782, 11858, 10710, 5906, 2505, 9450, 8332, 10162,
#     12138, 2766, 1323, 9115, 12237, 3336, 6234, 677, 6415, 6821, 1010, 8807, 787, 8120, 9162, 9369, 5241, 192, 10968, 7377, 2049, 7509, 3445, 7591, 5057, 6137, 4948, 1728, 400, 3643,
#     6874, 6136, 6427, 1987, 10587, 11635, 8724, 12233, 9090, 5529, 7083, 1359, 5435, 11316, 1254, 8410, 10367, 3998, 10256, 3710, 6093, 5446, 6950, 316, 11907, 8301, 11821, 6364, 1018,
#     1041, 8775, 2344, 11011, 5574, 1973, 9027, 7210, 11767, 10120, 4916, 4324, 5315, 4075, 4467, 4789, 5537, 7540, 7840, 5456, 147, 3789, 6118, 8471, 1190, 9606, 3860, 5445, 7753, 11239,
#     11367, 11848, 1058, 8210, 11177, 10211, 7967, 1958, 9139, 1319, 709, 8243, 6224, 11454, 8719, 8049, 12225, 8633, 9830, 11606, 9786, 2948, 1566, 6507, 5486, 9235, 9166, 10542, 5257,
#     3834, 7856, 6370, 8960, 7991, 168, 9597, 6328, 5106, 1962, 10695, 6167, 9734, 7105, 11089, 1360, 3956, 6170, 5297, 10885, 11964, 11341, 1146, 1159, 6299, 8240, 3728, 8212, 8273, 2919,
#     8527, 11637, 5766, 295, 6099, 9280, 1693, 174, 723, 6554, 2655, 6421, 2738, 3315, 426, 10431, 7535, 11942, 9364, 3757, 10314, 2057, 5369, 7796, 9087, 6906, 10474, 1512, 350, 1483,
#     6374, 12240, 11026, 6347, 1583, 2500, 1489, 6956, 10258, 2281, 5876, 3991, 8320, 9522, 156, 1293, 4737, 6860, 4774, 8517, 11871, 6381, 453, 2882, 1805, 2051, 1954, 11713, 3963, 2447,
#     6142, 4115, 9259, 10446, 9928, 218, 9381, 8760, 8855, 1350, 6457, 8474, 1734, 7866, 3869, 1530, 10595, 11010, 11424, 7119, 2672, 10080, 10526, 189, 3116, 1160, 4820, 3094, 7771, 10036,
#     1868, 5411, 9559, 8095, 9270, 2840, 2478, 4565, 7315, 5078, 10506, 9646, 1095, 9244, 5781, 8195, 8838, 4378, 1241, 9577, 4834, 7937, 9461, 12217, 8176, 1842, 3840, 7014, 10499, 11038,
#     6879, 2035, 1040, 10407, 6164, 4770, 11345, 7002, 3669, 5673, 3020, 5406, 4665, 3846, 1573, 6063, 3793, 7171, 11787, 1901, 2602, 5969, 7640, 6026, 9360, 1681, 8468, 1030, 466, 1120,
#     2535, 21, 5808, 791, 9855, 9462, 2873, 2307, 4289, 11641, 12139, 170, 6639, 9988, 11415, 2957, 1481, 9349, 10243, 12150, 8957, 2532, 3317, 8823, 1701, 4697, 8711, 778, 4504, 2626,
#     11759, 12281, 11832, 4301, 4523, 10440, 6513, 3268, 8494, 3758, 8835, 4218, 4390, 11410, 9696, 982, 10013, 904, 2485, 5547, 5039, 24, 1371, 11675, 11009, 5461, 9343, 2637, 7779, 1015,
#     10362, 11924, 11408, 10699, 4411, 9955, 11066, 10398, 7186, 10487, 10734, 3418, 7846, 8820, 6138, 417, 9996, 4693, 2338, 1398, 9199, 7246, 11463, 6671, 1658, 6500, 8787, 751, 7570,
#     6389, 910, 3065, 1506, 6586, 4483, 9667, 6903, 11779, 4661, 5368, 11711, 1944, 450, 8929, 4684, 12226, 7154, 9916, 7302, 8481, 3670, 9348, 11722, 6627, 5289, 3837, 2595, 3221, 4273,
#     8239, 5207, 11445, 7087, 980, 682, 7699, 5082, 6940, 9344, 10883, 2633, 293, 9057, 3769, 4855, 8809, 10118, 3007, 1265, 6759, 6685, 8345, 8190, 11520, 6763, 216, 50, 8136, 10076, 767,
#     8484, 7929, 9004, 9135, 7235, 12282, 10353, 11444, 8566, 1706, 8360, 7559, 3229, 10268, 2832, 3572, 1282, 3536, 5370, 3753, 3941, 6184, 9169, 5646, 6086, 10235, 2483, 1344, 3042, 1468,
#     3981, 3407, 11826, 180, 4138, 7684, 2689, 10880, 7070, 204, 5509, 1057, 9689, 4705, 9168, 9272, 1236, 4475, 5246, 4251, 4739, 11063, 6771, 7073, 9261, 2360, 11925, 11777, 7619, 4906,
#     6825, 4554, 11295, 239, 2900, 7021, 146, 11883, 10602, 5189, 6094, 1403, 1804, 11667, 10552, 5672, 4499, 636, 5609, 8307, 2947, 3393, 7954, 2291, 3375, 8464, 4235, 8761, 7376, 6492,
#     8330, 5959, 10141, 7350, 5115, 2442, 1248, 10344, 1029, 5724, 1325, 6691, 8945, 1892, 3624, 10767, 2151, 4119, 3343, 7681, 7126, 7287, 12269, 8342, 338, 9834, 5690, 1744, 1314, 8635,
#     9395, 4167, 6085, 923, 11251, 6092, 10058, 12096, 2800, 11864, 1836, 11897, 2185, 1620, 375, 7711, 11912, 1942, 3408, 9714, 11124, 9513, 1178, 5478, 8778, 3276, 8951, 2212, 9615, 1392,
#     5784, 1255, 11783, 1756, 8144, 8328, 8755, 6463, 2065, 7725, 3495, 10771, 8524, 8113, 7226, 2461, 10014, 5653, 8022, 11158, 1445, 7429, 11164, 1275, 6781, 1176, 5734, 12077, 6323, 9520,
#     3114, 6302, 6693, 579, 3889, 10872, 6613, 4505, 10032, 5835, 9202, 7406, 8314, 5102, 11877, 6701, 6444, 2528, 9233, 4963, 8545, 3607, 10962, 7057, 8347, 11841, 11275, 7365, 7508, 4566,
#     5836, 12221, 2260, 1535, 3200, 2717, 60, 4238, 11677, 4227, 3368, 11749, 12164, 1526, 4222, 6162, 4840, 8257, 3163, 7885, 346, 2068, 1389, 11197, 5209, 3359, 9084, 11825, 10361, 3678,
#     4265, 9118, 7800, 10463, 9363, 9051, 8581, 11153, 8840, 5412, 8080, 9011, 6296, 3515, 11851, 1218, 5061, 1536, 1721, 9860, 4103, 10916, 2982, 11572, 3589, 9839, 10584, 11475, 11873,
#     2110, 716, 5416, 2164, 1866, 5211, 7562, 11081, 10381, 7751, 11946, 3448]

# Generates a randomly distributed polynomial in Rq
def GenA(publicseed):

    debug("Generating the polynomial a_hat")
    a_hat = [0]*NEWHOPE_N   # Declare polynomial of size NEWHOPE_N with 0 coefficients

    debug("Initializing extseed")
    extseed = bytearray(33)
    extseed[0:32] = publicseed[0:32]

    debug("Starting loop")
    for i in range(0, (NEWHOPE_N//64)):
        ctr = 0
        extseed[32] = i
        state = hashlib.shake_128(extseed)
        while ctr < 64:
            buf = state.digest(SQUEEZE_BLOCK_SIZE*1)
            j = 0
            while (j<168) and (ctr<64):     # The algorithm has this in a for-loop, but this while loop is equivalent
                buf0 = int(buf[j])
                buf1 = (int(buf[j+1]) << 8) % 4294967296      # 2^32 = 4294967296
                val = buf0|buf1
                if val<(5*NEWHOPE_Q):
                    a_hat[(64*i)+ctr] = val % NEWHOPE_Q
                    ctr += 1
                j += 2

    debug("Done generating a_hat")
    return a_hat

# Samples the R-LWE secret and error
def Sample(noiseseed, nonce):

    debug("Sampling a random polynomial in Rq")
    r = [0]*NEWHOPE_N   # Declare polynomial of size NEWHOPE_N

    debug("Initializing extseed and setting nonce ")
    extseed = bytearray(34)
    extseed[0:32] = noiseseed[0:32]
    extseed[32] = nonce

    debug("Starting loop")
    for i in range(0, (NEWHOPE_N//64)):     # Generate noise in lbocks of 64 coefficients
        extseed[33] = i
        buf = hashlib.shake_256(extseed).digest(128)
        for j in range(0, 64):
            a = buf[2*j]
            b = buf[(2*j)+1]
            r[(64*i)+j] = (bin(a).count("1") + NEWHOPE_Q - bin(b).count("1")) % NEWHOPE_Q

    debug("Done sampling random polynomial in Rq")
    return r

# Multiplies two polynomials coefficient-wise
def Poly_mul(a, b):
    c = [0]*NEWHOPE_N
    for i in range(0, NEWHOPE_N):
        c[i] = (a[i]*b[i]) % NEWHOPE_Q
    return c

# Adds two polynomials coefficient-wise
def Poly_add(a, b):
    c = [0]*NEWHOPE_N
    for i in range(0, NEWHOPE_N):
        c[i] = (a[i]+b[i]) % NEWHOPE_Q
    return c

# Subtracts two polynomials coefficient-wise
def PolySubtract(a, b):
    c = [0]*NEWHOPE_N
    for i in range(0, NEWHOPE_N):
        c[i] = (a[i]-b[i]) % NEWHOPE_Q
    return c

# # Implementation from Patrick Longa and Michael Naehrig
# # - Algorithm 1: NTT
# # Title: "Speeding up the Number Theoretic Transform for Faster Ideal Lattice-Based Cryptography"
# # URL: "https://eprint.iacr.org/2016/504.pdf"
# def NTT(a):
#
#     debug("Starting NTT")
#     t = NEWHOPE_N
#     m = 1
#
#     debug("Beginning while-loop in NTT")
#     while(m < NEWHOPE_N):
#         t = t//2
#         for i in range(0, m):
#             j1 = 2*i*t
#             j2 = j1 + t - 1
#             s = psi_bitrev[m+i]
#             for j in range(j1, j2+1):
#                 u = a[j]
#                 v = a[j+t]*s
#                 a[j] = (u+v) % NEWHOPE_Q
#                 a[j+t] = (u-v) % NEWHOPE_Q
#         m = 2*m
#     debug("End of while-loop in NTT")
#     return a
#
# # Implementation from Patrick Longa and Michael Naehrig
# # - Algorithm 2: INTT
# # Title: "Speeding up the Number Theoretic Transform for Faster Ideal Lattice-Based Cryptography"
# # URL: "https://eprint.iacr.org/2016/504.pdf"
# def INTT(a):
#     t = 1
#     m = NEWHOPE_N
#     while (m > 1):
#         j1 = 0
#         h = m//2
#         for i in range(0, h):
#             j2 = j1 + t - 1
#             s = psi_bitrev_inv[h+1]
#             for j in range(j1, j2+1):
#                 u = a[j]
#                 v = a[j+1]
#                 a[j] = (u+v) % NEWHOPE_Q
#                 a[j+t] = (u-v)*s % NEWHOPE_Q
#             j1 = j1 + (2*t)
#         t = 2*t
#         m = m//2
#     for j in range(0, NEWHOPE_N):
#         a[j] = (a[j]*NEWHOPE_N_INV) % NEWHOPE_Q
#     return a

# Returns the forward number-theoretic transform of the given vector with
# respect to the given primitive nth root of unity under the given modulus.
def NTT(invec, root, mod):
	outvec = []
	for i in range(len(invec)):
		temp = 0
		for (j, val) in enumerate(invec):
			temp += val * pow(root, i * j, mod)
			temp %= mod
		outvec.append(temp)
	return outvec


# Returns the inverse number-theoretic transform of the given vector with
# respect to the given primitive nth root of unity under the given modulus.
def INTT(invec, root, mod):
	outvec = NTT(invec, reciprocal(root, mod), mod)
	scaler = reciprocal(len(invec), mod)
	return [(val * scaler % mod) for val in outvec]

# Returns the multiplicative inverse of n modulo mod. The inverse x has the property that
# 0 <= x < mod and (x * n) % mod = 1. The inverse exists if and only if gcd(n, mod) = 1.
def reciprocal(n, mod):
	if not (0 <= n < mod):
		raise ValueError()
	x, y = mod, n
	a, b = 0, 1
	while y != 0:
		a, b = b, a - x // y * b
		x, y = y, x % y
	if x == 1:
		return a % mod
	else:
		raise ValueError("Reciprocal does not exist")

# Encodes the ciphertext and error
def EncodeC(u, h):
    c = [0]*(NEWHOPE_7N_4 + NEWHOPE_3N_8)
    c[0:NEWHOPE_7N_4] = EncodePoly(u)
    c[NEWHOPE_7N_4:] = h
    return c

# Encodes a polynomial in Rq as an array of bytes
def EncodePoly(s):
    r = [0]*NEWHOPE_7N_4
    for i in range(0, 256):
        t0 = s[(4*i)+0] % NEWHOPE_Q
        t1 = s[(4*i)+1] % NEWHOPE_Q
        t2 = s[(4*i)+2] % NEWHOPE_Q
        t3 = s[(4*i)+3] % NEWHOPE_Q
        r[(7*i)+0] = t0 & int(0xff)
        r[(7*i)+1] = (t0 >> 8) | ((t1 << 6)%4294967296) & int(0xff)
        r[(7*i)+2] = (t1 >> 2) & int(0xff)
        r[(7*i)+3] = (t1 >> 10) | ((t2 << 4)%4294967296) & int(0xff)
        r[(7*i)+4] = (t2 >> 4) & int(0xff)
        r[(7*i)+5] = (t2 >> 12) | ((t3 << 2)%4294967296) & int(0xff)
        r[(7*i)+6] = (t3 >> 6) & int(0xff)
    return r

# Encodes the public key
def EncodePK(b_hat, publicseed):
    r = [0]*(NEWHOPE_7N_4 + 32)
    r[0:NEWHOPE_7N_4] = EncodePoly(b_hat)
    r[NEWHOPE_7N_4:] = publicseed
    return r

# Encodes the 32-byte message to a polynomial in Rq
def EncodeMsg(m):
    v = [0]*NEWHOPE_N
    for i in range(0, 32):
        for j in range(0, 8):
            mask = -(((m[i]>>j))&1)
            v[(8*i)+j+0] = (mask&(NEWHOPE_Q//2)) #% NEWHOPE_Q
            v[(8*i)+j+256] = (mask&(NEWHOPE_Q//2)) #% NEWHOPE_Q
            v[(8*i)+j+512] = (mask&(NEWHOPE_Q//2)) #% NEWHOPE_Q
            v[(8*i)+j+768] = (mask&(NEWHOPE_Q//2)) #% NEWHOPE_Q
    return v

# Decodes the ciphertext and error
def DecodeC(c):
    u = DecodePoly(c[0:NEWHOPE_7N_4])
    h = c[NEWHOPE_7N_4:]
    return u, h

# Decodes an array of bytes to a polynomial in Rq
def DecodePoly(v):
    debug('Starting decoding polynomial')
    r = [0]*NEWHOPE_N
    for i in range(0, 256):
        r[(4*i)+0] = int(v[(7*i)+0]) | (((int(v[(7*i)+1])&int(0x3f))<<8)%4294967296)
        r[(4*i)+1] = (int(v[(7*i)+1]) >> 6) | ((int(v[(7*i)+2]) << 2)%4294967296) | (((int(v[(7*i)+3])&int(0x0f))<<10)%4294967296)
        r[(4*i)+2] = (int(v[(7*i)+3]) >> 4) | ((int(v[(7*i)+4]) << 4)%4294967296) | (((int(v[(7*i)+5])&int(0x03))<<12)%4294967296)
        r[(4*i)+3] = (int(v[(7*i)+5]) >> 2) | ((int(v[(7*i)+6]) << 6)%4294967296)
    debug('Done decoding polynomial')
    return r

# Encodes the 32-byte message to a polynomial in Rq
def DecodeMsg(v):
    m = [0]*32
    for i in range(0, 256):
        t = abs(((v[i+0])%NEWHOPE_Q) - ((NEWHOPE_Q)//2))
        t = t + abs((((v[i+256])%NEWHOPE_Q) - ((NEWHOPE_Q)//2)))
        t = t + abs((((v[i+512])%NEWHOPE_Q) - ((NEWHOPE_Q)//2)))
        t = t + abs((((v[i+768])%NEWHOPE_Q) - ((NEWHOPE_Q)//2)))
        t = t - NEWHOPE_Q
        t = t >> 15
        m[i>>3] = m[i>>3] | -(t<<(i&7))
    return m

# Decodes the public key
def DecodePK(pk):
    debug('Starting decoding public key')
    b_hat = DecodePoly(pk[0:NEWHOPE_7N_4])
    seed = pk[NEWHOPE_7N_4:]
    debug('Done decoding public key')
    return b_hat, seed

# Compresses a message to send
def Compress(v):
    k = 0
    t = [0]*8
    h = [0]*NEWHOPE_3N_8
    for l in range(0, 128):
        i = 8*l
        for j in range(0, 8):
            t[j] = v[i+j] % NEWHOPE_Q
            t[j] = (((int(t[j]<<3))+NEWHOPE_Q//2)//NEWHOPE_Q) & int(0x7)
        h[k+0] = (t[0] | ((t[1]<<3)) | ((t[2]<<6))) #%256
        h[k+1] = ((t[2]>>2) | ((t[3]<<1)) | ((t[4]<<4)) | ((t[5]<<7))) #%256
        h[k+2] = ((t[5]>>1) | ((t[6]<<2)) | ((t[7]<<5))) #%256
        # print("============================compress================================")
        # print(h)
        # print("============================compress================================")
        k += 3
    return h

# Decompresses the message to recover the data
def Decompress(h):
    r = [0]*NEWHOPE_N
    k = 0
    # print("============================input================================")
    # print(h)
    # print("============================input================================")
    for l in range(0, 128):
        i = 8*l
        r[i+0] = h[k+0] & 7
        r[i+1] = (h[k+0]>>3) & 7
        r[i+2] = (h[k+0]>>6) | (((h[1]<<2))&4)
        r[i+3] = (h[k+1]>>1) & 7
        r[i+4] = (h[k+1]>>4) & 7
        r[i+5] = (h[k+1]>>7) | (((h[2]<<1))&6)
        r[i+6] = (h[k+2]>>2) & 7
        r[i+7] = (h[k+2]>>5)
        k += 3
        # print("============================decompress================================")
        # print(r)
        # print("============================decompress================================")
        for j in range(0, 8):
            r[i+j] = (((r[i+j])*NEWHOPE_Q)+4)>>3
    return r

# Generates the public and private key
def PKEGen():

    debug("Generating the 32-byte random seed")
    seed = os.urandom(32)

    debug("Creating publicseed and noiseseed")
    z = hashlib.shake_256(seed).digest(64)
    publicseed = z[0:32]
    noiseseed = z[32:]

    debug("Generating polynomial a_hat")
    a_hat = GenA(publicseed)

    debug("Sampling polynomial s")
    s = Sample(noiseseed, 0)

    debug("Computing s_hat = NTT of s")
    s_hat = NTT(s, NEWHOPE_ROOT, NEWHOPE_Q)

    debug("Sampling polynomial e")
    e = Sample(noiseseed, 1)

    debug("Computing e_hat = NTT of e")
    e_hat = NTT(e, NEWHOPE_ROOT, NEWHOPE_Q)

    debug("Computing ahat_shat")
    ahat_shat = Poly_mul(a_hat, s_hat)

    debug("Computing b_hat = a_hat dot s_hat + e_hat")
    b_hat = Poly_add(ahat_shat, e_hat)

    debug("Computing public key pk")
    pk = EncodePK(b_hat, publicseed)

    debug("Computing secret key sk")
    sk = EncodePoly(s_hat)

    debug("Public key generation complete. Returning keys")

    return pk, sk

# Encrypts a message and returns a ciphertext
def Encrypt(pk, m, coin):
    print("========================== Encrypting Message ==========================")
    b_hat, publicseed = DecodePK(pk)
    a_hat = GenA(publicseed)

    s_prime = Sample(coin, 0)
    e_prime = Sample(coin, 1)
    e_prime_prime = Sample(coin, 2)

    t_hat = NTT(s_prime, NEWHOPE_ROOT, NEWHOPE_Q)
    e_prime_ntt = NTT(e_prime, NEWHOPE_ROOT, NEWHOPE_Q)

    ahat_that = Poly_mul(a_hat, t_hat)
    u_hat = Poly_add(ahat_that, e_prime_ntt)

    v = EncodeMsg(m)

    bhat_that = Poly_mul(b_hat, t_hat)
    ntt_temp = INTT(bhat_that, NEWHOPE_ROOT, NEWHOPE_Q)

    sum1 = Poly_add(ntt_temp, e_prime_prime)
    v_prime = Poly_add(sum1, v)
    h = Compress(v_prime)
    c = EncodeC(u_hat, h)
    return c

# Decrypts a ciphertext
def Decrypt(c, sk):
    print("========================== Decrypting Message ==========================")
    u_hat, h = DecodeC(c)
    s_hat = DecodePoly(sk)
    v_prime = Decompress(h)

    us_product = Poly_mul(u_hat, s_hat)
    inv_product = INTT(us_product, NEWHOPE_ROOT, NEWHOPE_Q)
    v_sub = PolySubtract(v_prime, inv_product)
    m = DecodeMsg(v_sub)
    return m

# Driver for key creation, encryption and decryption
def main():
    print("=============================================================================")
    print("========================== Starting PKE generation ==========================")
    print("=============================================================================")

    # # SCRIPT TO RUN 1000 TIMES WITH RANDOM SEED AND COIN.
    # # Output in file 1000test.txt
    # start = dt.datetime.now()
    # total = 0
    # passed = 0
    # failed = 0
    # with open('1000test.txt', 'w') as f:
    #     for i in range(0, 1000):
    #         pk, sk = PKEGen()
    #         coin = os.urandom(32)
    #         m = [225, 235, 49, 214, 170, 104, 167, 11, 44, 191, 245, 93, 225, 169, 110, 109, 210, 245, 50, 76, 61, 222, 120, 169, 152, 103, 251, 147, 188, 248, 161, 144]
    #         c = Encrypt(pk, m, coin)
    #         m_prime = Decrypt(c, sk)
    #
    #         f.write('Round: {}\n'.format(i))
    #         f.write('Public key: {}\n'.format(pk))
    #         f.write('Secret key: {}\n'.format(sk))
    #         f.write('Coin: {}\n'.format(coin))
    #         if (m == m_prime):
    #             f.write('Status: PASSED\n')
    #             passed += 1
    #         else:
    #             f.write('Status: FAILED\n')
    #             failed += 1
    #         total +=1
    #         f.write('Total: {}  Passed: {}  Failed: {}'.format(total, passed, failed))
    #
    #         print("{} seconds: finished {} cycles".format((dt.datetime.now() - start).seconds,i))

    pk, sk = PKEGen()
    coin = os.urandom(32)
    m = [225, 235, 49, 214, 170, 104, 167, 11, 44, 191, 245, 93, 225, 169, 110, 109, 210, 245, 50, 76, 61, 222, 120, 169, 152, 103, 251, 147, 188, 248, 161, 144]
    c = Encrypt(pk, m, coin)
    m_prime = Decrypt(c, sk)
    print("========================== Here is the original message and recovered message ==========================")
    print(m)
    print(m_prime)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if str(sys.argv[1]).lower() == "debug":
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
