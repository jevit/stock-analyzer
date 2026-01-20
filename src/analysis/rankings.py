"""
Top rankings - Generate investment recommendations by criteria.
"""
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd
from loguru import logger

from src.scoring.scorer import TickerAnalysis
from src.analysis.fundamentals import FundamentalMetrics


@dataclass
class RankedStock:
    """A stock with its ranking score."""
    ticker: str
    name: str
    score: float
    rank: int

    # Key metrics for display
    price: float
    technical_score: int = 0

    # Specific to ranking type
    metric1_label: str = ""
    metric1_value: str = ""
    metric2_label: str = ""
    metric2_value: str = ""
    metric3_label: str = ""
    metric3_value: str = ""

    reason: str = ""


class TopRankings:
    """Generate top stock rankings by various criteria."""

    def __init__(
        self,
        analyses: List[TickerAnalysis],
        fundamentals: Dict[str, FundamentalMetrics],
        data: Dict[str, pd.DataFrame]
    ):
        """
        Initialize rankings.

        Args:
            analyses: List of technical analyses
            fundamentals: Dict of fundamental metrics
            data: Price data
        """
        self.analyses = analyses
        self.fundamentals = fundamentals
        self.data = data

    def get_top_technical(self, n: int = 10) -> List[RankedStock]:
        """
        Get top stocks by technical score.

        Args:
            n: Number of stocks to return

        Returns:
            List of top ranked stocks
        """
        # Sort by technical score
        sorted_analyses = sorted(
            self.analyses,
            key=lambda a: a.global_score,
            reverse=True
        )[:n]

        ranked = []
        for i, a in enumerate(sorted_analyses):
            fund = self.fundamentals.get(a.ticker)

            ranked.append(RankedStock(
                ticker=a.ticker,
                name=a.name or a.ticker,
                score=a.global_score,
                rank=i + 1,
                price=a.close,
                technical_score=a.global_score,
                metric1_label="Signal",
                metric1_value=a.best_strategy or "Aucun",
                metric2_label="RSI",
                metric2_value=f"{a.rsi:.0f}" if a.rsi else "—",
                metric3_label="Tendance",
                metric3_value=a.trend_status,
                reason=a.verdict
            ))

        return ranked

    def get_top_momentum(self, n: int = 10) -> List[RankedStock]:
        """
        Get top momentum stocks (strong recent performance).

        Args:
            n: Number of stocks to return

        Returns:
            List of top momentum stocks
        """
        momentum_scores = []

        for a in self.analyses:
            df = self.data.get(a.ticker)
            if df is None or len(df) < 60:
                continue

            # Calculate returns
            ret_1m = ((df['Close'].iloc[-1] / df['Close'].iloc[-20]) - 1) * 100 if len(df) >= 20 else 0
            ret_3m = ((df['Close'].iloc[-1] / df['Close'].iloc[-60]) - 1) * 100 if len(df) >= 60 else 0

            # Momentum score: weighted average
            momentum = (ret_1m * 0.6 + ret_3m * 0.4)

            # Bonus for strong volume
            vol_bonus = 10 if a.volume_ratio and a.volume_ratio > 1.5 else 0

            # Bonus for uptrend
            trend_bonus = 15 if a.dist_sma200_pct and a.dist_sma200_pct > 5 else 0

            total_score = momentum + vol_bonus + trend_bonus

            momentum_scores.append({
                'analysis': a,
                'score': total_score,
                'ret_1m': ret_1m,
                'ret_3m': ret_3m
            })

        # Sort by momentum score
        sorted_momentum = sorted(momentum_scores, key=lambda x: x['score'], reverse=True)[:n]

        ranked = []
        for i, item in enumerate(sorted_momentum):
            a = item['analysis']

            reason = f"+{item['ret_1m']:.1f}% sur 1M, +{item['ret_3m']:.1f}% sur 3M"

            ranked.append(RankedStock(
                ticker=a.ticker,
                name=a.name or a.ticker,
                score=item['score'],
                rank=i + 1,
                price=a.close,
                technical_score=a.global_score,
                metric1_label="Perf 1M",
                metric1_value=f"+{item['ret_1m']:.1f}%" if item['ret_1m'] > 0 else f"{item['ret_1m']:.1f}%",
                metric2_label="Perf 3M",
                metric2_value=f"+{item['ret_3m']:.1f}%" if item['ret_3m'] > 0 else f"{item['ret_3m']:.1f}%",
                metric3_label="Volume",
                metric3_value=f"{a.volume_ratio:.1f}x" if a.volume_ratio else "—",
                reason=reason
            ))

        return ranked

    def get_top_value(self, n: int = 10) -> List[RankedStock]:
        """
        Get top value stocks (undervalued fundamentals).

        Args:
            n: Number of stocks to return

        Returns:
            List of top value stocks
        """
        value_stocks = []

        for a in self.analyses:
            fund = self.fundamentals.get(a.ticker)
            if not fund or fund.value_score == 0:
                continue

            # Combined score: fundamentals + technical bonus
            combined_score = fund.value_score + (a.global_score * 0.2)

            value_stocks.append({
                'analysis': a,
                'fund': fund,
                'score': combined_score
            })

        # Sort by value score
        sorted_value = sorted(value_stocks, key=lambda x: x['score'], reverse=True)[:n]

        ranked = []
        for i, item in enumerate(sorted_value):
            a = item['analysis']
            fund = item['fund']

            pe_str = f"{fund.pe_ratio:.1f}" if fund.pe_ratio else "—"
            pb_str = f"{fund.pb_ratio:.1f}" if fund.pb_ratio else "—"

            reason = f"P/E: {pe_str}, P/B: {pb_str}"
            if fund.profit_margin:
                reason += f", Marge: {fund.profit_margin:.1f}%"

            ranked.append(RankedStock(
                ticker=a.ticker,
                name=a.name or a.ticker,
                score=item['score'],
                rank=i + 1,
                price=a.close,
                technical_score=a.global_score,
                metric1_label="P/E",
                metric1_value=pe_str,
                metric2_label="P/B",
                metric2_value=pb_str,
                metric3_label="Score Value",
                metric3_value=f"{fund.value_score}/100",
                reason=reason
            ))

        return ranked

    def get_top_growth(self, n: int = 10) -> List[RankedStock]:
        """
        Get top growth stocks (high growth metrics).

        Args:
            n: Number of stocks to return

        Returns:
            List of top growth stocks
        """
        growth_stocks = []

        for a in self.analyses:
            fund = self.fundamentals.get(a.ticker)
            if not fund or fund.growth_score == 0:
                continue

            # Combined score
            combined_score = fund.growth_score + (a.global_score * 0.15)

            growth_stocks.append({
                'analysis': a,
                'fund': fund,
                'score': combined_score
            })

        # Sort by growth score
        sorted_growth = sorted(growth_stocks, key=lambda x: x['score'], reverse=True)[:n]

        ranked = []
        for i, item in enumerate(sorted_growth):
            a = item['analysis']
            fund = item['fund']

            rev_growth = f"+{fund.revenue_growth:.1f}%" if fund.revenue_growth else "—"
            earn_growth = f"+{fund.earnings_growth:.1f}%" if fund.earnings_growth else "—"

            reason = f"Croissance revenus: {rev_growth}"
            if fund.earnings_growth:
                reason += f", bénéfices: {earn_growth}"

            ranked.append(RankedStock(
                ticker=a.ticker,
                name=a.name or a.ticker,
                score=item['score'],
                rank=i + 1,
                price=a.close,
                technical_score=a.global_score,
                metric1_label="Rev Growth",
                metric1_value=rev_growth,
                metric2_label="Earn Growth",
                metric2_value=earn_growth,
                metric3_label="Score Growth",
                metric3_value=f"{fund.growth_score}/100",
                reason=reason
            ))

        return ranked

    def get_top_dividend(self, n: int = 10) -> List[RankedStock]:
        """
        Get top dividend stocks.

        Args:
            n: Number of stocks to return

        Returns:
            List of top dividend stocks
        """
        dividend_stocks = []

        for a in self.analyses:
            fund = self.fundamentals.get(a.ticker)
            if not fund or fund.dividend_score == 0:
                continue

            # Combined score
            combined_score = fund.dividend_score + (a.global_score * 0.1)

            dividend_stocks.append({
                'analysis': a,
                'fund': fund,
                'score': combined_score
            })

        # Sort by dividend score
        sorted_div = sorted(dividend_stocks, key=lambda x: x['score'], reverse=True)[:n]

        ranked = []
        for i, item in enumerate(sorted_div):
            a = item['analysis']
            fund = item['fund']

            div_yield = f"{fund.dividend_yield:.2f}%" if fund.dividend_yield else "—"
            payout = f"{fund.payout_ratio:.0f}%" if fund.payout_ratio else "—"

            reason = f"Rendement: {div_yield}, Payout: {payout}"

            ranked.append(RankedStock(
                ticker=a.ticker,
                name=a.name or a.ticker,
                score=item['score'],
                rank=i + 1,
                price=a.close,
                technical_score=a.global_score,
                metric1_label="Rendement",
                metric1_value=div_yield,
                metric2_label="Payout",
                metric2_value=payout,
                metric3_label="Score Div",
                metric3_value=f"{fund.dividend_score}/100",
                reason=reason
            ))

        return ranked

    def get_top_quality(self, n: int = 10) -> List[RankedStock]:
        """
        Get top quality stocks (best fundamentals).

        Args:
            n: Number of stocks to return

        Returns:
            List of top quality stocks
        """
        quality_stocks = []

        for a in self.analyses:
            fund = self.fundamentals.get(a.ticker)
            if not fund or fund.quality_score == 0:
                continue

            # Combined score
            combined_score = fund.quality_score + (a.global_score * 0.3)

            quality_stocks.append({
                'analysis': a,
                'fund': fund,
                'score': combined_score
            })

        # Sort by quality score
        sorted_quality = sorted(quality_stocks, key=lambda x: x['score'], reverse=True)[:n]

        ranked = []
        for i, item in enumerate(sorted_quality):
            a = item['analysis']
            fund = item['fund']

            roe = f"{fund.roe:.1f}%" if fund.roe else "—"
            margin = f"{fund.profit_margin:.1f}%" if fund.profit_margin else "—"

            reason = f"ROE: {roe}, Marge: {margin}"

            ranked.append(RankedStock(
                ticker=a.ticker,
                name=a.name or a.ticker,
                score=item['score'],
                rank=i + 1,
                price=a.close,
                technical_score=a.global_score,
                metric1_label="ROE",
                metric1_value=roe,
                metric2_label="Marge",
                metric2_value=margin,
                metric3_label="Score Qualité",
                metric3_value=f"{fund.quality_score}/100",
                reason=reason
            ))

        return ranked

    def get_top_defensive(self, n: int = 10) -> List[RankedStock]:
        """
        Get top defensive stocks (low volatility).

        Args:
            n: Number of stocks to return

        Returns:
            List of top defensive stocks
        """
        defensive_stocks = []

        for a in self.analyses:
            if not a.atr_pct:
                continue

            fund = self.fundamentals.get(a.ticker)

            # Lower volatility = higher score
            volatility_score = max(0, 100 - (a.atr_pct * 10))

            # Bonus for dividends
            div_bonus = 0
            if fund and fund.dividend_yield:
                div_bonus = min(20, fund.dividend_yield * 5)

            # Bonus for positive trend
            trend_bonus = 10 if a.dist_sma200_pct and a.dist_sma200_pct > 0 else 0

            total_score = volatility_score + div_bonus + trend_bonus

            defensive_stocks.append({
                'analysis': a,
                'fund': fund,
                'score': total_score,
                'volatility': a.atr_pct
            })

        # Sort by defensive score
        sorted_def = sorted(defensive_stocks, key=lambda x: x['score'], reverse=True)[:n]

        ranked = []
        for i, item in enumerate(sorted_def):
            a = item['analysis']
            fund = item['fund']

            div_yield = f"{fund.dividend_yield:.2f}%" if fund and fund.dividend_yield else "—"

            reason = f"Volatilité faible: {item['volatility']:.2f}%"
            if fund and fund.dividend_yield:
                reason += f", Dividende: {div_yield}"

            ranked.append(RankedStock(
                ticker=a.ticker,
                name=a.name or a.ticker,
                score=item['score'],
                rank=i + 1,
                price=a.close,
                technical_score=a.global_score,
                metric1_label="Volatilité",
                metric1_value=f"{item['volatility']:.2f}%",
                metric2_label="Dividende",
                metric2_value=div_yield,
                metric3_label="Tendance",
                metric3_value=a.trend_status,
                reason=reason
            ))

        return ranked
