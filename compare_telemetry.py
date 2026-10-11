#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_telemetry.py — 遥五实测弹道点 vs 模型对拍
实测来源: B 站直播录屏（天链二号 01 星跟踪画面, "二级一次飞行段"）,
用户 2026-10-10 提供。
经度读数修正: 画面裁掉了前两位（"12"）。520 s 才飞 8.7 min, 平均地速 ~3 km/s
只能走 ~14°, "165.60°E" 物理不可能; 125.60/127.29°E 与模型 126.8/128.6 无缝衔接。
速度口径: 实测与模型地速吻合（~1%）, 惯速差 6% → 直播显示为地速。
"""
import numpy as np
import pandas as pd

TELEMETRY = [
    dict(t=520.0, lat=16.03, lon=125.60, alt=185.249, v=6.336),
    dict(t=554.0, lat=15.55, lon=127.29, alt=189.708, v=6.457),
]

def interp(df, t, cols):
    return {c: np.interp(t, df["time"], df[c]) for c in cols}

def show(name):
    df = pd.read_csv(name)
    out = []
    for pt in TELEMETRY:
        r = interp(df, pt["t"],
                   ["lat", "lon", "altitude", "vel_inertial", "vel_ground"])
        out.append(dict(t=pt["t"], lat=r["lat"], lon=r["lon"],
                        alt=r["altitude"]/1000.0,
                        v_i=r["vel_inertial"]/1000.0,
                        v_g=r["vel_ground"]/1000.0))
    return out

models = {"v1": show("output/cz5-tli-calib-trajectoryResult.csv"),
          "park160": show("output/cz5-park160-trajectoryResult.csv")}

print(f"{'时刻':>6} {'量':>12} {'实测':>10} {'v1':>10} {'park160':>10}")
for k, pt in enumerate(TELEMETRY):
    print("-"*58)
    print(f"{pt['t']:6.0f} {'纬度 °':>12} {pt['lat']:10.2f} "
          f"{models['v1'][k]['lat']:10.2f} {models['park160'][k]['lat']:10.2f}")
    print(f"{'':>6} {'经度 °':>12} {pt['lon']:10.2f} "
          f"{models['v1'][k]['lon']:10.2f} {models['park160'][k]['lon']:10.2f}")
    print(f"{'':>6} {'高度 km':>12} {pt['alt']:10.3f} "
          f"{models['v1'][k]['alt']:10.3f} {models['park160'][k]['alt']:10.3f}")
    print(f"{'':>6} {'v_inertial':>12} {'—':>10} "
          f"{models['v1'][k]['v_i']:10.3f} {models['park160'][k]['v_i']:10.3f}")
    print(f"{'':>6} {'v_ground':>12} {pt['v']:10.3f} "
          f"{models['v1'][k]['v_g']:10.3f} {models['park160'][k]['v_g']:10.3f}")
