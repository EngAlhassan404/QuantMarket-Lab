# QuantMarket-Lab: From Historical Research to Real-Time Analysis

![Version](https://img.shields.io/badge/Version-3.0.0-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Author](https://img.shields.io/badge/Author-Eng.%20Alhassan%20Ali%20Mubarak%20Bahbah-purple.svg)

A complete toolkit for quantitative market analysis, featuring an end-to-end Python research lab and a multi-mode, real-time statistical dashboard for TradingView. This project provides a workflow to both empirically test market theories and apply those insights in a live trading environment.

---

> ## Project Philosophy: An Empirical Laboratory for Market Theories
>
> This tool was built to explore a fundamental question in financial statistics: **Is there a discernible bias in the daily direction of efficient markets?**
>
> The underlying thesis, inspired by Burton Malkiel's "A Random Walk Down Wall Street," is that in an efficient market, the probability of an asset closing UP on any given day is roughly equal to the probability of it closing DOWN. This suggests a near **50/50 equilibrium** in the _frequency_ of directional days over the long term.
>
> A key insight revealed by this tool is the crucial difference between the **frequency** of directional days and the **magnitude** of price moves. A market can experience a catastrophic crash driven by a few days of massive-magnitude losses, yet the subsequent recovery can consist of a _greater number_ of smaller-magnitude UP days.
>
> This project has now evolved to not only prove these principles but also to provide a live tool for monitoring them in real-time, turning academic findings into a practical analytical edge.

---

## Project Components

This repository contains two main components, each designed for a specific purpose:

### 1. The Research Engine (Python Lab) 🔬
A complete end-to-end data science pipeline for acquiring, cleaning, and analyzing financial data to empirically test market hypotheses. This is the academic foundation of our work.
* *Ideal for researchers, data scientists, and developers.*
* (Details about the Python workflow are below)

### 2. The Live Dashboard (TradingView Indicator) 📈
A multi-mode, real-time statistical dashboard that applies our research findings directly on your charts. It's designed for practical, day-to-day analysis by traders.
* *Ideal for traders and technical analysts.*
* **➡️ [Click here to view the Live Indicator README, Code, and Showcase](./TradingView_Indicator/README.md)**

---

## Key Findings & Included Case Studies (from Python Lab)

The repository includes pre-generated results from several key analyses in the `/case_study_results/` directory. These serve as a quick-start showcase of the platform's capabilities and the core findings of this research.

1.  **Baseline Equilibrium (Gold, 2000-2025):** A 25-year analysis of Gold shows a remarkable balance, with **51.3% UP days** vs. **47.9% DOWN days**.

2.  **Resilience Under Stress (Crisis Periods):**
    - **2016 Brexit Referendum (GBP/USD):** Exhibited a near-perfect balance: **46.4% UP days vs. 53.3% DOWN days**.
    - **2020 COVID-19 Pandemic (WTI Oil):** Despite a historic crash, the full 2020-2021 period had **more UP days (54.1%)** than DOWN days.

3.  **The Exception That Proves the Rule (USD/JPY, 2024):**
    - Analysis of a market with a strong fundamental driver shows a clear directional bias (**58% UP days**), proving that equilibrium can be overcome by powerful trends.

## Project Workflows: Two Paths for Analysis

You can interact with this project in two distinct ways:

### Path A: The Research Engine (Python)
Follow this path if you want to run the full data science pipeline, replicate our findings, or conduct your own research.

1.  **`1_data_acquisition.py`**: The ingestion engine to fetch market data.
2.  **`2_data_cleaning.py`**: The quality assurance gate to clean and process data.
3.  **`3_run_analysis_cli.py`**: The batch processing engine to run analyses via the command line.
4.  **`4_launch_analysis_gui.py`**: The interactive laboratory (Streamlit GUI) for visual exploration.

### Path B: The Live Analysis Tool (TradingView)
For immediate analysis without any local setup, please use our live TradingView indicator.
* **➡️ [Click here for installation instructions and full documentation.](./TradingView_Indicator/README.md)**


## Installation & Setup (For Python Lab)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)[YourUsername]/QuantMarket-Lab.git
    cd QuantMarket-Lab
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    - Open `configs/master_config.yml`.
    - Replace `"YOUR_API_KEY_HERE"` with your personal Alpha Vantage API key.

## How to Run the Python Lab

Execute the scripts from the project's root directory in their numerical order.

1.  **Fetch latest data:**
    ```bash
    python 1_data_acquisition.py
    ```
2.  **Clean the data:**
    ```bash
    python 2_data_cleaning.py
    ```
3.  **Run analysis via CLI (example):**
    ```bash
    python 3_run_analysis_cli.py --asset GOLD --start_date 2020-01-01
    ```
4.  **Launch the interactive GUI:**
    ```bash
    streamlit run 4_launch_analysis_gui.py
    ```
