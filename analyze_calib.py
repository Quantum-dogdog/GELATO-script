#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_calib.py — CZ-5 遥五 TLI 标定对比表
读 GELATO trajectoryResult.csv，提取事件时刻/燃烧时长/终端根数，
与嫦娥五号（长征五号遥五）公开实测值对比，输出 markdown 表。

用法: python3 analyze_calib.py [trajectoryResult.csv]
参考值来源: 公开报道（事件时刻秒级为约数；滑行/二次点火为区间值）
"""
import sys
import numpy as np
import pandas as pd

CSV = sys.argv[1] if len(sys.argv) > 1 else "output/cz5-tli-calib-trajectoryResult.csv"

# —— 遥五公开实测参考值（人工选择值，非物理常数；秒级约数）——
Y5 = dict(
    kickturn=17.0,      # 程序转弯开始
    booster_sep=173.0,  # 助推分离
    fairing=280.0,      # 抛整流罩
    meco=480.0,         # 芯一级关机 / 一二级分离
    seco1=830.0,        # 二级一次关机（燃烧 ~350 s）
    burn1=350.0,
    coast=935.0,        # 停泊轨道滑行（"最长约 935 s"，取标称）
    seig2=1765.0,       # 二次点火（= 830 + 935，报道区间 1765-1767）
    seco2=2180.0,       # 二次关机（燃烧 ~415 s，报道区间 2180-2190）
    burn2=415.0,
    sep2=2185.0,        # 器箭分离（报道区间 2182-2190，取中值）
    payload=8200.0,     # 嫦娥五号轨道器+返回器组合体 ~8.2 t
)

df = pd.read_csv(CSV)
ev = df[df["event"].notna()].set_index("event")
t = ev["time"]

burn1 = t["COAST"] - t["SEIG"]
burn2 = t["SECO2"] - t["BURN2"]
coast = t["BURN2"] - t["COAST"]
last = df.iloc[-1]

rows = [
    ("程序转弯开始 KICKTURN", t["KICKTURN"], Y5["kickturn"]),
    ("助推分离 BOOSTER_SEP", t["BOOSTER_SEP"], Y5["booster_sep"]),
    ("抛整流罩 FAIRING", t["FAIRING"], Y5["fairing"]),
    ("芯一级关机 MECO", t["MECO"], Y5["meco"]),
    ("一次关机 SECO1", t["COAST"], Y5["seco1"]),
    ("一次燃烧时长", burn1, Y5["burn1"]),
    ("停泊滑行时长(fixed)", coast, Y5["coast"]),
    ("二次点火 BURN2", t["BURN2"], Y5["seig2"]),
    ("二次关机 SECO2", t["SECO2"], Y5["seco2"]),
    ("二次燃烧时长", burn2, Y5["burn2"]),
    ("器箭分离 SEP2", t["SEP2"], Y5["sep2"]),
]

print("## CZ-5 遥五标定对比表\n")
print("| 事件 | 模型 (s) | 遥五公开值 (s) | 偏差 (s) |")
print("|---|---|---|---|")
for name, model, ref in rows:
    print(f"| {name} | {model:9.2f} | {ref:9.1f} | {model - ref:+8.2f} |")

print(f"\n| 载荷质量 | {last['mass']:8.1f} kg | {Y5['payload']:.0f} kg "
      f"| {last['mass'] - Y5['payload']:+.1f} kg ({(last['mass']/Y5['payload']-1)*100:+.1f}%) |")

print("\n## 终端瞬时根数（SIMEND 末端, output_result 自带列）")
for k in ("altitude", "altitude_perigee", "altitude_apogee", "inclination",
          "argument_perigee", "lon_ascending_node", "true_anomaly"):
    if k in last.index:
        print(f"  {k:26s} = {last[k]:12.1f}")

print("\n## TLI 点（SECO2 时刻）地理位置与落点特征")
for k in ("lat", "lon", "lat_IIP", "lon_IIP"):
    if k in last.index:
        print(f"  {k:8s} = {last[k]:10.2f}")

# 一致性自检：燃烧时长合计 vs 预算等式（流量 = F/Isp_m/s, Isp·g0 = 4340 m/s）
total_burn = burn1 + burn2
budget_s = 29100.0 / (176720.0 / (442.62 * 9.80665))
print(f"\n自检: burn1+burn2 = {total_burn:.2f} s, 预算等式 {budget_s:.2f} s, "
      f"差 {total_burn - budget_s:+.3f} s")
