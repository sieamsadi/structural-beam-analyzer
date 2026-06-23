import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from indeterminatebeam import Beam, Support, PointLoadV, UDLV

# --- PAGE SETUP ---
st.set_page_config(page_title="Structural Beam Analyzer Pro", page_icon="🏗️", layout="wide")

# Custom CSS styling for a clean, industrial dashboard look
st.markdown("""
    <style>
    .reportview-container { background: #F8FAFC }
    .main-title { font-size:2.4rem !important; font-weight: 800; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-title { font-size:1.1rem !important; color: #64748B; margin-bottom: 2rem; }
    .card { background-color: #FFFFFF; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-left: 5px solid #3B82F6; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏗️ Enterprise Structural Beam Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Production-grade 1D Finite Element Analysis solver for commercial engineering design compliance.</div>', unsafe_allow_html=True)

# --- LOAD DATASET (With built-in safety fallback) ---
@st.cache_data
def load_steel_data():
    try:
        df = pd.read_csv("data/aisc_w_shapes.csv")
        return df
    except:
        # Fallback dataset if the CSV folder hasn't synced to the cloud yet
        data = {
            'Designation': ['W12X26', 'W14X30', 'W16X31', 'W18X50', 'W24X68'],
            'Ix': [204.0, 291.0, 375.0, 800.0, 1830.0],
            'Zx': [37.2, 47.3, 54.0, 101.0, 177.0]
        }
        return pd.DataFrame(data)

steel_df = load_steel_data()

# --- SIDEBAR INTERFACE ---
st.sidebar.header("📐 1. System Parameters")
length = st.sidebar.slider("Total Beam Span Length (m)", 2.0, 15.0, 6.0, 0.25)

material = st.sidebar.selectbox("Material Specification", ["Structural Steel (A36)", "Aluminum (6061-T6)"])
E = 200e9 if "Steel" in material else 69e9
sigma_yield = 250e6 if "Steel" in material else 276e6  # Pa

st.sidebar.markdown("---")
st.sidebar.header("⛓️ 2. Cross-Section Profile")
profile_source = st.sidebar.radio("Profile Type", ["AISC Standard W-Shapes (I-Beam)", "Custom Analytical Properties"])

if profile_source == "AISC Standard W-Shapes (I-Beam)":
    selected_shape = st.sidebar.selectbox("Select AISC Designation", steel_df['Designation'].tolist())
    row = steel_df[steel_df['Designation'] == selected_shape].iloc[0]
    
    # Convert Imperial database units (in⁴ and in³) to Metric SI Units (m⁴ and m³)
    I = float(row['Ix']) * 4.162314e-7
    Z = float(row['Zx']) * 1.638706e-5
    st.sidebar.caption(f"Configured Properties: I = {I:.3e} m⁴ | Z = {Z:.3e} m³")
else:
    I = st.sidebar.number_input("Moment of Inertia I (cm⁴)", value=5000.0) * 1e-8
    Z = st.sidebar.number_input("Section Modulus Z (cm³)", value=500.0) * 1e-6

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. Support Conditions")
boundary_type = st.sidebar.selectbox("Boundary Arrangement", ["Simply Supported", "Cantilever", "Fixed-Fixed"])

supports = []
if boundary_type == "Simply Supported":
    # (x, y, moment) -> Left is Pin (1,1,0), Right is Roller (0,1,0)
    supports = [Support(0, (1, 1, 0)), Support(length, (0, 1, 0))]
elif boundary_type == "Cantilever":
    # Fixed at the left wall (1,1,1)
    supports = [Support(0, (1, 1, 1))]
else:
    # Clamped at both walls
    supports = [Support(0, (1, 1, 1)), Support(length, (1, 1, 1))]

# --- CORE ENGINEERING LOGIC & LOADS ---
st.header("💥 Applied External Structural Loading")
col_l1, col_l2 = st.columns(2)

loads = []
with col_l1:
    st.subheader("Point Loads")
    num_pt_loads = st.number_input("Number of discrete point loads", min_value=0, max_value=3, value=1)
    for i in range(num_pt_loads):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            p_mag = st.number_input(f"Load {i+1} Magnitude (kN)", value=20.0, key=f"pmag_{i}") * 1000
        with p_col2:
            p_loc = st.slider(f"Load {i+1} Position (m)", 0.0, length, length/2, key=f"ploc_{i}")
        if p_mag > 0:
            loads.append(PointLoadV(-p_mag, p_loc))

with col_l2:
    st.subheader("Uniformly Distributed Loads (UDL)")
    num_udl_loads = st.number_input("Number of distributed loads", min_value=0, max_value=2, value=0)
    for i in range(num_udl_loads):
        u_col1, u_col2, u_col3 = st.columns(3)
        with u_col1:
            u_mag = st.number_input(f"UDL {i+1} Force (kN/m)", value=5.0, key=f"umag_{i}") * 1000
        with u_col2:
            u_start = st.slider(f"UDL {i+1} Start (m)", 0.0, length, 0.0, key=f"ustart_{i}")
        with u_col3:
            u_end = st.slider(f"UDL {i+1} End (m)", 0.0, length, length, key=f"uend_{i}")
        if u_mag > 0 and u_start < u_end:
            loads.append(UDLV(-u_mag, (u_start, u_end)))

# --- SOLVER EXECUTION ---
if not loads:
    st.warning("⚠️ Application running idle. Please add a load magnitude greater than 0 to compile calculation matrices.")
else:
    try:
        # Initialize Engine Solver
        beam = Beam(length)
        beam.add_supports(*supports)
        beam.add_loads(*loads)
        beam.analyse()
        
        # Grid sample resolution setup
        x_space = np.linspace(0, length, 400)
        shear_forces = [beam.get_shear_force(x) / 1000 for x in x_space]
        bending_moments = [beam.get_bending_moment(x) / 1000 for x in x_space]
        
        # Scale analytical deflection relative to user's custom E and I
        deflections = np.array([beam.get_deflection(x) * 1000 for x in x_space]) * ((200e9 * 1e-4) / (E * I))
        worst_deflection = deflections[np.argmax(np.abs(deflections))]
        
        # Stress verification: σ = M / Z
        max_moment_nm = np.max(np.abs(bending_moments)) * 1000
        max_stress_pa = max_moment_nm / Z
        max_stress_mpa = max_stress_pa / 1e6
        safety_factor = (sigma_yield / 1e6) / max_stress_mpa if max_stress_mpa > 0 else float('inf')
        
        # --- UI METRICS PANEL ---
        st.write("---")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="card"><small>MAX BENDING MOMENT</small><br><b style="font-size:1.5rem; color:#EF4444;">{np.max(np.abs(bending_moments)):.2f} kN·m</b></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="card"><small>WORST DEFLECTION</small><br><b style="font-size:1.5rem; color:#3B82F6;">{worst_deflection:.2f} mm</b></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="card"><small>MAX NORMAL STRESS</small><br><b style="font-size:1.5rem; color:#10B981;">{max_stress_mpa:.1f} MPa</b></div>', unsafe_allow_html=True)
        with m4:
            card_color = "#10B981" if safety_factor >= 1.5 else "#F59E0B" if safety_factor >= 1.0 else "#EF4444"
            st.markdown(f'<div class="card" style="border-left-color:{card_color};"><small>FACTOR OF SAFETY</small><br><b style="font-size:1.5rem; color:{card_color};">{safety_factor:.2f}</b></div>', unsafe_allow_html=True)

        # --- CHARTS VIEW GENERATION ---
        st.write(" ")
        graph_tab, data_tab = st.tabs(["📊 Interactive FEA Diagrams", "📋 Structural Text Reports"])
        
        with graph_tab:
            # Chart 1: Moment
            f_m = go.Figure()
            f_m.add_trace(go.Scatter(x=x_space, y=bending_moments, fill='tozeroy', line_color='#EF4444', name="Moment (kN·m)"))
            f_m.update_layout(title="Bending Moment Diagram (BMD)", xaxis_title="Position along span (m)", yaxis_title="Moment (kN·m)", template="plotly_white", height=320)
            st.plotly_chart(f_m, use_container_width=True)
            
            # Chart 2: Deflection
            f_d = go.Figure()
            f_d.add_trace(go.Scatter(x=x_space, y=deflections, line=dict(color='#3B82F6', width=3), name="Deflection (mm)"))
            f_d.update_layout(
                title="Elastic Deflection Curve (Sag Profile)", 
                xaxis_title="Position along span (m)", 
                yaxis_title="Deflection (mm)", 
                template="plotly_white", 
                height=320,
                yaxis_autorange="reversed"
            )
            st.plotly_chart(f_d, use_container_width=True)
            
        with data_tab:
            st.subheader("Calculation Memo Checksum Log")
            st.text(f"Material: {material} | Elastic Modulus: {E/1e9:.1f} GPa | Yield Strength: {sigma_yield/1e6:.1f} MPa")
            st.text(f"Evaluated Second Moment of Area (Izz): {I:.5e} m⁴")
            st.text(f"Evaluated Elastic Section Modulus (Z): {Z:.5e} m³")
            
            memo_txt = f"STRUCTURAL CALCULATION MEMO\nSpan: {length}m | Material: {material}\nMax Normal Stress: {max_stress_mpa:.2f} MPa\nFactor of Safety: {safety_factor:.2f}\nStatus: {'COMPLIANT' if safety_factor >= 1.0 else 'NON-COMPLIANT'}"
            st.download_button("Download Official Structural Memo (.txt)", data=memo_txt, file_name=f"beam_calc_{selected_shape if profile_source=='AISC Standard W-Shapes (I-Beam)' else 'Custom'}.txt")

    except Exception as error_msg:
        st.error(f"Solver Exception Event: Mathematical geometric constraint error. Please verify loads sit strictly inside the 0.0m to {length}m span. Details: {error_msg}")
