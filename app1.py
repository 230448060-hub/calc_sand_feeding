import streamlit as st
import math

st.title("水路実験 給砂量計算アプリ")

# 画面からの入力フォーム
Q_Lmin = st.number_input("流量 [L/min]", min_value=0.0, value=300.0)
B_cm   = st.number_input("水路幅 [cm]", min_value=0.1, value=30.0)
I      = st.number_input("水路勾配 [-]", min_value=0.0001, value=0.01, format="%.4f")
d50_mm = st.number_input("平均粒径 [mm]", min_value=0.01, value=1.0)

if st.button("計算実行"):
    # 単位換算 (SI単位へ)
    Q = Q_Lmin / 60000.0
    B = B_cm / 100.0
    d50 = d50_mm / 1000.0

    # 水理計算 (等流)
    n = (d50 ** (1/6)) / 20.0
    h = ((n * (Q / B)) / math.sqrt(I)) ** 0.6

    # MPM式による流砂量算定
    tau_star = (h * I) / (1.65 * d50)
    phi = 8.0 * max(0.0, tau_star - 0.05) ** 1.5
    qb = phi * math.sqrt(1.65 * 9.81 * (d50 ** 3))

    # 給砂量 [g/min] 換算
    ws = qb * B * 1e6 * 1.55 * 60.0

    # 結果表示
    st.metric("目標給砂量", f"{ws:.1f} g/min")
    st.metric("計算水深", f"{h * 100:.2f} cm")
