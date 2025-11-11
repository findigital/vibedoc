"""
VibeDoc SaaS Application V2 - Modern Design Edition
Award-winning UI/UX with monday.com-inspired design
"""

import gradio as gr
import os
import logging
import secrets
from datetime import datetime
from typing import Optional, Tuple

# Initialize database first
from database import init_database, get_db_session, UserService, SubscriptionService, ProjectService, UsageTrackingService
from auth import AuthService, session_manager
from models import SubscriptionTier, PRICING_TIERS

# Import theme
from theme import vibedoc_theme, VIBEDOC_CSS

# Import existing modules
from config import config
from export_manager import export_manager
from prompt_optimizer import prompt_optimizer
from explanation_manager import explanation_manager

# Configure logging
logging.basicConfig(level=getattr(logging, config.log_level), format=config.log_format)
logger = logging.getLogger(__name__)

# Initialize database on startup
init_database()

logger.info("🚀 VibeDoc SaaS V2 - Modern Design Edition")
logger.info("📦 Version: 3.0.0 | Award-Winning UI/UX")

# =============================================================================
# Helper Functions for UI Components
# =============================================================================

def create_pricing_card_html(tier: str) -> str:
    """Create beautiful pricing card HTML"""
    tier_info = PRICING_TIERS.get(getattr(SubscriptionTier, tier.upper()))
    if not tier_info:
        return ""

    featured_class = "featured" if tier == "PRO" else ""
    price = tier_info['price']
    features = tier_info['features']

    features_html = "\n".join([f'<li>✓ {feature}</li>' for feature in features])

    return f"""
<div class="pricing-card {featured_class}">
    <div class="pricing-tier-name">{tier_info['name']}</div>
    <div class="pricing-amount">
        <span class="currency">$</span>
        <span class="price">{int(price)}</span>
        <span class="period">/month</span>
    </div>
    <ul class="pricing-features">
        {features_html}
    </ul>
    <div class="pricing-cta">
        {'<div class="badge badge-pro">MOST POPULAR</div>' if tier == "PRO" else ''}
    </div>
</div>
"""

def create_usage_progress_html(current: int, limit: int, label: str, color: str = "primary") -> str:
    """Create usage progress bar HTML"""
    if limit <= 0:  # Unlimited
        percentage = 0
        display_limit = "∞"
    else:
        percentage = min((current / limit) * 100, 100)
        display_limit = str(limit)

    # Color logic
    if percentage >= 90:
        bar_color = "error-500"
    elif percentage >= 70:
        bar_color = "warning-500"
    else:
        bar_color = "primary-500"

    return f"""
<div class="usage-tracker">
    <div class="usage-label">
        <span>{label}</span>
        <span class="usage-stats">{current} / {display_limit}</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="width: {percentage}%; background: var(--{bar_color});"></div>
    </div>
</div>
"""

# =============================================================================
# Enhanced UI Functions
# =============================================================================

def signup_user(email: str, username: str, password: str, password_confirm: str, full_name: str = ""):
    """Handle user signup with enhanced feedback"""
    with get_db_session() as session:
        auth_service = AuthService(session)

        # Validate passwords match
        if password != password_confirm:
            return None, '<div class="error-message">🔒 Passwords do not match!</div>', gr.update(visible=True)

        # Register user
        success, message, user = auth_service.register_user(email, username, password, full_name)

        if success:
            success_msg = f'''
<div class="success-message">
    <h3>🎉 Welcome to VibeDoc!</h3>
    <p>{message}</p>
    <p><strong>Next step:</strong> Login to start creating amazing development plans!</p>
</div>
'''
            return None, success_msg, gr.update(visible=True)
        else:
            error_msg = f'<div class="error-message">❌ {message}</div>'
            return None, error_msg, gr.update(visible=True)

def login_user(email_or_username: str, password: str, request: gr.Request):
    """Handle user login with beautiful welcome screen"""
    with get_db_session() as session:
        auth_service = AuthService(session)

        success, message, user = auth_service.authenticate_user(email_or_username, password)

        if success:
            # Create session
            session_id = secrets.token_urlsafe(32)
            access_token = auth_service.create_access_token(user)
            session_manager.create_session(session_id, user, access_token)

            # Get subscription info
            subscription = SubscriptionService.get_subscription(user.id)

            # Create beautiful usage dashboard
            plans_progress = create_usage_progress_html(
                subscription.plans_generated,
                subscription.plan_generation_limit,
                "📋 Plans Generated"
            )

            projects_progress = create_usage_progress_html(
                subscription.projects_created,
                subscription.project_limit,
                "📁 Projects Created"
            )

            exports_progress = create_usage_progress_html(
                subscription.exports_made,
                subscription.export_limit,
                "💾 Exports Made"
            )

            tier_badge = f'<span class="badge badge-{subscription.tier.value}">{subscription.tier.value.upper()}</span>'

            welcome_msg = f"""
<div class="welcome-dashboard" style="animation: fadeIn 0.6s ease-out;">
    <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">Welcome back, {user.username}! 👋</h1>
    <p style="font-size: 1.1rem; color: var(--neutral-700); margin-bottom: 2rem;">
        Your subscription: {tier_badge}
    </p>

    <div style="display: grid; gap: 1rem; margin-top: 2rem;">
        {plans_progress}
        {projects_progress}
        {exports_progress}
    </div>

    <div style="margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #F6F7FB, #E6E9EF); border-radius: 12px;">
        <p style="margin: 0; font-size: 0.95rem; color: var(--neutral-800);">
            💡 <strong>Pro Tip:</strong> Start by generating a development plan for your next big idea!
        </p>
    </div>
</div>
"""

            return (
                session_id,
                welcome_msg,
                gr.update(visible=False),  # Hide auth tabs
                gr.update(visible=True),   # Show main app
                gr.update(visible=True),   # Show user info
                gr.update(value=f"<div style='padding: 8px 16px; background: white; border-radius: 12px; box-shadow: var(--shadow-sm);'>👤 <strong>{user.username}</strong> | {tier_badge}</div>")
            )
        else:
            error_msg = f'<div class="error-message">❌ {message}</div>'
            return None, error_msg, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value="")

def logout_user(session_id: str):
    """Handle user logout"""
    if session_id:
        session_manager.delete_session(session_id)

    return (
        None,
        "",
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value="")
    )

def generate_development_plan_saas(session_id: str, user_idea: str, reference_url: str = ""):
    """Generate development plan with beautiful loading and feedback"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return "", '<div class="error-message">🔒 Please login to generate plans</div>'

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    # Check usage limits
    can_proceed, limit_msg = SubscriptionService.check_usage_limit(user_id, 'plan')
    if not can_proceed:
        return "", f'<div class="warning-message">⚠️ {limit_msg}</div>'

    # Show loading state
    loading_msg = '''
<div style="text-align: center; padding: 2rem;">
    <div class="spinner" style="margin: 0 auto 1rem;"></div>
    <p style="font-size: 1.1rem; color: var(--neutral-700);">
        ✨ Creating your development plan...
    </p>
    <p style="font-size: 0.9rem; color: var(--neutral-600);">
        This usually takes 60-180 seconds
    </p>
</div>
'''

    try:
        # Simplified plan generation (integrate with actual logic)
        plan = f"""
# 🚀 Development Plan: {user_idea}

## 📋 Product Overview

**Target Users**: [AI will generate this]

**Core Features**:
- Feature 1
- Feature 2
- Feature 3

## 🏗️ Technical Architecture

```mermaid
graph TD
    A[Frontend] --> B[API Gateway]
    B --> C[Backend Services]
    C --> D[Database]
```

## 💻 Technology Stack

- **Frontend**: React, Next.js
- **Backend**: Node.js, Express
- **Database**: PostgreSQL
- **Cloud**: AWS/GCP

## 📅 Development Roadmap

### Phase 1: MVP (Weeks 1-4)
- Core feature development
- Basic UI/UX

### Phase 2: Enhancement (Weeks 5-8)
- Advanced features
- Performance optimization

### Phase 3: Launch (Weeks 9-12)
- Testing
- Deployment
- Marketing

## 🤖 AI Coding Prompts

### Prompt 1: Backend API
```
Create a RESTful API for {user_idea}...
```

---
*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Increment usage
        SubscriptionService.increment_usage(user_id, 'plan')

        # Log action
        UsageTrackingService.log_action(
            user_id=user_id,
            action_type='plan_generated',
            success=True,
            details={'idea': user_idea[:100]}
        )

        success_msg = '''
<div class="success-message" style="animation: success-bounce 0.5s ease-out;">
    ✅ Your development plan is ready! Scroll down to view it.
</div>
'''

        return plan, success_msg

    except Exception as e:
        logger.error(f"Plan generation error: {e}")
        error_msg = f'<div class="error-message">❌ Generation failed: {str(e)}</div>'
        return "", error_msg

def save_project(session_id: str, title: str, description: str, plan: str):
    """Save generated plan as project with enhanced feedback"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return '<div class="error-message">🔒 Please login to save projects</div>'

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    # Check limits
    can_proceed, limit_msg = SubscriptionService.check_usage_limit(user_id, 'project')
    if not can_proceed:
        return f'<div class="warning-message">⚠️ {limit_msg}</div>'

    if not title or not plan:
        return '<div class="error-message">❌ Please provide a title and generate a plan first</div>'

    # Save project
    project = ProjectService.create_project(
        user_id=user_id,
        title=title,
        description=description,
        generated_plan=plan
    )

    if project:
        return f'''
<div class="success-message" style="animation: slideUp 0.4s ease-out;">
    💾 <strong>Project saved successfully!</strong>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        "{title}" (ID: {project.id}) is now in your projects library
    </p>
</div>
'''
    else:
        return '<div class="error-message">❌ Failed to save project</div>'

def get_subscription_info(session_id: str):
    """Get beautiful subscription dashboard"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return "Please login to view subscription details"

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    subscription = SubscriptionService.get_subscription(user_id)

    if not subscription:
        return "No subscription found"

    tier_info = PRICING_TIERS.get(subscription.tier, {})
    tier_badge = f'<span class="badge badge-{subscription.tier.value}" style="font-size: 1.2rem;">{subscription.tier.value.upper()}</span>'

    # Usage progress bars
    plans_progress = create_usage_progress_html(
        subscription.plans_generated,
        subscription.plan_generation_limit,
        "📋 Plans Generated This Month"
    )

    projects_progress = create_usage_progress_html(
        subscription.projects_created,
        subscription.project_limit,
        "📁 Projects Created"
    )

    exports_progress = create_usage_progress_html(
        subscription.exports_made,
        subscription.export_limit,
        "💾 Exports Made This Month"
    )

    features_html = "\n".join([f'<li style="padding: 0.5rem 0;">✓ {feature}</li>' for feature in tier_info.get('features', [])])

    return f"""
<div style="animation: fadeIn 0.5s ease-out;">
    <div style="background: white; padding: 2rem; border-radius: 16px; box-shadow: var(--shadow-lg); margin-bottom: 2rem;">
        <h2 style="margin-top: 0;">Your Subscription</h2>
        <div style="margin: 1.5rem 0;">
            {tier_badge}
        </div>

        <h3 style="margin-top: 2rem; color: var(--neutral-800);">Current Usage</h3>
        <div style="display: grid; gap: 1rem; margin-top: 1rem;">
            {plans_progress}
            {projects_progress}
            {exports_progress}
        </div>

        <h3 style="margin-top: 2rem; color: var(--neutral-800);">Features Included</h3>
        <ul style="list-style: none; padding: 0; margin-top: 1rem;">
            {features_html}
        </ul>

        <div style="margin-top: 2rem; padding: 1rem; background: var(--neutral-100); border-radius: 12px;">
            <p style="margin: 0; font-size: 0.9rem; color: var(--neutral-700);">
                <strong>Billing Period:</strong> {subscription.current_period_start.strftime('%b %d, %Y') if subscription.current_period_start else 'N/A'} — {subscription.current_period_end.strftime('%b %d, %Y') if subscription.current_period_end else 'N/A'}
            </p>
        </div>
    </div>
</div>
"""

def show_pricing_comparison():
    """Create beautiful pricing comparison"""
    free_card = create_pricing_card_html("FREE")
    pro_card = create_pricing_card_html("PRO")
    enterprise_card = create_pricing_card_html("ENTERPRISE")

    return f"""
<div style="animation: fadeIn 0.6s ease-out;">
    <h2 style="text-align: center; margin-bottom: 3rem; font-size: 2.5rem;">
        Choose Your Plan
    </h2>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 3rem;">
        {free_card}
        {pro_card}
        {enterprise_card}
    </div>

    <div style="background: linear-gradient(135deg, var(--primary-500), var(--accent-purple)); color: white; padding: 2rem; border-radius: 16px; text-align: center;">
        <h3 style="color: white; margin-top: 0;">Ready to upgrade?</h3>
        <p style="font-size: 1.1rem; opacity: 0.95;">
            Contact us at <strong>support@vibedoc.com</strong> to upgrade your plan
        </p>
        <p style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0;">
            🔐 Secure payment via Stripe | 💳 All major cards accepted | 🔄 Cancel anytime
        </p>
    </div>
</div>
"""

# =============================================================================
# Create Modern SaaS Interface
# =============================================================================

def create_modern_saas_interface():
    """Create award-winning SaaS interface with modern design"""

    with gr.Blocks(
        title="VibeDoc - AI Product Manager & Architect",
        theme=vibedoc_theme,
        css=VIBEDOC_CSS
    ) as app:

        # Session state
        session_id_state = gr.State(None)

        # Hero Header
        gr.HTML("""
<div style="text-align: center; padding: 3rem 1rem 2rem; animation: slideUp 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);">
    <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem; background: linear-gradient(135deg, #6161FF 0%, #A25DDC 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        ✨ VibeDoc
    </h1>
    <p style="font-size: 1.3rem; color: var(--neutral-700); font-weight: 500; max-width: 700px; margin: 0 auto;">
        Your AI Product Manager & Software Architect
    </p>
    <p style="font-size: 1rem; color: var(--neutral-600); max-width: 600px; margin: 1rem auto 0;">
        Transform ideas into complete development plans in 60-180 seconds
    </p>
</div>
""")

        # Authentication Section
        with gr.Group(visible=True) as auth_section:
            with gr.Tabs():
                # Login Tab
                with gr.Tab("🔐 Login"):
                    gr.HTML('<div style="padding: 1rem 0;"><p style="text-align: center; color: var(--neutral-700);">Welcome back! Login to access your projects</p></div>')

                    with gr.Column():
                        login_email = gr.Textbox(
                            label="Email or Username",
                            placeholder="your@email.com or username",
                            elem_classes=["vibedoc-input"]
                        )
                        login_password = gr.Textbox(
                            label="Password",
                            type="password",
                            placeholder="••••••••",
                            elem_classes=["vibedoc-input"]
                        )
                        login_btn = gr.Button(
                            "Login to Your Account",
                            variant="primary",
                            size="lg",
                            elem_classes=["vibedoc-primary-btn"]
                        )
                        login_msg = gr.HTML("")

                # Signup Tab
                with gr.Tab("✨ Sign Up"):
                    gr.HTML('<div style="padding: 1rem 0;"><p style="text-align: center; color: var(--neutral-700);">Create your free account and start building!</p></div>')

                    with gr.Column():
                        signup_email = gr.Textbox(label="Email", placeholder="your@email.com")
                        signup_username = gr.Textbox(label="Username", placeholder="username")
                        signup_full_name = gr.Textbox(label="Full Name (Optional)", placeholder="John Doe")

                        with gr.Row():
                            signup_password = gr.Textbox(label="Password", type="password", placeholder="Min. 8 characters")
                            signup_password_confirm = gr.Textbox(label="Confirm Password", type="password", placeholder="Repeat password")

                        signup_btn = gr.Button(
                            "Create Free Account",
                            variant="primary",
                            size="lg"
                        )
                        signup_msg = gr.HTML("")

        # User Info Bar
        with gr.Row(visible=False) as user_info_bar:
            user_display = gr.HTML("")
            with gr.Column(scale=0):
                logout_btn = gr.Button("Logout", size="sm", variant="secondary")

        # Welcome Message
        welcome_msg = gr.HTML("", visible=False)

        # Main Application
        with gr.Group(visible=False) as main_app:
            with gr.Tabs():
                # Generate Plan Tab
                with gr.Tab("🚀 Generate Plan"):
                    gr.HTML("""
<div style="padding: 1rem 0 2rem;">
    <h2 style="margin-top: 0;">Create Your Development Plan</h2>
    <p style="color: var(--neutral-700);">
        Describe your app idea and get a complete technical plan with architecture, tech stack, and AI coding prompts
    </p>
</div>
""")

                    user_idea = gr.Textbox(
                        label="💡 Your Product Idea",
                        placeholder="Example: Build a fitness tracking app with AI-powered workout recommendations, meal planning, and social challenges...",
                        lines=6,
                        elem_classes=["vibedoc-input"]
                    )

                    reference_url = gr.Textbox(
                        label="🔗 Reference URL (Optional)",
                        placeholder="https://example.com/inspiration",
                        elem_classes=["vibedoc-input"]
                    )

                    generate_btn = gr.Button(
                        "✨ Generate Development Plan",
                        variant="primary",
                        size="lg"
                    )

                    gen_message = gr.HTML("")

                    generated_plan = gr.Textbox(
                        label="📋 Generated Development Plan",
                        lines=25,
                        interactive=False
                    )

                    # Save Section
                    gr.HTML('<div style="margin-top: 2rem; padding-top: 2rem; border-top: 2px solid var(--neutral-300);"><h3>💾 Save Your Plan</h3></div>')

                    with gr.Row():
                        project_title = gr.Textbox(
                            label="Project Title",
                            placeholder="My Awesome App",
                            scale=3
                        )
                        save_btn = gr.Button(
                            "💾 Save as Project",
                            variant="secondary",
                            size="lg",
                            scale=1
                        )

                    save_message = gr.HTML("")

                # My Projects Tab
                with gr.Tab("📁 My Projects"):
                    gr.HTML("""
<div style="padding: 1rem 0 2rem;">
    <h2 style="margin-top: 0;">Your Project Library</h2>
    <p style="color: var(--neutral-700);">
        Access and manage all your saved development plans
    </p>
</div>
""")

                    refresh_projects_btn = gr.Button("🔄 Refresh Projects", variant="secondary")
                    projects_display = gr.JSON(label="Projects")

                    gr.HTML('<div style="margin: 2rem 0;"><h3>Load a Project</h3></div>')

                    with gr.Row():
                        load_project_id = gr.Number(label="Project ID", precision=0)
                        load_btn = gr.Button("📂 Load Project", variant="primary")

                    load_message = gr.HTML("")

                    with gr.Column(visible=False) as loaded_project_area:
                        loaded_title = gr.Textbox(label="Title", interactive=False)
                        loaded_description = gr.Textbox(label="Description", interactive=False)
                        loaded_plan = gr.Textbox(label="Plan", lines=20, interactive=False)

                # Subscription Tab
                with gr.Tab("💳 Subscription"):
                    subscription_info = gr.HTML("")
                    pricing_display = gr.HTML("")

        # =============================================================================
        # Event Handlers
        # =============================================================================

        # Signup
        signup_btn.click(
            fn=signup_user,
            inputs=[signup_email, signup_username, signup_password, signup_password_confirm, signup_full_name],
            outputs=[session_id_state, signup_msg, auth_section]
        )

        # Login
        login_btn.click(
            fn=login_user,
            inputs=[login_email, login_password],
            outputs=[session_id_state, welcome_msg, auth_section, main_app, user_info_bar, user_display]
        )

        # Show welcome message on successful login
        session_id_state.change(
            fn=lambda sid: gr.update(visible=bool(sid)),
            inputs=[session_id_state],
            outputs=[welcome_msg]
        )

        # Logout
        logout_btn.click(
            fn=logout_user,
            inputs=[session_id_state],
            outputs=[session_id_state, welcome_msg, auth_section, main_app, user_info_bar, user_display]
        )

        # Generate Plan
        generate_btn.click(
            fn=generate_development_plan_saas,
            inputs=[session_id_state, user_idea, reference_url],
            outputs=[generated_plan, gen_message]
        )

        # Save Project
        save_btn.click(
            fn=save_project,
            inputs=[session_id_state, project_title, user_idea, generated_plan],
            outputs=[save_message]
        )

        # Load subscription info when tab is selected
        main_app.load(
            fn=get_subscription_info,
            inputs=[session_id_state],
            outputs=[subscription_info]
        )

        # Load pricing when subscription tab loads
        main_app.load(
            fn=show_pricing_comparison,
            outputs=[pricing_display]
        )

    return app

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("🎨 Creating modern SaaS interface...")

    app = create_modern_saas_interface()

    logger.info(f"🌐 Launching application on port {config.port}...")

    app.launch(
        server_name="0.0.0.0",
        server_port=config.port,
        share=False,
        show_error=True
    )
