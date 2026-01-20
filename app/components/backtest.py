"""
Backtesting page - Test strategies on historical data.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.backtest.engine import BacktestEngine
from src.backtest.results import analyze_by_strategy, create_equity_curve


def render_backtest_page():
    """Render the backtesting page."""
    st.title("📈 Backtesting")

    st.markdown("""
    Testez les stratégies de trading sur les données historiques pour voir comment elles auraient performé.
    """)

    # Check if data is loaded
    if not st.session_state.get("data_loaded"):
        st.warning("⚠️ Chargez d'abord des données depuis le tableau de bord")
        if st.button("📊 Aller au tableau de bord"):
            st.switch_page("main.py")
        return

    data = st.session_state.get("data", {})

    if not data:
        st.error("Aucune donnée disponible")
        return

    # Configuration section
    st.markdown("---")
    st.header("⚙️ Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        lookback_days = st.selectbox(
            "Période de test",
            options=[90, 180, 365, 730, 1095],
            index=2,
            format_func=lambda x: f"{x} jours ({x//365}Y)" if x >= 365 else f"{x} jours",
            help="📅 Période historique sur laquelle tester la stratégie. Plus la période est longue, plus les résultats sont statistiquement fiables, mais le calcul prendra plus de temps."
        )

    with col2:
        max_holding_days = st.slider(
            "Durée max de détention",
            min_value=5,
            max_value=60,
            value=30,
            help="⏱️ Durée maximale pendant laquelle une position peut être maintenue. Au-delà de ce délai, la position est automatiquement clôturée (protection contre les positions stagnantes)."
        )

    with col3:
        slippage = st.slider(
            "Slippage (%)",
            min_value=0.0,
            max_value=0.5,
            value=0.1,
            step=0.05,
            help="💸 Coût estimé de l'exécution (écart entre prix théorique et prix réel). Inclut les frais de courtage et l'écart d'exécution. 0.1% = réaliste pour la plupart des courtiers."
        )

    # Strategy selection
    strategy_choice = st.radio(
        "Stratégie à tester",
        options=["Toutes", "Trend Pullback", "Breakout", "Mean Reversion", "MACD Crossover", "Golden Cross", "Volume Breakout"],
        horizontal=False,
        help="🎯 Choisissez quelle stratégie backtester. 'Toutes' testera les 6 stratégies et comparera leurs performances."
    )

    strategy_name = None if strategy_choice == "Toutes" else strategy_choice

    # Run backtest button
    if st.button("🚀 Lancer le Backtest", type="primary"):
        with st.spinner("Backtesting en cours... Cela peut prendre quelques minutes."):
            # Create engine
            engine = BacktestEngine(
                lookback_days=lookback_days,
                max_holding_days=max_holding_days,
                slippage_pct=slippage
            )

            # Run backtest
            all_trades = engine.backtest_all(data, strategy_name=strategy_name)

            # Analyze results
            results_by_strategy = analyze_by_strategy(all_trades)

            # Store in session state
            st.session_state["backtest_trades"] = all_trades
            st.session_state["backtest_results"] = results_by_strategy
            st.session_state["backtest_config"] = {
                "lookback_days": lookback_days,
                "max_holding_days": max_holding_days,
                "slippage": slippage,
                "strategy": strategy_choice
            }

        st.success("✅ Backtest terminé!")
        st.rerun()

    # Display results if available
    if "backtest_results" in st.session_state:
        st.markdown("---")
        st.header("📊 Résultats")

        results = st.session_state["backtest_results"]
        config = st.session_state.get("backtest_config", {})

        # Summary metrics
        st.subheader(f"📅 Période: {config.get('lookback_days', 365)} jours | Stratégie: {config.get('strategy', 'Toutes')}")

        # Tabs for each strategy
        strategy_tabs = st.tabs(list(results.keys()))

        for i, (strategy_name, result) in enumerate(results.items()):
            with strategy_tabs[i]:
                render_strategy_results(strategy_name, result, st.session_state["backtest_trades"])

        # Export section
        st.markdown("---")
        st.subheader("💾 Export")

        if st.button("📥 Télécharger les trades (CSV)"):
            df_trades = create_trades_export(st.session_state["backtest_trades"])
            csv = df_trades.to_csv(index=False)

            st.download_button(
                label="Télécharger CSV",
                data=csv,
                file_name=f"backtest_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


def render_strategy_results(strategy_name: str, result, all_trades):
    """Render results for a single strategy."""

    # Key metrics in cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        win_rate_color = "normal" if result.win_rate_pct >= 50 else "inverse"
        st.metric(
            "🎯 Taux de réussite",
            f"{result.win_rate_pct:.1f}%",
            delta=f"{result.winning_trades}/{result.total_trades}",
            delta_color=win_rate_color
        )

    with col2:
        st.metric(
            "📊 Gain moyen",
            f"+{result.avg_win_pct:.2f}%",
            delta=f"vs -{abs(result.avg_loss_pct):.2f}% perte moy"
        )

    with col3:
        profit_color = "normal" if result.profit_factor > 1 else "inverse"
        st.metric(
            "💰 Profit Factor",
            f"{result.profit_factor:.2f}",
            delta="Bon" if result.profit_factor > 1.5 else "Faible",
            delta_color=profit_color
        )

    with col4:
        st.metric(
            "📈 Return total",
            f"{result.total_return_pct:+.1f}%",
            delta=f"{result.avg_return_pct:+.2f}% par trade"
        )

    # Detailed stats
    st.markdown("---")
    st.subheader("📋 Statistiques détaillées")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Performance**")
        st.text(f"Total trades:        {result.total_trades}")
        st.text(f"  Gagnants:          {result.winning_trades} ({result.win_rate_pct:.1f}%)")
        st.text(f"  Perdants:          {result.losing_trades}")
        st.text(f"Meilleur trade:      +{result.best_trade_pct:.2f}%")
        st.text(f"Pire trade:          {result.worst_trade_pct:.2f}%")

    with col2:
        st.markdown("**Risk Management**")
        st.text(f"R/R moyen réalisé:   {result.avg_rr_realized:.2f}")
        st.text(f"Max drawdown:        {result.max_drawdown_pct:.2f}%")
        st.text(f"Max pertes consec:   {result.max_consecutive_losses}")
        st.text(f"")
        st.text(f"")

    with col3:
        st.markdown("**Durée & Sorties**")
        st.text(f"Durée moyenne:       {result.avg_duration_days:.1f} jours")
        st.text(f"  Gains:             {result.avg_win_duration_days:.1f} j")
        st.text(f"  Pertes:            {result.avg_loss_duration_days:.1f} j")
        st.text(f"")
        st.text(f"Take Profit:         {result.take_profit_exits} ({result.take_profit_exits/result.total_trades*100:.0f}%)")
        st.text(f"Stop Loss:           {result.stop_loss_exits} ({result.stop_loss_exits/result.total_trades*100:.0f}%)")
        st.text(f"Timeout:             {result.timeout_exits} ({result.timeout_exits/result.total_trades*100:.0f}%)")

    # Equity curve
    st.markdown("---")
    st.subheader("📈 Courbe d'équité")

    # Get trades for this strategy
    strategy_trades = []
    for ticker_trades in all_trades.values():
        for trade in ticker_trades:
            if trade.strategy == strategy_name or strategy_name == "All Strategies":
                if trade.is_closed:
                    strategy_trades.append(trade)

    if strategy_trades:
        equity_df = create_equity_curve(strategy_trades)

        if not equity_df.empty:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=equity_df['Date'],
                y=equity_df['Cumulative_Return'],
                mode='lines',
                name='Return cumulé',
                line=dict(color='#2e7d32', width=2),
                fill='tozeroy',
                fillcolor='rgba(46, 125, 50, 0.1)'
            ))

            # Add zero line
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

            fig.update_layout(
                title="Performance cumulée (%)",
                xaxis_title="Date",
                yaxis_title="Return cumulé (%)",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

    # Recent trades table
    st.markdown("---")
    st.subheader("📋 Derniers trades")

    if strategy_trades:
        # Sort by date descending
        recent_trades = sorted(strategy_trades, key=lambda x: x.exit_date, reverse=True)[:20]

        trades_data = []
        for trade in recent_trades:
            result_emoji = "✅" if trade.is_winner else "❌"
            exit_emoji = {
                "take_profit": "🎯",
                "stop_loss": "🛑",
                "timeout": "⏱️",
                "end_of_data": "📊"
            }.get(trade.exit_reason, "")

            trades_data.append({
                "": result_emoji,
                "Ticker": trade.ticker,
                "Entrée": trade.entry_date.strftime("%d/%m/%y"),
                "Sortie": trade.exit_date.strftime("%d/%m/%y") if trade.exit_date else "",
                "Durée (j)": trade.duration_days,
                "P&L": f"{trade.pnl_pct:+.2f}%",
                "Exit": f"{exit_emoji} {trade.exit_reason}",
            })

        df_trades = pd.DataFrame(trades_data)
        st.dataframe(df_trades, use_container_width=True, hide_index=True)


def create_trades_export(all_trades):
    """Create a DataFrame for CSV export."""
    export_data = []

    for ticker, trades in all_trades.items():
        for trade in trades:
            if trade.is_closed:
                export_data.append({
                    "Ticker": trade.ticker,
                    "Strategy": trade.strategy,
                    "Entry_Date": trade.entry_date.strftime("%Y-%m-%d"),
                    "Entry_Price": f"{trade.entry_price:.2f}",
                    "Exit_Date": trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else "",
                    "Exit_Price": f"{trade.exit_price:.2f}" if trade.exit_price else "",
                    "Exit_Reason": trade.exit_reason,
                    "Duration_Days": trade.duration_days,
                    "PnL_%": f"{trade.pnl_pct:.2f}",
                    "Result": "WIN" if trade.is_winner else "LOSS",
                    "Stop_Loss": f"{trade.stop_loss:.2f}",
                    "Take_Profit": f"{trade.take_profit:.2f}",
                    "RR_Realized": f"{trade.risk_reward_realized:.2f}",
                })

    return pd.DataFrame(export_data)
