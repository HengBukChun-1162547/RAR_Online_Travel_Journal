from app.user import user
from app.auth.view import requires_permission, has_permission
from flask import redirect, render_template, request, session, url_for, flash, jsonify
from app.model import *

# Gift subscription page - Allows admin to select a user to gift
@user.route('/gift-subscription/<int:user_id>', methods=['GET'])
@requires_permission('view_others_subscriptions')
def gift_subscription(user_id):
    """
    Display the gift subscription page
    - Only admins can access
    - Can only gift to users with Traveller role
    """
    # Check if current user has permission to gift subscriptions
    if not has_permission('create_gift'):
        flash("Only administrators can gift subscriptions", "danger")
        return redirect(url_for('auth.landing'))
    
    # Get user information
    user_data = UserRepository.get_user(user_id=user_id)
    
    # Check if user exists and is a Traveller
    if not user_data:
        flash("User not found", "danger")
        return redirect(url_for('user.users'))
    
    if not has_permission('receive_gift', user_id=user_id):
        flash("Subscriptions can only be gifted to users with Traveller, Trial, or Premium roles", "danger")
        return redirect(url_for('user.users', user_id=user_id, page='profile'))
    
    # Get the user's current subscription status (if any)
    current_subscription = UserRepository.get_active_subscription(user_id)
    
    # Gift subscription plan options
    gift_plans = SubscriptionRepository.get_subscription_plan(subscription_type='Gifted')
    
    return render_template(
        'gift_subscription.html',
        user=user_data,
        current_subscription=current_subscription,
        gift_plans=gift_plans
    )

# Handle gift subscription confirmation
@user.route('/confirm-gift-subscription', methods=['POST'])
@requires_permission('view_others_subscriptions')
def confirm_gift_subscription():
    """
    Process the gift subscription confirmation
    - Validates all required form data
    - Creates a new subscription record
    - Redirects to user profile with success message
    """
    if not has_permission('create_gift'):
        flash("Only administrators can gift subscriptions", "danger")
        return redirect(url_for('user.users'))
    
    # Get form data
    user_id = request.form.get('user_id')
    plan_id = request.form.get('plan_id')
    reason = request.form.get('reason')
    if reason == 'Other':
        reason = request.form.get('otherReason', '').strip()
    
    if not user_id or not plan_id or not reason:
        flash("All fields are required", "danger")
        return redirect(url_for('user.gift_subscription', user_id=user_id))
    
    # Get user information and validate
    user_data = UserRepository.get_user(user_id=user_id)
    if not user_data or not has_permission('receive_gift', user_id=user_id):
        flash("User does not exist or does not have a valid role for gifting", "danger")
        return redirect(url_for('user.users'))
    
    # Get current subscription status (if any)
    current_subscription = UserRepository.get_active_subscription(user_id)
    subscription_status = "Free"
    remaining_days = 0
    expiry_date = None
    
    if current_subscription:
        subscription_status = current_subscription['subscription_type']
        # Calculate remaining days
        import datetime
        expiry_date = datetime.datetime.strptime(str(current_subscription['expiry_date']), '%Y-%m-%d %H:%M:%S')
        remaining_days = (expiry_date - datetime.datetime.now()).days
    
    # Get subscription plan details
    plan_durations = {5: 1, 6: 3, 7: 12}  # Plan IDs and duration mapping
    duration_months = plan_durations.get(int(plan_id), 0)
    
    if duration_months <= 0:
        flash("Invalid subscription plan", "danger")
        return redirect(url_for('user.gift_subscription', user_id=user_id))
    
    # Create the new subscription
    result = UserRepository.create_gifted_subscription(
        user_id=user_id,
        admin_id=session['user_id'],
        plan_id=plan_id,
        duration_months=duration_months,
        reason=reason,
        current_status=subscription_status,
        remaining_days=remaining_days,
        expiry_date=expiry_date
    )
    
    if result:
        role = "premium"
        result = UserRepository.update_user(user_id=user_id, role=role)
        message = f"You've Received a {duration_months} Month Subscription Gift! - Reason: {reason}"
        result = NotificationRepository.create_system_notification(user_id, message, 'Gift')
        flash(f"Successfully gifted {duration_months} month(s) subscription to user", "success")
        return redirect(url_for('user.users', user_id=user_id, page='profile'))
    else:
        flash("Failed to gift subscription, please try again later", "danger")
        return redirect(url_for('user.gift_subscription', user_id=user_id))

