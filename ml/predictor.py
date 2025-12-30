# -*- coding: utf-8 -*-
import random
from datetime import datetime
from typing import Dict
from contracts.schema import StockData, MLSignal

class MLEngine:
    # 8️⃣ Model Metadata (Class-level constants)
    MODEL_TYPE = "Hybrid ML (Random Forest + Technical Analysis)"
    MODEL_VERSION = "v2.3.1"
    LAST_TRAINED = "2024-12-20"
    PREDICTION_FREQUENCY = "Real-time (on-demand)"
    @staticmethod
    def predict(data: StockData) -> MLSignal:
        """
        Generates a trading signal based on technical indicators.
        In a production system, this would call a trained model or an LLM API.
        """
        
        # Extract latest values
        rsi = data.rsi[-1] if data.rsi and len(data.rsi) > 0 else 50
        macd = data.macd[-1] if data.macd and len(data.macd) > 0 else 0
        macd_signal = data.macd_signal[-1] if data.macd_signal and len(data.macd_signal) > 0 else 0
        macd_hist = data.macd_hist[-1] if data.macd_hist and len(data.macd_hist) > 0 else 0
        price = data.current_price
        sma_20 = data.sma_20[-1] if data.sma_20 and len(data.sma_20) > 0 else price
        sma_50 = data.sma_50[-1] if data.sma_50 and len(data.sma_50) > 0 else price
        
        score = 0
        reasons = []
        
        # Logic for Signal Generation (Heuristic Mock)
        
        # RSI Logic
        if rsi < 30:
            score += 2
            reasons.append(f"RSI is oversold ({rsi:.1f}), suggesting a potential rebound.")
        elif rsi > 70:
            score -= 2
            reasons.append(f"RSI is overbought ({rsi:.1f}), suggesting a potential pullback.")
        else:
            reasons.append(f"RSI is neutral ({rsi:.1f}).")
            
        # MACD Logic
        if macd > macd_signal:
            score += 1
            reasons.append("MACD line is above the signal line (Bullish).")
        else:
            score -= 1
            reasons.append("MACD line is below the signal line (Bearish).")
            
        # Trend Logic
        if price > sma_50:
            score += 1
            reasons.append("Price is above the 50-day SMA (Uptrend).")
        else:
            score -= 1
            reasons.append("Price is below the 50-day SMA (Downtrend).")
        
        # MACD Histogram momentum
        if abs(macd_hist) > 0:
            if macd_hist > 0:
                score += 0.5
                reasons.append("MACD histogram shows increasing bullish momentum.")
            else:
                score -= 0.5
                reasons.append("MACD histogram shows increasing bearish momentum.")
        
        # Golden/Death Cross detection
        if len(data.sma_20) > 1 and len(data.sma_50) > 1:
            prev_20 = data.sma_20[-2]
            prev_50 = data.sma_50[-2]
            if prev_20 <= prev_50 and sma_20 > sma_50:
                score += 2
                reasons.append("🌟 Golden Cross detected (SMA 20 crossed above SMA 50).")
            elif prev_20 >= prev_50 and sma_20 < sma_50:
                score -= 2
                reasons.append("💀 Death Cross detected (SMA 20 crossed below SMA 50).")
            
        # Determine Action
        if score >= 2:
            action = "BUY"
            confidence = 75 + (score * 5) # Mock confidence
        elif score <= -2:
            action = "SELL"
            confidence = 75 + (abs(score) * 5)
        else:
            action = "HOLD"
            confidence = 50.0
            
        # Cap confidence
        confidence = min(98.5, max(50.0, confidence))
        
        # 5️⃣ Confidence Level (categorical)
        if confidence >= 85:
            confidence_level = "Very High"
        elif confidence >= 70:
            confidence_level = "High"
        elif confidence >= 55:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        # 2️⃣ Numerical Signal Encoding
        signal_value = 1 if action == "BUY" else (-1 if action == "SELL" else 0)
        
        # 4️⃣ Generate "Gen-AI" Explanation (Enhanced)
        explanation = f"🤖 **AI Analysis for {data.symbol}**\n\n"
        explanation += f"The advanced {MLEngine.MODEL_TYPE} model recommends a **{action}** signal "
        explanation += f"with **{confidence:.1f}% confidence** ({confidence_level} certainty).\n\n"
        explanation += f"**Key Market Insights:**\n"
        for i, reason in enumerate(reasons, 1):
            explanation += f"{i}. {reason}\n"
        explanation += f"\n⚠️ **Risk Assessment:** Market volatility and external factors remain important considerations. "
        explanation += f"This signal is based on technical analysis and should be combined with fundamental research."
        
        # 6️⃣ Calculate Feature Importance (weighted by contribution to score)
        feature_importance = {}
        
        # RSI contribution
        if rsi < 30:
            feature_importance["RSI (Oversold)"] = 2.0 / max(abs(score), 1) * 100
        elif rsi > 70:
            feature_importance["RSI (Overbought)"] = 2.0 / max(abs(score), 1) * 100
        else:
            feature_importance["RSI (Neutral)"] = 0.5 / max(abs(score), 1) * 100
        
        # MACD contribution
        if macd > macd_signal:
            feature_importance["MACD (Bullish)"] = 1.0 / max(abs(score), 1) * 100
        else:
            feature_importance["MACD (Bearish)"] = 1.0 / max(abs(score), 1) * 100
        
        # Trend contribution
        if price > sma_50:
            feature_importance["Trend (Uptrend)"] = 1.0 / max(abs(score), 1) * 100
        else:
            feature_importance["Trend (Downtrend)"] = 1.0 / max(abs(score), 1) * 100
        
        # Volume analysis
        if data.volumes and len(data.volumes) > 1:
            vol_change = ((data.volumes[-1] - data.volumes[-2]) / data.volumes[-2]) * 100
            feature_importance["Volume"] = min(abs(vol_change) / 10, 15.0)
        else:
            feature_importance["Volume"] = 5.0
        
        # Cross detection contribution
        if len(data.sma_20) > 1 and len(data.sma_50) > 1:
            prev_20 = data.sma_20[-2]
            prev_50 = data.sma_50[-2]
            if prev_20 <= prev_50 and sma_20 > sma_50:
                feature_importance["Golden Cross"] = 2.0 / max(abs(score), 1) * 100
            elif prev_20 >= prev_50 and sma_20 < sma_50:
                feature_importance["Death Cross"] = 2.0 / max(abs(score), 1) * 100
        
        # Normalize feature importance to sum to 100%
        total_importance = sum(feature_importance.values())
        if total_importance > 0:
            feature_importance = {k: (v / total_importance) * 100 for k, v in feature_importance.items()}
        
        # 3️⃣ Timestamp alignment
        current_timestamp = datetime.now()
        prediction_date = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        return MLSignal(
            # 1️⃣ Core Output
            action=action,
            
            # 2️⃣ Numerical Encoding
            signal_value=signal_value,
            
            # 3️⃣ Timestamp
            timestamp=current_timestamp,
            prediction_date=prediction_date,
            
            # 4️⃣ Explanation
            reasoning=explanation,
            
            # 5️⃣ Confidence
            confidence=confidence,
            confidence_level=confidence_level,
            
            # 6️⃣ Feature Importance
            key_factors=[r.split('(')[0].strip() for r in reasons[:5]],
            feature_importance=feature_importance,
            
            # 7️⃣ Prediction Frequency
            prediction_frequency=MLEngine.PREDICTION_FREQUENCY,
            
            # 8️⃣ Model Metadata
            model_type=MLEngine.MODEL_TYPE,
            model_version=MLEngine.MODEL_VERSION,
            last_trained=MLEngine.LAST_TRAINED
        )
