"""
VibeDoc SaaS Application
Full-featured SaaS with authentication, subscriptions, and project management
"""

import gradio as gr
import os
import logging
import secrets
from datetime import datetime
from typing import Optional, Tuple
from functools import partial

# Initialize database first
from database import init_database, get_db_session, UserService, SubscriptionService, ProjectService, UsageTrackingService
from auth import AuthService, session_manager
from models import SubscriptionTier, PRICING_TIERS

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

logger.info("🚀 VibeDoc SaaS - AI Product Manager & Architect")
logger.info("📦 Version: 3.0.0 | SaaS Edition")

# Import plan generation from original app
# We'll need to modify the original app.py to export the generation function
# For now, let's create a simplified version

def generate_plan_simple(user_idea: str, reference_url: str = "") -> Tuple[str, str]:
    """
    Simplified plan generation (placeholder - will integrate with existing app.py)
    """
    import requests

    if not user_idea or not user_idea.strip():
        return "", "❌ Please enter your product idea!"

    try:
        # This is a simplified version - integrate with actual generation logic from app.py
        plan = f"""
# Development Plan: {user_idea}

## Overview
This is your AI-generated development plan.

## Technical Architecture
[Architecture details would be generated here]

## Implementation Roadmap
[Roadmap details would be generated here]

## AI Coding Prompts
[AI coding prompts would be generated here]

---
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return plan, "✅ Plan generated successfully!"
    except Exception as e:
        logger.error(f"Plan generation error: {e}")
        return "", f"❌ Generation failed: {str(e)}"

# =============================================================================
# Authentication Functions
# =============================================================================

def signup_user(email: str, username: str, password: str, password_confirm: str, full_name: str = ""):
    """Handle user signup"""
    with get_db_session() as session:
        auth_service = AuthService(session)

        # Validate passwords match
        if password != password_confirm:
            return None, "❌ Passwords do not match!", gr.update(visible=True)

        # Register user
        success, message, user = auth_service.register_user(email, username, password, full_name)

        if success:
            return None, f"✅ {message} Please login to continue.", gr.update(visible=True)
        else:
            return None, f"❌ {message}", gr.update(visible=True)

def login_user(email_or_username: str, password: str, request: gr.Request):
    """Handle user login"""
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

            welcome_msg = f"""
# Welcome back, {user.username}! 🎉

**Subscription:** {subscription.tier.value.upper()} tier
**Monthly Limits:**
- Plans: {subscription.plans_generated}/{subscription.plan_generation_limit if subscription.plan_generation_limit > 0 else '∞'}
- Projects: {len(user.projects)}/{subscription.project_limit if subscription.project_limit > 0 else '∞'}
- Exports: {subscription.exports_made}/{subscription.export_limit if subscription.export_limit > 0 else '∞'}
"""

            return (
                session_id,
                welcome_msg,
                gr.update(visible=False),  # Hide auth tabs
                gr.update(visible=True),   # Show main app
                gr.update(visible=True),   # Show user info
                gr.update(value=f"👤 {user.username}")
            )
        else:
            return None, f"❌ {message}", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value="")

def logout_user(session_id: str):
    """Handle user logout"""
    if session_id:
        session_manager.delete_session(session_id)

    return (
        None,  # Clear session_id
        "",    # Clear welcome message
        gr.update(visible=True),   # Show auth tabs
        gr.update(visible=False),  # Hide main app
        gr.update(visible=False),  # Hide user info
        gr.update(value="")
    )

# =============================================================================
# Plan Generation with Usage Tracking
# =============================================================================

def generate_development_plan_saas(session_id: str, user_idea: str, reference_url: str = ""):
    """Generate development plan with subscription limits"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return "", "❌ Please login to generate plans"

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    # Check usage limits
    can_proceed, limit_msg = SubscriptionService.check_usage_limit(user_id, 'plan')
    if not can_proceed:
        return "", f"❌ {limit_msg}"

    # Generate plan
    start_time = datetime.now()
    plan, message = generate_plan_simple(user_idea, reference_url)
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    if plan:
        # Increment usage
        SubscriptionService.increment_usage(user_id, 'plan')

        # Log action
        UsageTrackingService.log_action(
            user_id=user_id,
            action_type='plan_generated',
            success=True,
            processing_time=processing_time,
            details={'idea': user_idea[:100]}
        )

        return plan, f"✅ {message}"
    else:
        UsageTrackingService.log_action(
            user_id=user_id,
            action_type='plan_generated',
            success=False,
            error_message=message
        )
        return "", message

# =============================================================================
# Project Management
# =============================================================================

def save_project(session_id: str, title: str, description: str, plan: str):
    """Save generated plan as project"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return "❌ Please login to save projects"

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    # Check limits
    can_proceed, limit_msg = SubscriptionService.check_usage_limit(user_id, 'project')
    if not can_proceed:
        return f"❌ {limit_msg}"

    if not title or not plan:
        return "❌ Please provide a title and generate a plan first"

    # Save project
    project = ProjectService.create_project(
        user_id=user_id,
        title=title,
        description=description,
        generated_plan=plan
    )

    if project:
        return f"✅ Project '{title}' saved successfully! (ID: {project.id})"
    else:
        return "❌ Failed to save project"

def load_user_projects(session_id: str):
    """Load user's projects"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return []

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    projects = ProjectService.get_user_projects(user_id)

    # Format for display
    project_list = []
    for project in projects:
        project_list.append({
            'id': project.id,
            'title': project.title,
            'created': project.created_at.strftime('%Y-%m-%d %H:%M'),
            'favorite': '⭐' if project.is_favorite else ''
        })

    return project_list

def load_project(session_id: str, project_id: int):
    """Load specific project"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return "", "", "❌ Please login"

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    project = ProjectService.get_project(project_id, user_id)

    if project:
        return project.title, project.description, project.generated_plan, f"✅ Loaded: {project.title}"
    else:
        return "", "", "", "❌ Project not found"

# =============================================================================
# Subscription Management
# =============================================================================

def get_subscription_info(session_id: str):
    """Get user's subscription information"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return "Please login to view subscription details"

    session = session_manager.get_session(session_id)
    user_id = session['user_id']

    subscription = SubscriptionService.get_subscription(user_id)

    if not subscription:
        return "No subscription found"

    tier_name = subscription.tier.value.upper()
    tier_info = PRICING_TIERS.get(subscription.tier, {})

    info = f"""
# Your Subscription: {tier_name}

## Current Usage (This Month)
- **Plans Generated:** {subscription.plans_generated} / {subscription.plan_generation_limit if subscription.plan_generation_limit > 0 else '∞'}
- **Projects Created:** {subscription.projects_created} / {subscription.project_limit if subscription.project_limit > 0 else '∞'}
- **Exports Made:** {subscription.exports_made} / {subscription.export_limit if subscription.export_limit > 0 else '∞'}

## Features Included
{chr(10).join(f'- {feature}' for feature in tier_info.get('features', []))}

## Billing Period
- **Current Period:** {subscription.current_period_start.strftime('%Y-%m-%d') if subscription.current_period_start else 'N/A'} to {subscription.current_period_end.strftime('%Y-%m-%d') if subscription.current_period_end else 'N/A'}
"""

    return info

def show_pricing():
    """Display pricing tiers"""
    pricing_md = """
# VibeDoc Pricing Plans

Choose the plan that fits your needs:

"""

    for tier, details in PRICING_TIERS.items():
        pricing_md += f"""
## {details['name']} - ${details['price']}/month

{chr(10).join(f'- {feature}' for feature in details['features'])}

---
"""

    return pricing_md

# =============================================================================
# Admin Dashboard
# =============================================================================

def admin_dashboard(session_id: str):
    """Admin dashboard with system stats"""
    if not session_id or not session_manager.is_authenticated(session_id):
        return "❌ Please login"

    session = session_manager.get_session(session_id)
    if not session.get('is_admin'):
        return "❌ Admin access required"

    stats = UsageTrackingService.get_system_stats()

    dashboard_md = f"""
# Admin Dashboard

## System Statistics

- **Total Users:** {stats['total_users']}
- **Active Users:** {stats['active_users']}
- **Total Projects:** {stats['total_projects']}

## Subscription Breakdown

"""

    for tier, count in stats['subscription_breakdown'].items():
        dashboard_md += f"- **{tier.upper()}:** {count} users\n"

    return dashboard_md

# =============================================================================
# Gradio Interface
# =============================================================================

def create_saas_interface():
    """Create the complete SaaS interface"""

    with gr.Blocks(title="VibeDoc - AI Product Manager & Architect", theme=gr.themes.Soft()) as app:

        # Session state
        session_id_state = gr.State(None)

        # Header
        gr.Markdown("""
        # 🚀 VibeDoc: Your AI Product Manager & Architect

        **Transform Ideas into Complete Development Plans in Minutes**
        """)

        # Authentication Section (shown by default)
        with gr.Group(visible=True) as auth_section:
            with gr.Tabs() as auth_tabs:
                # Login Tab
                with gr.Tab("Login"):
                    login_email = gr.Textbox(label="Email or Username", placeholder="your@email.com")
                    login_password = gr.Textbox(label="Password", type="password")
                    login_btn = gr.Button("Login", variant="primary")
                    login_msg = gr.Markdown("")

                # Signup Tab
                with gr.Tab("Sign Up"):
                    signup_email = gr.Textbox(label="Email", placeholder="your@email.com")
                    signup_username = gr.Textbox(label="Username", placeholder="username")
                    signup_full_name = gr.Textbox(label="Full Name (Optional)", placeholder="John Doe")
                    signup_password = gr.Textbox(label="Password", type="password")
                    signup_password_confirm = gr.Textbox(label="Confirm Password", type="password")
                    signup_btn = gr.Button("Create Account", variant="primary")
                    signup_msg = gr.Markdown("")

        # User Info Bar (hidden by default)
        with gr.Row(visible=False) as user_info_bar:
            user_display = gr.Markdown("👤 User")
            logout_btn = gr.Button("Logout", size="sm")

        # Welcome Message
        welcome_msg = gr.Markdown("", visible=False)

        # Main Application (hidden until logged in)
        with gr.Group(visible=False) as main_app:
            with gr.Tabs() as main_tabs:

                # Generate Plan Tab
                with gr.Tab("📋 Generate Plan"):
                    gr.Markdown("### Enter Your Product Idea")

                    user_idea = gr.Textbox(
                        label="Product Idea",
                        placeholder="Describe your app idea...",
                        lines=5
                    )
                    reference_url = gr.Textbox(
                        label="Reference URL (Optional)",
                        placeholder="https://..."
                    )

                    generate_btn = gr.Button("Generate Development Plan", variant="primary", size="lg")

                    gen_message = gr.Markdown("")
                    generated_plan = gr.Textbox(label="Generated Plan", lines=20)

                    # Save plan
                    with gr.Row():
                        project_title = gr.Textbox(label="Project Title", placeholder="My Awesome App")
                        save_btn = gr.Button("💾 Save as Project", variant="secondary")

                    save_message = gr.Markdown("")

                # My Projects Tab
                with gr.Tab("📁 My Projects"):
                    gr.Markdown("### Your Saved Projects")

                    refresh_projects_btn = gr.Button("🔄 Refresh Projects")
                    projects_display = gr.JSON(label="Projects")

                    with gr.Row():
                        load_project_id = gr.Number(label="Project ID", precision=0)
                        load_btn = gr.Button("Load Project")

                    load_message = gr.Markdown("")
                    loaded_title = gr.Textbox(label="Title", interactive=False)
                    loaded_description = gr.Textbox(label="Description", interactive=False)
                    loaded_plan = gr.Textbox(label="Plan", lines=20, interactive=False)

                # Subscription Tab
                with gr.Tab("💳 Subscription"):
                    subscription_info = gr.Markdown("")

                    gr.Markdown("---")
                    pricing_info = gr.Markdown(show_pricing())

                    gr.Markdown("""
                    ### Upgrade Your Plan

                    Contact support to upgrade: support@vibedoc.com
                    """)

                # Admin Tab (only for admins)
                with gr.Tab("⚙️ Admin", visible=False) as admin_tab:
                    admin_content = gr.Markdown("")
                    refresh_admin_btn = gr.Button("Refresh Stats")

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

        # Load Projects
        refresh_projects_btn.click(
            fn=load_user_projects,
            inputs=[session_id_state],
            outputs=[projects_display]
        )

        load_btn.click(
            fn=load_project,
            inputs=[session_id_state, load_project_id],
            outputs=[loaded_title, loaded_description, loaded_plan, load_message]
        )

        # Subscription Info
        main_tabs.select(
            fn=get_subscription_info,
            inputs=[session_id_state],
            outputs=[subscription_info]
        )

        # Admin Dashboard
        refresh_admin_btn.click(
            fn=admin_dashboard,
            inputs=[session_id_state],
            outputs=[admin_content]
        )

    return app

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("🎨 Creating Gradio interface...")

    app = create_saas_interface()

    logger.info(f"🌐 Launching application on port {config.port}...")

    app.launch(
        server_name="0.0.0.0",
        server_port=config.port,
        share=False,
        show_error=True
    )
