# 🏗️ Enterprise Structural Beam Analyzer & FEA Engine

A production-grade, cloud-accessible 1D Finite Element Analysis (FEA) solver engineered to compute internal forces, bending moments, and elastic deflection curves for structural components. 

### 🌐 Live Application
Test the interactive, mobile-responsive dashboard here: **[structural-beam-analyzer.streamlit.app](https://structural-beam-analyzer.streamlit.app/)**

---

## 🎯 The Business & Freelance Value
Engineers and contractors frequently need to run quick, compliant structural validation checks on-site or during client consultations. Desktop suites like ANSYS, SAP2000, or specialized CAD modules are expensive, heavily licensed, and clunky on portable devices.

**This application provides a lightweight SaaS alternative:**
* **Zero License Overhead:** Accessible from any tablet or smartphone in the field.
* **Instant Database Cross-Referencing:** Pulls real-world structural data instantly rather than requiring manual lookups.
* **Rapid Iteration:** Clients can swap loads, change materials, and view safety factors instantly, dramatically cutting down estimation time.

---

## 🚀 Key Features

* **AISC Database Integration:** Automatically reads a structural steel database to parse real-world properties for W-Shapes (I-Beams).
* **Multi-Load Support:** Dynamically handles multiple concurrent point loads ($PointLoadV$) and Uniformly Distributed Loads ($UDLV$).
* **Boundary Configurations:** Easily switches between **Simply Supported** (Pin/Roller), **Cantilever** (Fixed/Free), and **Fixed-Fixed** conditions.
* **Interactive Visualizations:** Renders zoomable, hover-responsive Bending Moment Diagrams (BMD) and exaggerated Elastic Deflection Curves via Plotly.
* **Real-time Safety Auditing:** Dynamically calculates maximum flexural stress and outputs an instantaneous **Factor of Safety (FoS)** margin.

---

## 🧮 Theoretical Background

The calculation core uses a 1D stiffness matrix array to solve beam mechanics based on **Euler-Bernoulli Beam Theory**. 

### 1. Flexural Stress Calculation
Normal bending stress ($\sigma$) is computed at the extreme fibers of the beam cross-section using the flexural formula:

$$\sigma = \frac{M}{Z}$$

Where:
* $M$ = Local Bending Moment ($N \cdot m$)
* $Z$ = Elastic Section Modulus ($m^3$), derived from the Second Moment of Area ($I_{zz}$) and distance to the neutral axis ($y_{max}$) via $Z = \frac{I}{y_{max}}$.

### 2. Design Compliance
The system automatically audits structural integrity by comparing maximum induced stress against the material's structural limits:

$$\text{Factor of Safety (FoS)} = \frac{\sigma_{\text{yield}}}{\sigma_{\text{max}}}$$

* **FoS $\ge$ 1.5:** Fully compliant structural margin (Green indicator).
* **1.0 $\le$ FoS < 1.5:** Marginal/Warning threshold (Orange indicator).
* **FoS < 1.0:** Structural failure via plastic deformation (Red failure alert).

---

## 💻 Tech Stack & Architecture

* **UI Framework:** Streamlit
* **FEA Solver Core:** `indeterminatebeam` (SciPy & SymPy backend)
* **Data Pipelines:** Pandas & NumPy
* **Graphics Suite:** Plotly WebGL (Scatter & Fill Traces)

---


