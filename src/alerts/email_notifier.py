"""
Email notification system.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from loguru import logger

from config.settings import get_settings
from src.scoring.scorer import TickerAnalysis


class EmailNotifier:
    """Send alerts via email."""

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        email_from: Optional[str] = None,
        email_password: Optional[str] = None,
        email_to: Optional[str] = None
    ):
        """
        Initialize email notifier.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port (587 for TLS)
            email_from: Sender email
            email_password: Email password or app password
            email_to: Recipient email
        """
        settings = get_settings()
        self.smtp_server = smtp_server or settings.smtp_server
        self.smtp_port = smtp_port or settings.smtp_port
        self.email_from = email_from or settings.email_from
        self.email_password = email_password or settings.email_password
        self.email_to = email_to or settings.email_to

    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return all([
            self.smtp_server,
            self.smtp_port,
            self.email_from,
            self.email_password,
            self.email_to
        ])

    def send_email(self, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """
        Send an email.

        Args:
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback (optional)

        Returns:
            True if sent successfully
        """
        if not self.is_configured():
            logger.warning("Email not configured - skipping notification")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_from
            msg['To'] = self.email_to

            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)

            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.email_from, self.email_password)
                server.sendmail(self.email_from, self.email_to, msg.as_string())

            logger.info(f"Email sent successfully to {self.email_to}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def format_alert_email(self, analyses: List[TickerAnalysis], min_score: int = 75) -> tuple:
        """
        Format analysis results into an email.

        Args:
            analyses: List of TickerAnalysis
            min_score: Minimum score to include

        Returns:
            Tuple of (subject, html_body, text_body)
        """
        # Filter by score
        alerts = [a for a in analyses if a.global_score >= min_score and a.has_signal]

        if not alerts:
            return None, None, None

        # Subject
        subject = f"📊 Stock Analyzer - {len(alerts)} signal(s) détecté(s)"

        # HTML body
        html_parts = [
            "<html><head><style>",
            "body { font-family: Arial, sans-serif; color: #333; }",
            ".header { background: #1e88e5; color: white; padding: 20px; }",
            ".alert { border-left: 4px solid #4caf50; padding: 15px; margin: 15px 0; background: #f5f5f5; }",
            ".high-score { border-left-color: #2e7d32; }",
            ".ticker { font-size: 1.3em; font-weight: bold; color: #1565c0; }",
            ".strategy { color: #6a1b9a; font-weight: bold; }",
            ".price { color: #f57c00; }",
            ".footer { margin-top: 30px; padding: 20px; background: #ffeaa7; border-left: 4px solid #fdcb6e; }",
            "</style></head><body>",
            "<div class='header'>",
            f"<h1>📊 Stock Analyzer</h1>",
            f"<p>{len(alerts)} signal(s) détecté(s) (score ≥ {min_score})</p>",
            "</div>",
        ]

        for a in alerts[:15]:  # Limit to top 15
            score_class = "high-score" if a.global_score >= 80 else ""
            emoji = "🚀" if "Breakout" in a.best_strategy else "📈" if "Pullback" in a.best_strategy else "🔄"

            html_parts.append(f"<div class='alert {score_class}'>")
            html_parts.append(f"<div class='ticker'>{emoji} {a.ticker}")
            if a.name and a.name != a.ticker:
                html_parts.append(f" - {a.name}")
            html_parts.append(f"</div>")
            html_parts.append(f"<p><strong>Score:</strong> {a.global_score}/100</p>")
            html_parts.append(f"<p><strong class='strategy'>Stratégie:</strong> {a.best_strategy}</p>")
            html_parts.append(f"<p><strong class='price'>Prix:</strong> {a.close:.2f}")

            if a.rsi:
                rsi_color = "#ef5350" if a.rsi > 70 else "#26a69a" if a.rsi < 30 else "#666"
                html_parts.append(f" | <strong>RSI:</strong> <span style='color:{rsi_color}'>{a.rsi:.1f}</span>")

            html_parts.append("</p>")

            # Main reason
            if a.reasons:
                main_reason = next(
                    (r for r in a.reasons if not r.startswith("⭐")),
                    a.reasons[0]
                )
                html_parts.append(f"<p>📌 {main_reason}</p>")

            # Technical levels
            if a.entry_level and a.target_level and a.invalidation_level:
                html_parts.append("<p style='font-size:0.9em; color:#666;'>")
                html_parts.append(f"🎯 Entrée: {a.entry_level:.2f} | ")
                html_parts.append(f"🎁 Objectif: {a.target_level:.2f} | ")
                html_parts.append(f"🛑 Stop: {a.invalidation_level:.2f} | ")
                html_parts.append(f"R/R: {a.risk_reward_ratio:.1f}")
                html_parts.append("</p>")

            html_parts.append("</div>")

        # Footer disclaimer
        html_parts.append("<div class='footer'>")
        html_parts.append("<strong>⚠️ Avertissement Important</strong><br>")
        html_parts.append("Cette analyse technique est fournie à titre éducatif uniquement. ")
        html_parts.append("Elle ne constitue en aucun cas un conseil en investissement. ")
        html_parts.append("Faites toujours vos propres recherches.")
        html_parts.append("</div>")

        html_parts.append("</body></html>")

        html_body = "\n".join(html_parts)

        # Plain text version
        text_parts = [
            f"Stock Analyzer - Alertes",
            f"{len(alerts)} signal(s) détecté(s) (score >= {min_score})",
            "",
        ]

        for a in alerts[:15]:
            emoji = "**" if a.global_score >= 80 else "*"
            text_parts.append(f"{emoji} {a.ticker} - Score: {a.global_score}/100")
            text_parts.append(f"   Stratégie: {a.best_strategy}")
            text_parts.append(f"   Prix: {a.close:.2f}" + (f" | RSI: {a.rsi:.1f}" if a.rsi else ""))

            if a.reasons:
                main_reason = next((r for r in a.reasons if not r.startswith("⭐")), a.reasons[0])
                text_parts.append(f"   → {main_reason[:80]}")

            text_parts.append("")

        text_parts.append("-" * 50)
        text_parts.append("⚠️ Analyse technique uniquement - Pas de conseil financier")

        text_body = "\n".join(text_parts)

        return subject, html_body, text_body

    def send_daily_alert(self, analyses: List[TickerAnalysis], min_score: int = 75) -> bool:
        """
        Send daily alert with top opportunities.

        Args:
            analyses: List of TickerAnalysis
            min_score: Minimum score threshold

        Returns:
            True if sent successfully (or no alerts to send)
        """
        subject, html_body, text_body = self.format_alert_email(analyses, min_score)

        if not subject:
            logger.info(f"No signals with score >= {min_score} - no alert sent")
            return True

        return self.send_email(subject, html_body, text_body)

    def test_connection(self) -> bool:
        """Test email connection by sending a test message."""
        if not self.is_configured():
            return False

        html = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background: #4caf50; color: white; padding: 20px;">
                <h1>✅ Test de connexion réussi!</h1>
            </div>
            <div style="padding: 20px;">
                <p>Votre configuration email fonctionne correctement pour Stock Analyzer.</p>
                <p>Vous recevrez maintenant des alertes quand des signaux forts seront détectés.</p>
            </div>
        </body>
        </html>
        """

        text = "✅ Test de connexion réussi! Votre configuration email fonctionne pour Stock Analyzer."

        return self.send_email("🔔 Stock Analyzer - Test de connexion", html, text)
