import streamlit as st
from typing import Tuple

# Define constants for easy maintenance
PERIOD_OPTIONS = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
INTERVAL_OPTIONS = ["1d", "1wk", "1mo"]

def render_controls() -> Tuple[str, str, str]:
    """
    Renders minimalistic trading controls.
    
    Returns:
        Tuple[str, str, str]: (symbol, period, interval)
    """
    # 1. Search Input
    symbol = st.text_input(
        "🔍 Market Search",
        value="AAPL",
        placeholder="e.g. AAPL, NVDA, BTC-USD"
    )

    # 2. Advanced Settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox("History", PERIOD_OPTIONS, index=3)
        with col2:
            interval = st.selectbox("Interval", INTERVAL_OPTIONS, index=0)

    # 3. Quick Select
    quick_select = st.selectbox(
        "Quick Select",
        ["Custom Search", "NVDA", "TSLA", "MSFT", "AMZN", "GOOGL", "BTC-USD", "ETH-USD"],
        index=0
    )

    # Logic: Use Quick Select if active, otherwise use Search Input
    final_symbol = quick_select if quick_select != "Custom Search" else symbol
    
    return final_symbol.strip().upper(), period, interval