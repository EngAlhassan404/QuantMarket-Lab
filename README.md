# QuantMarket-Lab: A Financial Data & Analysis Platform

**Version:** 2.0.0 | **License:** MIT | **Author:** Eng.Alhassan Ali Mubarak Bahbah

An end-to-end platform for acquiring, cleaning, and analyzing financial market data. This project provides a complete, automated workflow to empirically test the "Daily Directional Equilibrium" hypothesis and serves as a practical laboratory for students and researchers in quantitative finance and economics.

---

> ## Project Philosophy: An Empirical Laboratory for Market Theories
>
> This tool was built to explore a fundamental question in financial statistics: **Is there a discernible bias in the daily direction of efficient markets?**
>
> The underlying thesis, inspired by Burton Malkiel's "A Random Walk Down Wall Street," is that in an efficient market, the probability of an asset closing UP on any given day is roughly equal to the probability of it closing DOWN. This suggests a near **50/50 equilibrium** in the _frequency_ of directional days over the long term.
>
> A key insight revealed by this tool is the crucial difference between the **frequency** of directional days and the **magnitude** of price moves. A market can experience a catastrophic crash driven by a few days of massive-magnitude losses, yet the subsequent recovery can consist of a _greater number_ of smaller-magnitude UP days. This directly challenges the simplistic "selling is king" mantra during crises, highlighting that a blind long-term selling strategy would miss the more numerous recovery days.

---

## Key Findings & Included Case Studies

The repository includes pre-generated results from several key analyses in the `/case_study_results/` directory. These serve as a quick-start showcase of the platform's capabilities and the core findings of this research.

1.  **Baseline Equilibrium (Gold, 2000-2025):** A 25-year analysis of Gold shows a remarkable balance, with **51.3% UP days** vs. **47.9% DOWN days**, confirming the long-term equilibrium hypothesis in a relatively neutral asset.

2.  **Resilience Under Stress (Crisis Periods):**

    - **2016 Brexit Referendum (GBP/USD):** During a year of intense political and economic uncertainty, the Pound Sterling still exhibited a near-perfect balance: **46.4% UP days vs. 53.3% DOWN days**. This is a powerful testament to the resilience of the equilibrium theory even amidst a major sovereign crisis.
    - **2008 GFC (USD/CHF):** Maintained a near-perfect balance, demonstrating that equilibrium holds even during systemic financial shocks.
    - **2012 Eurozone Crisis (EUR/USD):** Showed a 50.6% UP vs. 48.3% DOWN ratio, proving the thesis holds in the face of sovereign debt crises.
    - **2020 COVID-19 Pandemic (WTI Oil):** Despite a historic price crash into negative territory, the full 2020-2021 period had **more UP days (54.1%)** than DOWN days, perfectly illustrating that the recovery phase consists of more frequent, smaller gains.

3.  **The Exception That Proves the Rule (USD/JPY, 2024):**
    - Analysis of a market with a strong, persistent fundamental driver (interest rate differentials) shows a clear directional bias (**58% UP days**). This serves as a vital counter-example, proving that the 50/50 equilibrium is a characteristic of balanced markets, which can be overcome by powerful, trending fundamentals.

## The 4-Step Workflow

The platform is organized into a series of numbered scripts in the root directory. Execute them in order to experience the full pipeline.

1.  **`1_data_acquisition.py`**: The ingestion engine. It connects to the Alpha Vantage API, fetches the latest daily data for all assets defined in `configs/master_config.yml`, and intelligently saves it to the `data/raw/` directory.

2.  **`2_data_cleaning.py`**: The quality assurance gate. This script reads the raw data from `data/raw/`, handles duplicates, validates data types, standardizes formats, and saves the clean, analysis-ready version to `data/processed/`.

3.  **`3_run_analysis_cli.py`**: The batch processing engine. A Command-Line Interface (CLI) to run the core statistical analysis on cleaned data. Ideal for automation and generating reports for specific assets and timeframes.

4.  **`4_launch_analysis_gui.py`**: The interactive laboratory. A Streamlit-based Graphical User Interface (GUI) that allows for visual, interactive exploration of the data.

## Installation & Setup

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

## How to Run the Platform

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
