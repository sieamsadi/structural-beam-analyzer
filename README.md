# Cloud-Based 1D Structural Finite Element Analysis (FEA) Engine

An interactive, production-ready engineering web application designed to compute shear force distribution, internal bending moment variations, and elastic deformation curves for structural components.



[Image of Bending Moment Diagram]


## 🛠️ Engineering Infrastructure & Logic
- **UI Architecture:** Python Streamlit Ecosystem
- **Mathematical Computation Engine:** Euler-Bernoulli dynamic matrix solutions utilizing the `indeterminatebeam` library.
- **Data Rendering Engine:** Dynamic client-ready hover graphs via Plotly API.
- **Section Property Parsing:** Automates extraction of cross-sectional areas and second moment of areas ($I_{zz}$) using an underlying database conforming to **AISC (American Institute of Steel Construction)** configurations.

## 🚀 Deployment & Local Operation
Ensure Python 3.10+ is loaded on local environment path configuration variables.

1. Clone system directory structure locally.
2. Spin up dependency installations via package manager pip script execution:
   ```bash
   pip install -r requirements.txt