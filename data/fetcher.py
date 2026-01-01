# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from contracts.schema import StockData

class DataEngine:
    @staticmethod
    def fetch_data(symbol: str, period: str = "1y", interval: str = "1d") -> StockData:
        """
        Fetches market data and calculates technical indicators.
        Cached for 5 minutes to improve performance.
        """
        import streamlit as st
        
        @st.cache_data(ttl=300, show_spinner=False)
        def _fetch_cached(symbol: str, period: str, interval: str) -> dict:
            data = DataEngine._fetch_uncached(symbol, period, interval)
            return data.dict()
        
        data_dict = _fetch_cached(symbol, period, interval)
        return StockData(**data_dict)
    
    @staticmethod
    def _fetch_uncached(symbol: str, period: str, interval: str) -> StockData:
        """Internal method to fetch data without caching"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Calculate Indicators
            df['RSI'] = DataEngine._calculate_rsi(df['Close'])
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
            
            # Fill NaNs for JSON serialization
            df = df.fillna(0)
            
            # Get latest info
            try:
                info = ticker.info
                current_price = info.get('currentPrice', df['Close'].iloc[-1])
                prev_close = info.get('previousClose', df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1])
            except Exception:
                # Fallback if info fetch fails
                current_price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1]

            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100 if prev_close else 0
            
            # Determine market status (simple heuristic)
            # In a real app, we'd check exchange hours
            market_status = "Open" if datetime.now().weekday() < 5 else "Closed"

            return StockData(
                symbol=symbol.upper(),
                current_price=float(current_price),
                price_change=float(price_change),
                price_change_pct=float(price_change_pct),
                last_updated=datetime.now(),
                market_status=market_status,
                dates=df.index.strftime('%Y-%m-%d').tolist(),
                opens=df['Open'].tolist(),
                highs=df['High'].tolist(),
                lows=df['Low'].tolist(),
                closes=df['Close'].tolist(),
                volumes=df['Volume'].astype(int).tolist(),
                rsi=df['RSI'].tolist(),
                sma_20=df['SMA_20'].tolist(),
                sma_50=df['SMA_50'].tolist(),
                ema_12=df['EMA_12'].tolist(),
                ema_26=df['EMA_26'].tolist(),
                macd=df['MACD'].tolist(),
                macd_signal=df['MACD_Signal'].tolist(),
                macd_hist=df['MACD_Hist'].tolist()
            )
            
        except Exception as e:
            raise RuntimeError(f"Data Engineering Error: {str(e)}")

    @staticmethod
    def _calculate_rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
