# RP-FRAMEWORK-DATA

This repository contains the data and notebooks used to reproduce the figures and tables in our reproduction-probability (RP) evaluation study.

## Repository Structure

### `fig.ipynb`
Generates the main figures used in the paper, including:

- **Fig. 2**
- **Fig. 6**
- **Fig. 7**
- **Fig. 8**
- **Fig. 12**

### `table1&2/`
This folder contains the results used to produce **Table 1** and **Table 2**.

The table results are organised by output type and data type:

- **1_Point/**
  - **Continuous/**
  - **Discrete/**
- **2_Sequence/**
  - **Continuous/**
  - **Discrete/**
- **3_Field/**
  - **Continuous/**
  - **Discrete/**

Within each subfolder, the experimental conditions are separated as:

- **`no-noisy/`**  
  Corresponds to **Condition A**: *aleatory uncertainty only*  
  (i.e., **Table 2: Reproduction results under Condition A**)

- **`has-noisy/`**  
  Corresponds to **Condition B**: *combined aleatory and epistemic uncertainty*  
  (i.e., **Table 3: Reproduction results under Condition B**)

### `case1/` and `case2/`
These two folders contain the evaluation outputs for the **two real-world case studies** reported in the paper:

- **`case1/`**: evaluation results for **Case 1** in the manuscript  
- **`case2/`**: evaluation results for **Case 2** in the manuscript  

(Each case folder includes the corresponding inputs/outputs and notebooks used to compute the reported metrics and visualisations.)

## Notes
- Folder names follow the paper’s output taxonomy: **Point / Sequence / Field** × **Continuous / Discrete**.
- If you only want the clean (aleatory-only) evaluation results, use the `no-noisy/` folders.
- If you want the combined uncertainty results (including epistemic effects), use the `has-noisy/` folders.

## Quick Start
1. Open and run `fig.ipynb` to reproduce figures.
2. Use the corresponding folders under `table1&2/` to locate the data for each table and scenario.
3. Check `case1/` and `case2/` for the evaluation results of the two manuscript case studies.