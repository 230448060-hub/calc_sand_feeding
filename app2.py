import streamlit as st
import math

def calc_iwagaki_tau_c(d50_m: float, s: float) -> float:
    """岩垣の公式（水温20℃相当）による限界無次元掃流力 tau_c* の算定"""
    d_cm = d50_m * 100.0
    if d_cm >= 0.303:
        u_star_c2 = 80.9 * d_cm
    elif d_cm >= 0.118:
        u_star_c2 = 134.6 * (d_cm ** (31.0 / 22.0))
    elif d_cm >= 0.0565:
        u_star_c2 = 55.0 * d_cm
    elif d_cm >= 0.0065:
        u_star_c2 = 8.41 * (d_cm ** (11.0 / 32.0))
    else:
        u_star_c2 = 226.0 * d_cm
    return u_star_c2 / ((s - 1.0) * 981.0 * d_cm)

st.title("水路実験 給砂量計算アプリ（芦田・道上式ver）")

Q_Lmin = st.number_input("流量 [L/min]", min_value=0.0, value=300.0)
B_cm   = st.number_input("水路幅 [cm]", min_value=0.1, value=30.0)
I      = st.number_input("水路勾配 [-]", min_value=0.0001, value=0.01, format="%.4f")
d50_mm = st.number_input("平均粒径 [mm]", min_value=0.01, value=1.0)

with st.expander("詳細パラメータ・計算オプション設定"):
    eff_mode = st.radio(
        "有効掃流力 τe* の算定方法",
        ["標準（河床波の形状抵抗を考慮：u*e を算定）", "簡易（平坦河床近似：τe* = τ*）"]
    )
    tau_c_mode = st.radio(
        "限界無次元掃流力 τc* の設定",
        ["固定値を使用（デフォルト 0.05）", "岩垣の公式で粒径から自動計算"]
    )
    tau_c_input = st.number_input(
        "限界無次元掃流力 τc*（固定値選択時）",
        min_value=0.001, value=0.05, format="%.3f"
    )
    rho_d = st.number_input("乾燥かさ密度 ρd [g/cm³]", min_value=0.1, value=1.55)
    s     = st.number_input("砂の水中比重 s [-]", min_value=1.01, value=2.65)

if st.button("計算実行"):
    g = 9.81
    Q = Q_Lmin / 60000.0
    B = B_cm / 100.0
    d50 = d50_mm / 1000.0

    n = (d50 ** (1.0 / 6.0)) / 20.0
    h = ((n * (Q / B)) / math.sqrt(I)) ** 0.6
    U = Q / (B * h) if h > 0 else 0.0

    u_star = math.sqrt(g * h * I)
    tau_star = (h * I) / ((s - 1.0) * d50)

    if eff_mode.startswith("標準"):
        ratio = max(1.0, h / (d50 * (1.0 + 2.0 * tau_star)))
        denom = 6.0 + 5.75 * math.log10(ratio)
        u_star_e = min(u_star, U / denom)
        tau_star_e = (u_star_e ** 2) / ((s - 1.0) * g * d50)
    else:
        tau_star_e = tau_star

    if tau_c_mode.startswith("岩垣"):
        tau_c = calc_iwagaki_tau_c(d50, s)
    else:
        tau_c = tau_c_input

    if tau_star > tau_c:
        ratio_c = tau_c / tau_star
        phi = 17.0 * (tau_star_e ** 1.5) * (1.0 - ratio_c) * (1.0 - math.sqrt(ratio_c))
    else:
        phi = 0.0

    qb = phi * math.sqrt((s - 1.0) * g * (d50 ** 3))
    ws = qb * B * 1e6 * rho_d 

    col1, col2 = st.columns(2)
    col1.metric("目標給砂量", f"{ws:.2f} g/s")
    col2.metric("計算水深", f"{h * 100:.2f} cm")

    st.caption(
        f"水理諸元確認: 無次元掃流力 τ* = {tau_star:.4f} / "
        f"有効掃流力 τe* = {tau_star_e:.4f} / "
        f"限界掃流力 τc* = {tau_c:.4f} / 平均流速 U = {U:.3f} m/s"
    )
