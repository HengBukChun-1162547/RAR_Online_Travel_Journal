from flask import Blueprint, render_template, flash, redirect, url_for, request, session, current_app
from datetime import datetime, timedelta
from app import Utils
from app.auth.view import requires_permission, has_permission
from app.model import *
from app.gamification.view import gamification_service

premium = Blueprint('premium', __name__)

def handle_subscription(request, user_id):
    """ Get the subscription details from the form """
    subscription_type = request.form.get('subscription_type')
    subscription_plan_id = request.form.get('plan_id')
    plan = SubscriptionRepository.get_subscription_plan(subscription_plan_id=subscription_plan_id)
    if not plan:
        flash("Invalid subscription plan selected.", 'error')
        return redirect(url_for('premium.subscribe_to_premium_features'))

    current_date = datetime.now()
    latest_subscription = SubscriptionRepository.get_newest_subscription(user_id=user_id, limit=1)
    if latest_subscription and latest_subscription['expiry_date'] > current_date:
        start_date = latest_subscription['expiry_date'] + timedelta(days=1)
    else:
        start_date = current_date

    duration_months = plan['duration_months']
    expiry_date = start_date + timedelta(days=30 * duration_months)
    return SubscriptionRepository.create_subscription(user_id=user_id, subscription_type=subscription_type, subscription_plan_id=subscription_plan_id, start_date=start_date, expiry_date=expiry_date, created_by=None, note=None)

def handle_payment(request, subscription_id):
    """ Get the payment details from the form """
    payment_amount = request.form.get('payment_amount')
    card_number = request.form.get('cardNumber')
    card_cvv = request.form.get('cardCVV')
    card_expiry_date = request.form.get('cardExpiryDate')
    card_holder = request.form.get('cardHolder')
    card_type = request.form.get('cardType')
    billing_country = request.form.get('country')
    address1 = request.form.get('addressLine1')
    address2 = request.form.get('addressLine2')
    city = request.form.get('city')
    state = request.form.get('state')
    postal = request.form.get('postalCode')
    return PaymentRepository.create_payment(subscription_id, payment_amount, card_number, card_cvv, card_expiry_date, card_holder, card_type, billing_country, address1, address2, city, state, postal)

@premium.route('/premium_features')
@requires_permission('view_premium_features')
def premium_features():
    subscription_plans = SubscriptionRepository.get_subscription_plan(subscription=True)
    user_id = session.get('user_id')
    user = UserRepository.get_user(user_id=user_id)
    return render_template('premium_features.html', subscription_plans=subscription_plans, user=user)

@premium.route('/premium_features/subscribe', methods=['GET', 'POST'])
@requires_permission('view_subscription_page')
def subscribe_to_premium_features():
    if request.method == 'POST' and 'plan_id' in request.form:
        if has_permission('create_subscription'):
            plan_id = request.form.get('plan_id')
            plan = SubscriptionRepository.get_subscription_plan(subscription_plan_id=plan_id)
            if not plan:
                flash("Invalid subscription plan selected.", 'error')
                return redirect(url_for('premium.premium_features'))
            return render_template('payment.html', plan=plan)
        else:
            flash("You don't need to purchase a subscription.", 'info')

    subscription_plans = SubscriptionRepository.get_subscription_plan(subscription_type='Purchased')
    return render_template('subscription.html', subscription_plans=subscription_plans)

@premium.route('/premium_features/trial', methods=['GET', 'POST'])
@requires_permission('view_trial_page')
def subscribe_to_trial():
    if request.method == 'POST' and 'plan_id' in request.form:
        user_id = session.get('user_id')
        if has_permission('create_trial'):
            free_trial = SubscriptionRepository.get_free_trial_subscription(user_id=user_id)
            if free_trial and free_trial['trial_used'] == 1:
                flash("You have already used your free trial.", 'error')
                return redirect(url_for('premium.premium_features'))
            else:
                subscription_id = handle_subscription(request, user_id)
                if not subscription_id:
                    flash("Failed to makr a  subscription.", 'error')
                    return redirect(url_for('premium.subscribe_to_premium_features'))
                free_trial = SubscriptionRepository.create_free_trial_subscription(user_id=user_id, trial_used=1, subscription_id=subscription_id)
                if free_trial <= 0:
                    flash("Failed to create free trial subscription.", 'error')
                    return redirect(url_for('premium.subscribe_to_premium_features'))

            role = "trial"
            result = UserRepository.update_user(user_id=user_id, role=role)
            if result == -1:
                flash("Failed to update user role.", 'error')
                return redirect(url_for('premium.subscribe_to_premium_features'))
            else:
                from app.auth.view import update_session
                update_session(user_id)
                flash("Subscription successfully!", 'success')
            return redirect(url_for('premium.premium_features'))
    subscription_plans = SubscriptionRepository.get_subscription_plan(subscription_type='Trial')
    return render_template('subscription.html', subscription_plans=subscription_plans)

@premium.route('/premium_features/payment', methods=['POST'])
@requires_permission('create_subscription')
def process_payment():
    if request.method == 'POST':
        user_id = session.get('user_id')
        # Create subscription and payment records
        subscription_id = handle_subscription(request, user_id)
        if not subscription_id:
            flash("Failed to makr a subscription.", 'error')
            return redirect(url_for('premium.subscribe_to_premium_features'))

        payment = handle_payment(request, subscription_id)
        if not payment:
            flash("Failed to process payment.", 'error')
            return redirect(url_for('premium.subscribe_to_premium_features'))

        role = "premium"
        result = UserRepository.update_user(user_id=user_id, role=role)
        if result == -1:
            flash("Failed to update user role.", 'error')
            return redirect(url_for('premium.subscribe_to_premium_features'))
        else:
            from app.auth.view import update_session
            update_session(user_id)
            flash("Subscription and payment processed successfully!", 'success')
        return redirect(url_for('premium.premium_features'))

    return redirect(url_for('premium.premium_features'))


@premium.route('/subscription/manage')
@requires_permission('view_premium_features')
def manage_subscription():
    user_id = session.get('user_id')
    all_subscription_plans = SubscriptionRepository.get_all_subscription_details(user_id=user_id)
    first_subscribed_date = SubscriptionRepository.get_first_subscribed_date(user_id)

    payment_details = SubscriptionRepository.get_all_subscription_transaction_details(user_id)
    user_data = UserRepository.get_user(user_id=user_id)
    
    has_active_subscription = UserRepository.get_active_subscription(user_id) is not None

    return render_template('subscription_details.html',
                           all_subscription_plans=all_subscription_plans,
                           has_active_subscription = has_active_subscription,
                           first_subscribed_date=first_subscribed_date,
                           payment_details=payment_details,
                           user_data=user_data)

@premium.route('/subscription/history')
@requires_permission('view_premium_features')
def subscription_history():
    user_id = session.get('user_id')
    staff_view_user_id = request.args.get('user_id', None)

    if staff_view_user_id and not has_permission('view_others_subscriptions'):
        return render_template('access_denied.html'), 403

    if staff_view_user_id:
        user_id =staff_view_user_id
    payment_details = SubscriptionRepository.get_all_subscription_transaction_details(user_id)

    return render_template('subscription_history_traveller.html', payment_details=payment_details, staff_view_user_id=staff_view_user_id)

@premium.route('/subscription/viewinvoice/<int:payment_id>')
@requires_permission('view_premium_features')
def view_subscription_invoice(payment_id):
    user_id = session.get('user_id')
    staff_view_user_id = request.args.get('user_id', None)

    payment_details = SubscriptionRepository.get_invoice_details(payment_id)

    for detail in payment_details:
        if user_id != detail['user_id'] and not has_permission('view_others_subscriptions'):
            return render_template('access_denied.html'), 403

    return render_template('subscription_receipt_traveller.html', payment_details=payment_details, staff_view_user_id=staff_view_user_id)

@premium.route('/premium_features/check_trial')
@requires_permission('create_trial')
def check_trial():
    user_id = session.get('user_id')
    free_trial = SubscriptionRepository.get_free_trial_subscription(user_id=user_id)
    if free_trial and free_trial['trial_used'] == 1:
        flash("A user has only one free subscription opportunity, you can only get one free subscription, please purchase a subscription if you want to access premium features.", 'error')
        return redirect(url_for('premium.subscribe_to_premium_features'))
    else:
        subscription_plans = SubscriptionRepository.get_subscription_plan(subscription_type='Trial')
        current_date = datetime.now()
        start_date = current_date
        duration_months = subscription_plans[0]['duration_months']
        expiry_date = start_date + timedelta(days=30 * duration_months)
        trial = {
            'start_date': start_date,
            'expiry_date': expiry_date,
            'duration_months': duration_months
        }
        flash("You are eligible for a free trial.", 'success')
        return render_template('subscription.html', subscription_plans=subscription_plans, trial=trial)

@premium.route('/location/follow/<int:location_id>', methods=['POST'])
@requires_permission('follow_location')
def followed_location(location_id):
    user_id = session.get('user_id')
    user_role = session.get('role')
    event_id = request.form.get('event_id')

    if user_role in ['traveller']:
        flash('Only paid users and staff can follow locations.', 'warning')
        return redirect(url_for('premium.premium_features'))

    success = LocationRepository.follow_location(user_id, location_id)
    if success:
        flash('You are now following this location.', 'success')
    else:
        flash('You are already following this location.', 'info')
    return redirect(url_for('event.event_detail', event_id=event_id))

@premium.route('/location/unfollow/<int:location_id>', methods=['POST'])
@requires_permission('follow_location')
def unfollowed_location(location_id):
    event_id = request.form.get('event_id')
    LocationRepository.unfollow_location(session['user_id'], location_id)
    flash('Location unfollowed.', 'info')
    return redirect(url_for('event.event_detail', event_id=event_id))

@premium.route('/premium_features/follow_user', methods=['POST'])
@requires_permission('follow_user')
def follow_user():
    user_id = session.get('user_id')
    user_role = session.get('role')
    if request.method == 'POST' and 'followed_user_id' in request.form:
        followed_user_id = request.form.get('followed_user_id')
        journey_id = request.form.get('journey_id', None)
        page = request.form.get('page', None)

        if user_role in ['traveller']:
            flash('Only paid users and staff can follow users.', 'warning')
            return redirect(url_for('premium.premium_features'))

        result = FollowRepository.create_follow_user(follower_id=user_id, followed_id=followed_user_id)
        if result:
            gamification_service.check_achievement(user_id, 13)  # Check for "Follow Any User Who is Shared His Journey Public" achievement
            flash("Successfully followed the user!", 'success')
        else:
            flash("Failed to follow the user.", 'error')
        if journey_id:    
            return redirect(url_for('journey.journey_detail', journey_id=journey_id))
        else:
            if page:
                return redirect(url_for('user.view_other_profile', selected_user_id=followed_user_id, page=page))
            else:
                return redirect(url_for('user.view_other_profile', selected_user_id=followed_user_id))
    

@premium.route('/premium_features/unfollow_user', methods=['POST'])
@requires_permission('follow_user')
def unfollow_user():
    user_id = session.get('user_id')
    user_role = session.get('role')
    if request.method == 'POST' and 'followed_user_id' in request.form:
        followed_user_id = request.form.get('followed_user_id')
        journey_id = request.form.get('journey_id')
        page = request.form.get('page', None)

        if user_role in ['traveller']:
            flash('Only paid users and staff can unfollow users.', 'warning')
            return redirect(url_for('premium.premium_features'))

        result = FollowRepository.delete_follow_user(follower_id=user_id, followed_id=followed_user_id)
        if result:
            flash("Successfully unfollowed the user!", 'success')
        else:
            flash("Failed to unfollow the user.", 'error')
        if journey_id:    
            return redirect(url_for('journey.journey_detail', journey_id=journey_id))
        else:
            if page:
                return redirect(url_for('user.view_other_profile', selected_user_id=followed_user_id, page=page))
            else:
                return redirect(url_for('user.view_other_profile', selected_user_id=followed_user_id))


@premium.route('/premium_features/follow_journey', methods=['POST'])
@requires_permission('follow_journey')
def follow_journey():
    user_id = session.get('user_id')
    user_role = session.get('role')

    if request.method == 'POST' and 'journey_id' in request.form:
        journey_id = request.form.get('journey_id')

        if user_role in ['traveller']:
            flash('Only paid users and staff can follow journeys.', 'warning')
            return redirect(url_for('premium.premium_features'))

        result = FollowRepository.create_follow_journey(follower_id=user_id, journey_id=journey_id)
        if result:
            gamification_service.check_achievement(user_id, 12)  # CHeck for "Follow First "Shared Journey" achievement
            flash("Successfully followed the journey!", 'success')
        else:
            flash("Failed to follow the journey.", 'error')
        return redirect(url_for('journey.journey_detail', journey_id=journey_id))

@premium.route('/premium_features/unfollow_journey', methods=['POST'])
@requires_permission('follow_journey')
def unfollow_journey():
    user_id = session.get('user_id')
    user_role = session.get('role')
    if request.method == 'POST' and 'journey_id' in request.form:
        journey_id = request.form.get('journey_id')

        if user_role in ['traveller']:
            flash('Only paid users and staff can unfollow journeys.', 'warning')
            return redirect(url_for('premium.premium_features'))

        result = FollowRepository.delete_follow_journey(follower_id=user_id, journey_id=journey_id)
        if result:
            flash("Successfully unfollowed the journey!", 'success')
        else:
            flash("Failed to unfollow the journey.", 'error')
        return redirect(url_for('journey.journey_detail', journey_id=journey_id))
    
    
def generate_expiring_notifications():
    """ Generate notifications for the user which is expiringin the next 7 Days """
    
    expiring_subscriptions = NotificationRepository.get_expiring_subscription_details()
    print(expiring_subscriptions)
    
    if(expiring_subscriptions is not None):
        
        for subscription in expiring_subscriptions:
            
            user_id = subscription['user_id']
            
            if subscription['days_remaining'] == 0:
                message = "Your plan expiring today"
            
            elif (subscription['days_remaining'] <= 7 ):    
                message = "Your plan will expire in "+str(subscription['days_remaining'])+ " Days"
                
            
            notification_response = NotificationRepository.create_system_notification(user_id,message,'Subscription')
            # print(type(notification_response))
            print("Notification Id:"+str(notification_response))
                
    else:
        print("No expiring subscriptions..!!")

def revert_user_after_subscription_expired():
    """ Reset user status when subscription expires """
    
    expired_subscriptions = SubscriptionRepository.get_expired_subscription_details()
    
    if(expired_subscriptions is not None):
    
        for exp_subscription in expired_subscriptions:
            if(exp_subscription['days_remaining'] < 0):
                user_id = exp_subscription['user_id']
                response = UserRepository.update_user(user_id, role='traveller')
                print("user updated:"+str(response))
                message = f"Your subscription has expired, you have been reverted to Free Traveller."
                result = NotificationRepository.create_system_notification(user_id, message, 'Subscription')
                # print(type(response))
    else:
        print("No subscriptions expiring today..!!")

def update_subscription_expiry_date(user_id, new_expiry_date):
    """ Update the subscription expiry date for a user """
    
    subscriptions = UserRepository.get_subscription_history(user_id)
    for subscription in subscriptions:
        response = SubscriptionRepository.update_subscription_expiry_date(subscription['subscription_id'], new_expiry_date)
        if response:
            flash(f"Subscription expiry date updated to {new_expiry_date.strftime('%d %b %Y')}", 'success')
        else:
            flash(f"Failed to update subscription expiry date", 'error')     