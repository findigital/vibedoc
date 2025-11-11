"""
VibeDoc Custom Gradio Theme
Modern, award-winning design inspired by monday.com
"""

import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes

class VibeDocTheme(Base):
    """
    Custom Gradio theme with monday.com-inspired design

    Features:
    - Bold, vibrant colors
    - Modern typography
    - Smooth animations
    - Generous spacing
    - Accessible contrasts
    """

    def __init__(
        self,
        *,
        primary_hue=colors.purple,
        secondary_hue=colors.green,
        neutral_hue=colors.gray,
        spacing_size=sizes.spacing_lg,
        radius_size=sizes.radius_lg,
        text_size=sizes.text_lg,
        font=(
            fonts.GoogleFont("Inter"),
            "ui-sans-serif",
            "system-ui",
            "sans-serif",
        ),
        font_mono=(
            fonts.GoogleFont("JetBrains Mono"),
            "ui-monospace",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )

        # Color customizations
        self.set(
            # Primary colors - Electric Purple
            button_primary_background_fill="#6161FF",
            button_primary_background_fill_hover="#5151E5",
            button_primary_background_fill_dark="#6161FF",
            button_primary_background_fill_hover_dark="#7A7AFF",
            button_primary_text_color="white",
            button_primary_text_color_dark="white",

            # Secondary colors - Success Green
            button_secondary_background_fill="#00CA72",
            button_secondary_background_fill_hover="#00B365",
            button_secondary_text_color="white",

            # Border and focus
            input_border_color="#E6E9EF",
            input_border_color_focus="#6161FF",
            input_border_width="2px",
            input_shadow_focus="0 0 0 4px rgba(97, 97, 255, 0.1)",

            # Backgrounds
            background_fill_primary="white",
            background_fill_secondary="#F6F7FB",

            # Shadows - more pronounced
            shadow_drop="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            shadow_drop_lg="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",

            # Border radius - more rounded
            button_large_radius="12px",
            button_small_radius="8px",
            container_radius="16px",

            # Spacing - more generous
            button_large_padding="14px 28px",
            button_small_padding="8px 16px",

            # Typography
            text_lg="18px",
            text_md="16px",
            text_sm="14px",
        )

# Create theme instance
vibedoc_theme = VibeDocTheme()

# Custom CSS for advanced styling
VIBEDOC_CSS = """
/* ============================================================================
   VibeDoc Custom Styles
   Modern, award-winning design with smooth micro-interactions
   ============================================================================ */

/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ============================================================================
   CSS Variables (Design Tokens)
   ============================================================================ */
:root {
    /* Colors - Primary */
    --primary-500: #6161FF;
    --primary-600: #5151E5;
    --primary-700: #4141CC;
    --primary-400: #7A7AFF;
    --primary-300: #9999FF;

    /* Colors - Secondary */
    --success-500: #00CA72;
    --success-600: #00B365;
    --warning-500: #FDAB3D;
    --error-500: #E44258;
    --info-500: #0085FF;

    /* Colors - Neutral */
    --neutral-900: #1F1F1F;
    --neutral-800: #323338;
    --neutral-700: #676879;
    --neutral-500: #C5C7D0;
    --neutral-300: #E6E9EF;
    --neutral-100: #F6F7FB;
    --neutral-50: #FFFFFF;

    /* Colors - Accent */
    --accent-purple: #A25DDC;
    --accent-pink: #FF6AC3;
    --accent-orange: #FF7A59;
    --accent-blue: #579BFC;
    --accent-teal: #00D4C8;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --shadow-primary: 0 10px 30px -5px rgba(97, 97, 255, 0.3);
    --shadow-success: 0 10px 30px -5px rgba(0, 202, 114, 0.3);

    /* Animations */
    --ease-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);
    --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --duration-fast: 150ms;
    --duration-normal: 250ms;
    --duration-slow: 350ms;
}

/* ============================================================================
   Global Styles
   ============================================================================ */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

body {
    background: linear-gradient(135deg, #F6F7FB 0%, #E6E9EF 100%) !important;
    min-height: 100vh;
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* ============================================================================
   Animations & Keyframes
   ============================================================================ */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

@keyframes scaleIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes success-bounce {
    0% { transform: scale(0); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* ============================================================================
   Container & Layout
   ============================================================================ */
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    animation: fadeIn 0.5s var(--ease-smooth);
}

/* Header styling */
.gradio-container h1 {
    background: linear-gradient(135deg, var(--primary-500) 0%, var(--accent-purple) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
    font-size: 3rem !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem !important;
    animation: slideUp 0.6s var(--ease-bounce);
}

.gradio-container h2 {
    color: var(--neutral-800);
    font-weight: 700 !important;
    font-size: 2rem !important;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
}

.gradio-container h3 {
    color: var(--neutral-800);
    font-weight: 600 !important;
    font-size: 1.5rem !important;
}

/* ============================================================================
   Buttons - Modern & Interactive
   ============================================================================ */
button.primary,
button[variant="primary"],
.gr-button-primary {
    background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    box-shadow: var(--shadow-md) !important;
    transition: all var(--duration-normal) var(--ease-smooth) !important;
    cursor: pointer !important;
    position: relative;
    overflow: hidden;
}

button.primary:hover,
button[variant="primary"]:hover,
.gr-button-primary:hover {
    background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%) !important;
    box-shadow: var(--shadow-primary) !important;
    transform: translateY(-2px) scale(1.02) !important;
}

button.primary:active,
button[variant="primary"]:active,
.gr-button-primary:active {
    transform: translateY(0) scale(0.98) !important;
    box-shadow: var(--shadow-sm) !important;
}

button.secondary,
button[variant="secondary"],
.gr-button-secondary {
    background: white !important;
    color: var(--neutral-800) !important;
    border: 2px solid var(--neutral-300) !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
    transition: all var(--duration-normal) var(--ease-smooth) !important;
}

button.secondary:hover,
button[variant="secondary"]:hover,
.gr-button-secondary:hover {
    background: var(--neutral-100) !important;
    border-color: var(--neutral-500) !important;
    transform: translateY(-1px) !important;
}

/* Success button */
.gr-button-success {
    background: linear-gradient(135deg, var(--success-500) 0%, var(--success-600) 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: var(--shadow-success) !important;
}

/* ============================================================================
   Cards & Containers
   ============================================================================ */
.gr-box,
.gr-panel,
.gr-form,
.gr-group {
    background: white !important;
    border-radius: 16px !important;
    border: 1px solid var(--neutral-300) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 24px !important;
    transition: all var(--duration-normal) var(--ease-smooth) !important;
    animation: scaleIn 0.4s var(--ease-smooth);
}

.gr-box:hover,
.gr-panel:hover {
    box-shadow: var(--shadow-lg) !important;
    transform: translateY(-2px) !important;
}

/* ============================================================================
   Input Fields - Modern & Clean
   ============================================================================ */
input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
textarea,
.gr-input,
.gr-textbox {
    border: 2px solid var(--neutral-300) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    transition: all var(--duration-fast) var(--ease-smooth) !important;
    background: white !important;
}

input:focus,
textarea:focus,
.gr-input:focus,
.gr-textbox:focus {
    border-color: var(--primary-500) !important;
    box-shadow: 0 0 0 4px rgba(97, 97, 255, 0.1) !important;
    outline: none !important;
    transform: scale(1.01) !important;
}

input::placeholder,
textarea::placeholder {
    color: var(--neutral-500) !important;
    font-weight: 400 !important;
}

/* ============================================================================
   Tabs - Modern Tab Design
   ============================================================================ */
.tab-nav {
    background: white !important;
    border-radius: 16px !important;
    padding: 8px !important;
    box-shadow: var(--shadow-sm) !important;
    gap: 8px !important;
}

.tab-nav button {
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all var(--duration-normal) var(--ease-smooth) !important;
    border: none !important;
    background: transparent !important;
    color: var(--neutral-700) !important;
}

.tab-nav button.selected,
.tab-nav button:hover {
    background: var(--primary-500) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
}

.tab-nav button:not(.selected):hover {
    background: var(--neutral-100) !important;
    color: var(--neutral-900) !important;
}

/* ============================================================================
   Markdown Content - Beautiful Typography
   ============================================================================ */
.markdown-body,
.gr-markdown {
    color: var(--neutral-800) !important;
    line-height: 1.7 !important;
    animation: fadeIn 0.4s var(--ease-smooth);
}

.markdown-body h1,
.gr-markdown h1 {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
    background: linear-gradient(135deg, var(--primary-500), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.markdown-body h2,
.gr-markdown h2 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    margin-top: 1.5rem !important;
    color: var(--neutral-900) !important;
    border-bottom: 3px solid var(--primary-500) !important;
    padding-bottom: 0.5rem !important;
}

.markdown-body h3,
.gr-markdown h3 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--neutral-800) !important;
}

.markdown-body p,
.gr-markdown p {
    margin-bottom: 1rem !important;
    font-size: 16px !important;
}

.markdown-body code,
.gr-markdown code {
    background: var(--neutral-100) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    color: var(--primary-600) !important;
}

.markdown-body pre,
.gr-markdown pre {
    background: var(--neutral-900) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    overflow-x: auto !important;
}

/* ============================================================================
   Success & Error States
   ============================================================================ */
.success-message {
    background: linear-gradient(135deg, #00CA72 0%, #00B365 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: var(--shadow-success);
    animation: slideUp 0.4s var(--ease-bounce);
}

.error-message {
    background: linear-gradient(135deg, #E44258 0%, #CC3850 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: 0 10px 30px -5px rgba(228, 66, 88, 0.3);
    animation: shake 0.5s var(--ease-smooth);
}

.warning-message {
    background: linear-gradient(135deg, #FDAB3D 0%, #F59E28 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    animation: pulse 2s infinite;
}

/* ============================================================================
   Loading States & Skeleton Screens
   ============================================================================ */
.loading-skeleton {
    background: linear-gradient(
        90deg,
        var(--neutral-100) 0%,
        var(--neutral-200) 50%,
        var(--neutral-100) 100%
    );
    background-size: 200% 100%;
    animation: shimmer 2s infinite linear;
    border-radius: 8px;
    height: 20px;
}

.spinner {
    border: 3px solid var(--neutral-300);
    border-top: 3px solid var(--primary-500);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ============================================================================
   Progress Indicators
   ============================================================================ */
.progress-bar {
    background: var(--neutral-200);
    border-radius: 9999px;
    height: 12px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    background: linear-gradient(90deg, var(--primary-500), var(--accent-purple));
    height: 100%;
    border-radius: 9999px;
    transition: width var(--duration-slow) var(--ease-smooth);
    box-shadow: 0 0 10px rgba(97, 97, 255, 0.5);
}

/* ============================================================================
   Badges & Tags
   ============================================================================ */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-primary {
    background: var(--primary-500);
    color: white;
}

.badge-success {
    background: var(--success-500);
    color: white;
}

.badge-warning {
    background: var(--warning-500);
    color: white;
}

.badge-free {
    background: var(--neutral-300);
    color: var(--neutral-800);
}

.badge-pro {
    background: linear-gradient(135deg, var(--primary-500), var(--accent-purple));
    color: white;
    box-shadow: var(--shadow-md);
}

.badge-enterprise {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: var(--neutral-900);
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

/* ============================================================================
   Pricing Cards
   ============================================================================ */
.pricing-card {
    background: white;
    border-radius: 24px;
    padding: 32px;
    border: 2px solid var(--neutral-300);
    transition: all var(--duration-normal) var(--ease-smooth);
    position: relative;
    overflow: hidden;
}

.pricing-card:hover {
    border-color: var(--primary-500);
    box-shadow: var(--shadow-xl);
    transform: translateY(-8px) scale(1.02);
}

.pricing-card.featured {
    border-color: var(--primary-500);
    border-width: 3px;
    box-shadow: var(--shadow-primary);
}

.pricing-card.featured::before {
    content: "POPULAR";
    position: absolute;
    top: 20px;
    right: -30px;
    background: var(--success-500);
    color: white;
    padding: 4px 40px;
    font-size: 12px;
    font-weight: 700;
    transform: rotate(45deg);
    box-shadow: var(--shadow-md);
}

/* ============================================================================
   Responsive Design
   ============================================================================ */
@media (max-width: 768px) {
    .gradio-container h1 {
        font-size: 2rem !important;
    }

    button.primary,
    button.secondary {
        padding: 12px 20px !important;
        font-size: 14px !important;
    }

    .gr-box,
    .gr-panel {
        padding: 16px !important;
    }
}

/* ============================================================================
   Accessibility - Reduced Motion
   ============================================================================ */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ============================================================================
   Focus Styles - Accessibility
   ============================================================================ */
*:focus-visible {
    outline: 3px solid var(--primary-500) !important;
    outline-offset: 2px !important;
}

/* ============================================================================
   Utility Classes
   ============================================================================ */
.mt-4 { margin-top: 1rem !important; }
.mt-6 { margin-top: 1.5rem !important; }
.mt-8 { margin-top: 2rem !important; }

.mb-4 { margin-bottom: 1rem !important; }
.mb-6 { margin-bottom: 1.5rem !important; }
.mb-8 { margin-bottom: 2rem !important; }

.text-center { text-align: center !important; }
.text-bold { font-weight: 700 !important; }

.hidden { display: none !important; }
.visible { display: block !important; }

/* ============================================================================
   Enhanced Pricing Cards
   ============================================================================ */
.pricing-card {
    background: white;
    border-radius: 24px;
    padding: 32px;
    border: 2px solid var(--neutral-300);
    transition: all var(--duration-normal) var(--ease-smooth);
    position: relative;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.pricing-card:hover {
    border-color: var(--primary-500);
    box-shadow: var(--shadow-xl);
    transform: translateY(-8px) scale(1.02);
}

.pricing-card.featured {
    border-color: var(--primary-500);
    border-width: 3px;
    box-shadow: var(--shadow-primary);
    background: linear-gradient(180deg, white 0%, rgba(97, 97, 255, 0.02) 100%);
}

.pricing-card.featured::before {
    content: "POPULAR";
    position: absolute;
    top: 20px;
    right: -30px;
    background: var(--success-500);
    color: white;
    padding: 4px 40px;
    font-size: 11px;
    font-weight: 700;
    transform: rotate(45deg);
    box-shadow: var(--shadow-md);
    letter-spacing: 0.5px;
}

.pricing-tier-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--neutral-900);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.pricing-amount {
    display: flex;
    align-items: baseline;
    margin-bottom: 2rem;
}

.pricing-amount .currency {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--neutral-700);
    margin-right: 0.25rem;
}

.pricing-amount .price {
    font-size: 3.5rem;
    font-weight: 800;
    color: var(--primary-500);
    line-height: 1;
}

.pricing-amount .period {
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--neutral-600);
    margin-left: 0.5rem;
}

.pricing-features {
    list-style: none;
    padding: 0;
    margin: 0 0 2rem 0;
    flex-grow: 1;
}

.pricing-features li {
    padding: 0.75rem 0;
    color: var(--neutral-800);
    font-size: 0.95rem;
    border-bottom: 1px solid var(--neutral-200);
    display: flex;
    align-items: center;
}

.pricing-features li:last-child {
    border-bottom: none;
}

.pricing-features li::before {
    content: "✓";
    color: var(--success-500);
    font-weight: 700;
    font-size: 1.2rem;
    margin-right: 0.75rem;
}

.pricing-cta {
    margin-top: auto;
    text-align: center;
}

/* ============================================================================
   Usage Tracker Component
   ============================================================================ */
.usage-tracker {
    padding: 1rem;
    background: var(--neutral-50);
    border-radius: 12px;
    border: 1px solid var(--neutral-200);
}

.usage-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--neutral-800);
}

.usage-stats {
    color: var(--neutral-600);
    font-weight: 500;
}

.progress-bar {
    background: var(--neutral-200);
    border-radius: 9999px;
    height: 10px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    background: linear-gradient(90deg, var(--primary-500), var(--accent-purple));
    height: 100%;
    border-radius: 9999px;
    transition: width var(--duration-slow) var(--ease-smooth);
    box-shadow: 0 0 10px rgba(97, 97, 255, 0.5);
    position: relative;
    overflow: hidden;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.3) 50%,
        transparent 100%
    );
    animation: shimmer 2s infinite;
}

/* ============================================================================
   Welcome Dashboard
   ============================================================================ */
.welcome-dashboard {
    background: white;
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--neutral-200);
}

/* ============================================================================
   Enhanced Toast Notifications (Future)
   ============================================================================ */
.toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 9999;
    pointer-events: none;
}

.toast {
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: var(--shadow-xl);
    margin-bottom: 0.75rem;
    pointer-events: auto;
    animation: slideInRight 0.3s var(--ease-smooth);
    border-left: 4px solid var(--primary-500);
}

@keyframes slideInRight {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast.success {
    border-left-color: var(--success-500);
}

.toast.error {
    border-left-color: var(--error-500);
}

.toast.warning {
    border-left-color: var(--warning-500);
}
"""
