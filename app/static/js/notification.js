document.addEventListener('DOMContentLoaded', function() {
    // Title character counter
    initializeTitleCounter();

    // Initialize tab switching if on notifications page
    initializeTabSwitching();

    // Initialize read all buttons if on notifications page
    initializeMarkAllReadButtons();

    // Always initialize the notification system if user is logged in
    initializeNotificationSystem();

    // Initialize single message "Read" buttons
    initializeSingleMessageReadButtons();

    // Initialize edit log read buttons on journey page
    initializeEditLogReadButtons();
});

/**
 * Display a toast notification using Bootstrap Toast
 */
function showToast(message, category = 'success') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // Determine toast styling based on category
    let headerBg, icon, title;
    switch (category) {
        case 'success':
            headerBg = 'bg-success';
            icon = 'bi-check-circle-fill';
            title = 'Success';
            break;
        case 'danger':
        case 'error':
            headerBg = 'bg-danger';
            icon = 'bi-exclamation-triangle-fill';
            title = 'Error';
            break;
        case 'warning':
            headerBg = 'bg-warning';
            icon = 'bi-exclamation-triangle-fill';
            title = 'Warning';
            break;
        case 'info':
            headerBg = 'bg-info';
            icon = 'bi-info-circle-fill';
            title = 'Info';
            break;
        default:
            headerBg = 'bg-primary';
            icon = 'bi-info-circle-fill';
            title = 'Notification';
    }
    
    // Create unique ID for this toast
    const toastId = 'toast-' + Date.now();
    
    // Create toast element
    const toastElement = document.createElement('div');
    toastElement.className = 'toast';
    toastElement.id = toastId;
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    toastElement.innerHTML = `
        <div class="toast-header ${headerBg} text-white">
            <i class="bi ${icon} me-2"></i>
            <strong class="me-auto">${title}</strong>
            <small>now</small>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toastElement);
    
    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000 // 5 seconds
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Initialize tab switching functionality
 */
function initializeTabSwitching() {
    // Check if on notifications page
    const tabsContainer = document.getElementById('notificationTabs');
    if (!tabsContainer) return;
    
    // Get tab elements
    const announcementsTab = document.getElementById('announcements-tab');
    const subscriptionsTab = document.getElementById('subscriptions-tab');
    const editLogsTab = document.getElementById('edit-logs-tab');
    
    // Get URL parameters to determine active tab
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    
    // Set active tab based on URL parameter
    if (tabParam === 'subscriptions') {
        activateTab('subscriptions', subscriptionsTab);
    } else if (tabParam === 'edit-logs') {
        activateTab('edit-logs', editLogsTab);
    } else {
        activateTab('announcements', announcementsTab);
    }

    if (editLogsTab) {
        editLogsTab.addEventListener('click', function() {
            const url = new URL(window.location);
            url.searchParams.set('tab', 'edit-logs');
            window.history.pushState({}, '', url);
        });
    }
    
    // Add click event listeners to update URL when tabs are clicked
    announcementsTab.addEventListener('click', function() {
        // Update URL without reloading the page
        const url = new URL(window.location);
        url.searchParams.set('tab', 'announcements');
        window.history.pushState({}, '', url);
    });
    
    subscriptionsTab.addEventListener('click', function() {
        // Update URL without reloading the page
        const url = new URL(window.location);
        url.searchParams.set('tab', 'subscriptions');
        window.history.pushState({}, '', url);
    });

    function activateTab(tabName, tabElement) {
        // Only target nav-links within the notification tabs container
        document.querySelectorAll('#notificationTabs .nav-link').forEach(tab => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
        });
        
        tabElement.classList.add('active');
        tabElement.setAttribute('aria-selected', 'true');
        document.getElementById(tabName).classList.add('show', 'active');
    }   
}

/**
 * Mark all announcements as read
 */
function markAllAnnouncementsAsRead() {
    return fetch('/api/announcements/mark-all-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
            if (data.success) {
                // Show success message if not on inform page
                const tabsContainer = document.getElementById('notificationTabs');
                if (!tabsContainer && data.message) {
                    //showTemporaryMessage('Announcements marked as read', 'success');
                    showToast('Announcements marked as read', 'success');
                }
                
                // Check if on inform page
                if (tabsContainer) {
                    // On inform page, update content
                    initializeTitleCounter();
                    window.location.reload();
                } else {
                    // Not on inform page, update dropdown
                    setTimeout(() => {
                        updateNotificationBellCount();
                        refreshNotificationDropdown();
                    }, 500);
                }
            } else {
                //showTemporaryMessage('Failed to mark announcements as read', 'danger');
                showToast('Failed to mark announcements as read', 'danger');
            }
    })
    .catch(error => {
        console.error('Error in markAllAnnouncementsAsRead:', error);
        //showTemporaryMessage('Error marking announcements as read', 'danger');
        showToast('Error marking announcements as read', 'danger');
        return { success: false };
    });
}

/**
 * Mark all subscription notifications as read
 */
function markAllSubscriptionNotificationsAsRead() {
    return fetch('/api/systemnotifications/mark-all-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
            if (data.success) {
                // Show success message if not on inform page
                const tabsContainer = document.getElementById('notificationTabs');
                if (!tabsContainer && data.message) {
                    //showTemporaryMessage('System notifications marked as read', 'success');
                    showToast('System notifications marked as read', 'success');
                }
                
                // Check if on inform page
                if (tabsContainer) {
                    // On inform page, update content
                    initializeTitleCounter();
                    window.location.reload();
                } else {
                    // Not on inform page, update dropdown
                    setTimeout(() => {
                        updateNotificationBellCount();
                        refreshNotificationDropdown();
                    }, 500);
                }
            } else {
                //showTemporaryMessage('Failed to mark system notifications as read', 'danger');
                showToast('Failed to mark system notifications as read', 'danger');
            }
    })
    .catch(error => {
        console.error('Error in markAllSubscriptionNotificationsAsRead:', error);
        //showTemporaryMessage('Error marking system notifications as read', 'danger');
        showToast('Error marking system notifications as read', 'danger');
        return { success: false };
    });
}

/**
 * Mark all edit log messages as read
 */
function markAllEditLogsAsRead() {
    // Get edit log ID
    return fetch('/api/editlogs/mark-all-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
            if (data.success) {
                // Show success message if not on inform page
                const tabsContainer = document.getElementById('notificationTabs');
                if (!tabsContainer && data.message) {
                    //showTemporaryMessage('Edit logs marked as read', 'success');
                    showToast('Edit logs marked as read', 'success');
                }
                
                // Check if on inform page
                if (tabsContainer) {
                    // On inform page, update content
                    initializeTitleCounter();
                    window.location.reload();
                } else {
                    // Not on inform page, update dropdown
                    setTimeout(() => {
                        updateNotificationBellCount();
                        refreshNotificationDropdown();
                    }, 500);
                }
            } else {
                //showTemporaryMessage('Failed to mark edit logs as read', 'danger');
                showToast('Failed to mark edit logs as read', 'danger');
            }
    })
    .catch(error => {
        console.error('Error in markAllEditLogsAsRead:', error);
        //showTemporaryMessage('Error marking edit logs as read', 'danger');
        showToast('Error marking edit logs as read', 'danger');
        return { success: false };
    });
}

/**
 * Mark all event edit log messages as read
 */
function markAllEditLogsHistoryAsRead(journey_id, event_id) {
    return fetch('/api/editlogs_history/mark-all-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ journey_id: journey_id, event_id: event_id})
    })
    .then(response => response.json())
    .then(data => {
            if (data.success) {
                // Show success message if not on inform page
                const tabsContainer = document.getElementById('notificationTabs');
                
                // Check if on inform page
                if (tabsContainer) {
                    // On inform page, update content
                    initializeTitleCounter();
                    window.location.reload();
                } else {
                    // Not on inform page, update dropdown
                    window.location.reload();
                }
            } else {
                //showTemporaryMessage('Failed to mark edit logs as read', 'danger');
                showToast('Failed to mark all event edit logs as read', 'danger');
            }
    })
    .catch(error => {
        console.error('Error in markAllEventEditLogsAsRead:', error);
        //showTemporaryMessage('Error marking edit logs as read', 'danger');
        showToast('Error marking all event edit logs as read', 'danger');
        return { success: false };
    });
}

/**
 * Global function to update notification bell count
 * This function is accessible from anywhere in the file
 */
function updateNotificationBellCount() {
    return Promise.all([
        fetch('/api/announcements/unread-count').then(res => res.json()).catch(() => ({ success: false, count: 0 })),
        fetch('/api/subscriptionnotifications/unread-count').then(res => res.json()).catch(() => ({ success: false, count: 0 })),
        fetch('/api/editnotifications/unread-count').then(res => res.json()).catch(() => ({ success: false, count: 0 }))
    ])
    .then(([announcements, subscriptions, edits]) => {
        const totalCount = 
            (announcements.success ? announcements.count : 0) +
            (subscriptions.success ? subscriptions.count : 0) +
            (edits.success ? edits.count : 0);
        
        // Update bell notification badge
        const notificationBadge = document.getElementById('notification-badge');
        if (notificationBadge) {
            if (totalCount > 0) {
                notificationBadge.textContent = totalCount;
                notificationBadge.classList.remove('d-none');
            } else {
                notificationBadge.classList.add('d-none');
            }
        }
        
        return totalCount;
    })
    .catch(error => {
        console.error('Error updating notification bell count:', error);
        return 0;
    });
}

/**
 * Refresh the notification dropdown content
 */
function refreshNotificationDropdown() {
    // Only refresh if the notification system has been initialized
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) return;

    getAllUnreadNotifications();
}

// Format edit log summary for display
function formatEditLogSummary(notification) {
    let title = notification.edit_reason || 'Content was edited';
    
    // Add prefix for staff edits
    title = `Staff changed your journey: ${title}`;
    
    // If summary exists and has content, append the changes information
    if (notification.summary && Array.isArray(notification.summary) && notification.summary.length > 0) {
        const changes = notification.summary.map(change => {
            const field = change.item || 'field';
            let oldVal = change.old_value ? String(change.old_value).substring(0, 20) : 'empty';
            let newVal = change.new_value ? String(change.new_value).substring(0, 20) : 'empty';
            
            // Special handling for image fields
            if (field === 'cover_image' || field === 'event_image') {
                oldVal = 'image';
            }

            // Truncate long values and add ellipsis
            const oldDisplay = oldVal.length > 20 ? oldVal + '...' : oldVal;
            const newDisplay = newVal.length > 20 ? newVal + '...' : newVal;
            
            return `${field}: "${oldDisplay}" → "${newDisplay}"`;
        }).join(', ');
        
        title = `${title} (${changes})`;
    }
    
    return title;
}

/**
 * Get all unread notifications and update UI
 */
function getAllUnreadNotifications() {
    Promise.all([
        fetch('/api/announcements/unread')
            .then(response => response.json())
            .catch(error => {
                console.error('Error checking announcements:', error);
                return { success: false, announcements: [] };
            }),
        fetch('/api/subscriptionnotifications/unread')
            .then(response => response.json())
            .catch(error => {
                console.error('Error checking subscription notifications:', error);
                return { success: false, notification_list: [] };
            }),
        fetch('/api/editnotifications/unread')
            .then(response => response.json())
            .catch(error => {
                console.error('Error checking edit notifications:', error);
                return { success: false, notifications: [] };
            })
    ])
    .then(([announcementsData, subscriptionsData, editsData]) => {
        // Combine all notifications
        const allNotifications = [];
        
        // Add announcements
        if (announcementsData.success && announcementsData.announcements) {
            announcementsData.announcements.forEach(announcement => {
                allNotifications.push({
                    type: 'announcement',
                    id: announcement.announcement_id,
                    title: announcement.title,
                    date: new Date(announcement.create_time),
                    link: `/announcement/${announcement.announcement_id}`,
                    icon: 'bi-megaphone-fill',
                    iconBg: 'bg-primary'
                });
            });
        }
        
        // Add subscription notifications
        if (subscriptionsData.success && subscriptionsData.notification_list) {
            subscriptionsData.notification_list.forEach(notification => {
                allNotifications.push({
                    type: 'subscription',
                    id: notification.notification_id,
                    title: notification.message,
                    date: new Date(notification.created_at),
                    link: '/inform?tab=subscriptions',
                    icon: 'bi-star-fill',
                    iconBg: 'bg-warning'
                });
            });
        }
        
        // Add edit notifications
        if (editsData.success && editsData.notifications) {
            editsData.notifications.forEach(notification => {
                // Parse summary if it's a JSON string
                let parsedSummary = notification.summary;
                if (typeof notification.summary === 'string') {
                    try {
                        parsedSummary = JSON.parse(notification.summary);
                    } catch (e) {
                        parsedSummary = null;
                    }
                }
                const editNotification = {
                    type: 'edit',
                    id: notification.notification_id,
                    edit_reason: notification.edit_reason,
                    summary: parsedSummary,
                    date: new Date(notification.created_at),
                    link: '/inform?tab=edit-logs',
                    icon: 'bi-pencil-fill',
                    iconBg: 'bg-info'
                };

                 // Format the title with summary information
                editNotification.title = formatEditLogSummary(editNotification);
                
                allNotifications.push(editNotification);
            });
        }
        
        // Sort all notifications by date (newest first)
        allNotifications.sort((a, b) => b.date - a.date);
        
        // Update the UI with the combined and sorted notifications
        updateNotificationsUI(allNotifications);
    })
    .catch(error => console.error('Error getting all notifications:', error));
}

/**
 * Update the notification dropdown with all notifications
 */
function updateNotificationsUI(allNotifications) {
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) return;
    
    // Clear existing content
    notificationContainer.innerHTML = '';

    if (!allNotifications || allNotifications.length === 0) {
        // No notifications to show
        const emptyState = document.createElement('div');
        emptyState.className = 'dropdown-item text-center py-3';
        emptyState.innerHTML = `
            <span class="text-muted">No notifications</span>
        `;
        notificationContainer.appendChild(emptyState);
        return;
    }

    // Create notification items
    allNotifications.forEach(notification => {
        const notificationItem = document.createElement('a');
        notificationItem.className = 'dropdown-item d-flex align-items-center py-2 border-bottom';
        notificationItem.href = notification.link;
        
        // Format date
        const dateString = notification.date.toLocaleDateString();
        
        notificationItem.innerHTML = `
        <div class="flex-shrink-0 me-2 mt-1">
            <span class="${notification.iconBg} text-white rounded-circle p-1 d-inline-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">
                <i class="bi ${notification.icon}" style="font-size: 0.75rem;"></i>
            </span>
        </div>
        <div class="flex-grow-1" style="min-width: 0; max-width: 280px;">
            <div class="fw-medium mb-1" style="
                line-height: 1.4; 
                word-wrap: break-word; 
                overflow-wrap: break-word; 
                word-break: break-word;
                white-space: normal;
                display: -webkit-box;
                -webkit-box-orient: vertical;
                overflow: hidden;
            ">${notification.title}</div>
            <div class="small text-muted">${dateString}</div>
        </div>
        `;
        notificationContainer.appendChild(notificationItem);
    });

    // Add "Mark all as read" button only if there are notifications
    if (allNotifications.length > 0) {
        const markAllReadLink = document.createElement('a');
        markAllReadLink.className = 'dropdown-item text-center text-primary small pt-2';
        markAllReadLink.href = '#';
        markAllReadLink.textContent = 'Mark all notifications as read';
        markAllReadLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Dropdown mark all button clicked'); // Debug log
            markAllNotificationsAsRead();
        });
        notificationContainer.appendChild(markAllReadLink);
    }
}

/**
 * Initialize read all buttons functionality
 */
function initializeMarkAllReadButtons() {
    // Check for announcements read all button
    const markAllAnnouncementsReadBtn = document.getElementById('markAllAnnouncementsReadBtn');
    if (markAllAnnouncementsReadBtn) {
        markAllAnnouncementsReadBtn.addEventListener('click', function() {
            console.log('Marking all announcements as read...');
            // Send request to mark all announcements as read
            markAllAnnouncementsAsRead()
                .then(data => {
                    console.log('Mark all announcements response:', data);
                    if (data.success) {
                        // Update UI - remove unread highlighting and badge in announcements tab
                        const unreadRows = document.querySelectorAll('#announcements tr.table-primary');
                        unreadRows.forEach(row => {
                            row.classList.remove('table-primary');
                        });
                        
                        const unreadBadges = document.querySelectorAll('#announcements .badge.bg-danger');
                        unreadBadges.forEach(badge => {
                            if (badge.textContent === 'New') {
                                badge.remove();
                            }
                        });
                        
                        // Update notification bell
                        updateNotificationBellCount();
                        // Hide the read all button
                        markAllAnnouncementsReadBtn.style.display = 'none';
                        // Update the badge on the announcements tab
                        const announcementsTabBadge = document.querySelector('#announcements-tab .badge');
                        if (announcementsTabBadge) {
                            announcementsTabBadge.remove();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error marking announcements as read:', error);
                });
        });
    }
    
    // Check for subscription messages read all button
    const markAllSubscriptionsReadBtn = document.getElementById('markAllSubscriptionsReadBtn');
    if (markAllSubscriptionsReadBtn) {
        markAllSubscriptionsReadBtn.addEventListener('click', function() {
            console.log('Marking all subscription notifications as read...');
            // Send request to mark all subscription messages as read
            markAllSubscriptionNotificationsAsRead()
                .then(data => {
                    console.log('Mark all subscriptions response:', data);
                    if (data.success) {
                        // Update UI - remove unread highlighting and badge in subscriptions tab
                        const unreadRows = document.querySelectorAll('#subscriptions tr.table-primary');
                        unreadRows.forEach(row => {
                            row.classList.remove('table-primary');
                        });
                        
                        const unreadBadges = document.querySelectorAll('#subscriptions .badge.bg-danger');
                        unreadBadges.forEach(badge => {
                            if (badge.textContent === 'New') {
                                badge.remove();
                            }
                        });
                        
                        // Update notification bell
                        updateNotificationBellCount();
                        // Hide the read all button
                        markAllSubscriptionsReadBtn.style.display = 'none';
                        // Update the badge on the subscriptions tab
                        const subscriptionsTabBadge = document.querySelector('#subscriptions-tab .badge');
                        if (subscriptionsTabBadge) {
                            subscriptionsTabBadge.remove();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error marking subscription notifications as read:', error);
                });
        });
    }

    // Check for edit logs read all button
    const markAllEditLogsReadBtn = document.getElementById('markAllEditLogsReadBtn');
    if (markAllEditLogsReadBtn) {
        markAllEditLogsReadBtn.addEventListener('click', function() {
            console.log('Marking all edit logs as read...');
            // Send request to mark all edit logs as read
            markAllEditLogsAsRead()
                .then(data => {
                    console.log('Mark all edit logs response:', data);
                    if (data.success) {
                        // Update UI - remove unread highlighting and badge in edit logs tab
                        const unreadRows = document.querySelectorAll('#edit-logs tr.table-primary');
                        unreadRows.forEach(row => {
                            row.classList.remove('table-primary');
                        });
                        
                        const unreadBadges = document.querySelectorAll('#edit-logs .badge.bg-danger');
                        unreadBadges.forEach(badge => {
                            if (badge.textContent === 'New') {
                                badge.remove();
                            }
                        });
                        
                        // Update notification bell
                        updateNotificationBellCount();
                        // Hide the read all button
                        markAllEditLogsReadBtn.style.display = 'none';
                        // Update the badge on the edit logs tab
                        const editLogsTabBadge = document.querySelector('#edit-logs-tab .badge');
                        if (editLogsTabBadge) {
                            editLogsTabBadge.remove();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error marking edit logs as read:', error);
                });
        });
    }

    //
    const markAllEventEditLogsReadBtn = document.getElementById('markAllEventEditLogsReadBtn');
    if (markAllEventEditLogsReadBtn) {
        markAllEventEditLogsReadBtn.addEventListener('click', function() {
            const event_id = markAllEventEditLogsReadBtn.getAttribute('data-event-id');
            markAllEditLogsHistoryAsRead(null, event_id)
            .then(data => {
                    console.log('Mark all event edit logs response:', data);
                    if (data.success) {
                        const unreadBadges = document.querySelectorAll('#edit-logs .badge.bg-danger.me2');
                        unreadBadges.forEach(badge => {
                            if (badge.textContent === 'New') {
                                badge.remove();
                            }
                        });
                        
                        // Update notification bell
                        updateNotificationBellCount();
                        // Hide the read all button
                        markAllEditLogsReadBtn.style.display = 'none';
                        // Update the badge on the edit logs tab
                        const editLogsTabBadge = document.querySelector('#edit-logs-tab .badge');
                        if (editLogsTabBadge) {
                            editLogsTabBadge.remove();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error marking all event edit logs as read:', error);
                });
        });
    }

    //
    const markAllJourneyEditLogsReadBtn = document.getElementById('markAllJourneyEditLogsReadBtn');
    if (markAllJourneyEditLogsReadBtn) {
        markAllJourneyEditLogsReadBtn.addEventListener('click', function() {
            const journey_id = markAllJourneyEditLogsReadBtn.getAttribute('data-journey-id');
            markAllEditLogsHistoryAsRead(journey_id, null)
            .then(data => {
                    console.log('Mark all journey edit logs response:', data);
                    if (data.success) {
                        const unreadBadges = document.querySelectorAll('#edit-logs .badge.bg-danger.me2');
                        unreadBadges.forEach(badge => {
                            if (badge.textContent === 'New') {
                                badge.remove();
                            }
                        });
                        
                        // Update notification bell
                        updateNotificationBellCount();
                        // Hide the read all button
                        markAllEditLogsReadBtn.style.display = 'none';
                        // Update the badge on the edit logs tab
                        const editLogsTabBadge = document.querySelector('#edit-logs-tab .badge');
                        if (editLogsTabBadge) {
                            editLogsTabBadge.remove();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error marking all journey edit logs as read:', error);
                });
        });
    }
}

/**
 * Initialize title character counter
 */
function initializeTitleCounter() {
    const titleInput = document.getElementById('title');
    const titleCounter = document.getElementById('titleCounter');
    
    if (!titleInput || !titleCounter) return;
    
    // Get maxlength from the input element dynamically
    const maxLength = parseInt(titleInput.getAttribute('maxlength')) || 255;
    
    // Update counter on load
    updateCharacterCount(titleInput, titleCounter, maxLength);
    
    // Update counter on input
    titleInput.addEventListener('input', function() {
        updateCharacterCount(titleInput, titleCounter, maxLength);
    });
}

/**
 * Update character count for input fields
 */
function updateCharacterCount(inputElement, counterElement, maxLength) {
    const currentLength = inputElement.value.length;
    counterElement.textContent = `${currentLength}/${maxLength}`;
    
    // Remove all color classes first
    counterElement.classList.remove('text-muted', 'text-warning', 'text-danger');
    
    // Add appropriate color based on character count
    if (currentLength > maxLength) {
        counterElement.classList.add('text-danger');
    } else if (currentLength > maxLength * 0.9) {
        counterElement.classList.add('text-danger');
    } else if (currentLength > maxLength * 0.8) {
        counterElement.classList.add('text-warning');
    } else {
        counterElement.classList.add('text-muted');
    }
}

/**
 * Display a temporary success message
 */
// function showTemporaryMessage(message, type = 'success') {
//     // Create message element
//     const messageDiv = document.createElement('div');
//     messageDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
//     messageDiv.style.cssText = 'top: 80px; right: 20px; z-index: 1055; min-width: 300px;';
//     messageDiv.innerHTML = `
//         ${message}
//         <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
//     `;
    
//     // Add to page
//     document.body.appendChild(messageDiv);
    
//     // Auto remove after 3 seconds
//     setTimeout(() => {
//         if (messageDiv.parentNode) {
//             messageDiv.remove();
//         }
//     }, 3000);
// }

/**
 * Mark all notifications as read (all types) - Global function
 */
function markAllNotificationsAsRead() {
    fetch('/api/notifications/mark-all-read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message from API response
            if (data.message) {
                //showTemporaryMessage(data.message, 'success');
                showToast(data.message, 'success');
            }
            
            // Clear all notifications from UI
            const notificationContainer = document.getElementById('notification-container');
            if (notificationContainer) {
                notificationContainer.innerHTML = '';
                
                // Show empty state
                const emptyState = document.createElement('div');
                emptyState.className = 'dropdown-item text-center py-3';
                emptyState.innerHTML = `
                    <span class="text-muted">No notifications</span>
                `;
                notificationContainer.appendChild(emptyState);
            }
            
            // Update notification count
            updateNotificationBellCount();
            
            // Check if on inform page and update accordingly
            const tabsContainer = document.getElementById('notificationTabs');
            if (tabsContainer) {
                // On inform page, reload to show updated content
                setTimeout(() => {
                    window.location.reload();
                }, 1000); // Delay to show the message before reload
            } else {
                // Not on inform page, refresh dropdown
                setTimeout(() => {
                    refreshNotificationDropdown();
                }, 500);
            }
        } else {
            // Show error message
            //showTemporaryMessage(data.message || 'Failed to mark notifications as read', 'danger');
            showToast(data.message || 'Failed to mark notifications as read', 'danger');
        }
    })
    .catch(error => {
        console.error('Error marking all notifications as read:', error);
        //showTemporaryMessage('Error marking notifications as read', 'danger');
        showToast('Error marking notifications as read', 'danger');
    });
}

/**
 * Initialize the notification system in the navbar
 */
function initializeNotificationSystem() {
    // Check if user is logged in (by checking if notification bell exists)
    const notificationBell = document.querySelector('.bi-bell');
    if (!notificationBell) return;

    // Elements
    const notificationBadge = document.getElementById('notification-badge');
    const notificationContainer = document.getElementById('notification-container');
    
    if (!notificationBadge || !notificationContainer) return;

    // Check for all types of notifications
    checkAllNotifications();

    // Refresh notifications every 1 minutes
    setInterval(checkAllNotifications, 60000); 

    /**
     * Check for all types of unread notifications and update UI
     */
    function checkAllNotifications() {
        // Get all notifications
        getAllUnreadNotifications();
        
        // Update total count badge
        updateNotificationBellCount();
    }
}

// Initialize single message "Mark as Read" buttons
function initializeSingleMessageReadButtons() {
    // Find all "Read" buttons
    const markAsReadBtns = document.querySelectorAll('.mark-as-read-btn');
    
    // Add click event handlers to each button
    markAsReadBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Get notification ID
            const notificationId = this.getAttribute('data-notification-id');
            
            // Send request to mark as read
            fetch('/api/subscriptionnotifications/mark-as-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ notification_id: notificationId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mark successful, update UI
                    const row = this.closest('tr');
                    
                    // Remove blue highlight
                    row.classList.remove('table-primary');
                    
                    // Remove "New" badge
                    const newBadge = row.querySelector('.badge.bg-danger.me-2');
                    if (newBadge && newBadge.textContent === 'New') {
                        newBadge.remove();
                    }
                    
                    // Update button to match the read state style
                    this.outerHTML = '<button type="button" class="btn btn-sm btn-outline-secondary" disabled>Read</button>';
                    
                    // Update notification counts and dropdown with longer delay
                    setTimeout(() => {
                        updateNotificationBellCount();
                        refreshNotificationDropdown(); // Add this line to refresh dropdown
                    }, 500); // Increased delay to 500ms
                    
                    // Update subscriptions tab badge count
                    updateSubscriptionsTabBadge();
                } else {
                    showToast('Failed to mark notification as read', 'danger');
                }
            })
            .catch(error => {
                console.error('Error marking message as read:', error);
                showToast('Error marking notification as read', 'danger');
            });
        });
    });
}

// Update unread count badge on subscriptions tab
function updateSubscriptionsTabBadge() {
    // Get unread count badge on subscriptions tab
    const subscriptionsTabBadge = document.querySelector('#subscriptions-tab .badge');
    if (subscriptionsTabBadge) {
        // Get current unread message count
        let unreadCount = parseInt(subscriptionsTabBadge.textContent);
        
        // Decrease count
        unreadCount--;
        
        if (unreadCount <= 0) {
            // If no unread messages, remove badge
            subscriptionsTabBadge.remove();
            
            // Hide "Read All" button
            const markAllSubscriptionsReadBtn = document.getElementById('markAllSubscriptionsReadBtn');
            if (markAllSubscriptionsReadBtn) {
                markAllSubscriptionsReadBtn.style.display = 'none';
            }
        } else {
            // Update badge count
            subscriptionsTabBadge.textContent = unreadCount;
        }
    }
}

// Update unread count badge on editlog tab
function updateEditLogsTabBadge() {
    // Get unread count badge on edit logs tab
    const editlogsTabBadge = document.querySelector('#edit-logs-tab .badge');
    if (editlogsTabBadge) {
        // Get current unread message count
        let unreadCount = parseInt(editlogsTabBadge.textContent);
        
        // Decrease count
        unreadCount--;
        
        if (unreadCount <= 0) {
            // If no unread messages, remove badge
            editlogsTabBadge.remove();
            
            // Hide "Read All" button
            const markAllEditLogsReadBtn = document.getElementById('markAllEditLogsReadBtn');
            if (markAllEditLogsReadBtn) {
                markAllEditLogsReadBtn.style.display = 'none';
            }
        } else {
            // Update badge count
            editlogsTabBadge.textContent = unreadCount;
        }
    }
}

// Update unread count badge on journey and event edit history page
function updateJourneyEventEditHistoryBadge() {
    // Count remaining unread edit logs on the page
    const remainingUnreadBadges = document.querySelectorAll('.edit-log-entry .badge.bg-danger');
    const unreadCount = Array.from(remainingUnreadBadges).filter(badge => badge.textContent === 'New').length;
    
    // Find the Edit History badge in journey detail page
    const allH5Elements = document.querySelectorAll('.card-header h5');
    let editHistoryTitle = null;

    allH5Elements.forEach(h5 => {
        if (h5.textContent.includes('Edit History')) {
            editHistoryTitle = h5;
        }
    });

    if (editHistoryTitle && editHistoryTitle.textContent.includes('Edit History')) {
        const existingBadge = editHistoryTitle.querySelector('.badge.bg-danger');
        
        if (unreadCount > 0) {
            if (existingBadge) {
                // Update existing badge
                existingBadge.textContent = unreadCount;
            } else {
                // Create new badge if it doesn't exist
                const newBadge = document.createElement('span');
                newBadge.className = 'badge bg-danger ms-2';
                newBadge.textContent = unreadCount;
                editHistoryTitle.appendChild(newBadge);
            }
        } else {
            // Remove badge if no unread items
            if (existingBadge) {
                existingBadge.remove();
            }
            
            // Hide "Read All" button
            const markAllJourneyEditLogsReadBtn = document.getElementById('markAllJourneyEditLogsReadBtn');
            if (markAllJourneyEditLogsReadBtn) {
                markAllJourneyEditLogsReadBtn.style.display = 'none';
            }

            // Hide "Read All" button
            const markAllEventEditLogsReadBtn = document.getElementById('markAllEventEditLogsReadBtn');
            if (markAllEventEditLogsReadBtn) {
                markAllEventEditLogsReadBtn.style.display = 'none';
            }
        }
    }
}

// Function to refresh notification count - now calls the global function
function refreshNotificationCount() {
    updateNotificationBellCount();
}

// Function to refresh the inform page with the current tab
function refreshWithCurrentTab() {
    const currentTab = new URLSearchParams(window.location.search).get('tab') || 'announcements';
    window.location.href = `/inform?tab=${currentTab}`;
}

// initializeEditLogReadButtons function
function initializeEditLogReadButtons() {
    // mark edit logs as read for inform page
    const markEditAsReadBtns = document.querySelectorAll('.mark-edit-log-read-btn');
    // mark edit logs as read for journey edit log history page
    const markJourneyEditAsReadHistoryBtns = document.querySelectorAll('.mark-journey-edit-log-history-read-btn');
    // mark edit logs as read for event edit log history page
    const markEventEditAsReadHistoryBtns = document.querySelectorAll('.mark-event-edit-log-history-read-btn');
    
    // Add click event handlers to each button
    markEditAsReadBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Get edit log ID
            const editLogId = this.getAttribute('data-edit-log-id');
            // Send request to mark as read
            fetch('/api/editlogs/mark-as-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ edit_log_id: editLogId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mark successful, find the corresponding View button and redirect
                    const row = this.closest('tr');
                    const viewButton = row.querySelector('a.btn[href]'); // Find the View button with href
                    
                    if (viewButton) {
                        // Get the target URL and redirect
                        const targetUrl = viewButton.getAttribute('href');
                        window.location.href = targetUrl;
                    } else {
                        // Fallback to reload if no View button found
                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    }
                } else {
                    showToast('Failed to mark edit log as read', 'danger');
                }
            })
            .catch(error => {
                console.error('Error marking edit log as read:', error);
                showToast('Error marking edit log as read', 'danger');
            });
        });
    });

    // Add click event handlers for journey edit log history buttons
    markJourneyEditAsReadHistoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Get edit log ID
            const editLogId = this.getAttribute('data-edit-log-id');
            // Send request to mark as read
            fetch('/api/editlogs/mark-as-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ edit_log_id: editLogId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mark successful, update UI
                    const row = this.closest('.edit-log-entry');

                    if (!row) {
                        console.error('Could not find parent container');
                        return;
                    }
                    // Remove "New" badge
                    const newBadge = row.querySelector('.badge.bg-danger');
                    if (newBadge && newBadge.textContent === 'New') {
                        newBadge.remove();
                    }
                    // Update button to match the read state style
                    this.outerHTML = '<span class="badge bg-secondary">Read</span>';
                    // Update notification counts and dropdown with longer delay
                    setTimeout(() => {
                        updateNotificationBellCount();
                        refreshNotificationDropdown(); // Add this line to refresh dropdown
                    }, 500); // Increased delay to 500ms
                    
                    // Update edit logs badge count
                    updateJourneyEventEditHistoryBadge();
                } else {
                    showToast('Failed to mark journey edit log as read', 'danger');
                }
            })
            .catch(error => {
                console.error('Error marking journey edit log as read:', error);
                showToast('Error marking journey edit log as read', 'danger');
            });
        });
    });

    // Add click event handlers for event edit log history buttons
    markEventEditAsReadHistoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Get edit log ID
            const editLogId = this.getAttribute('data-edit-log-id');
            // Send request to mark as read
            fetch('/api/editlogs/mark-as-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ edit_log_id: editLogId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mark successful, update UI
                    const row = this.closest('.edit-log-entry');

                    if (!row) {
                        console.error('Could not find parent container');
                        return;
                    }
                    // Remove "New" badge
                    const newBadge = row.querySelector('.badge.bg-danger');
                    if (newBadge && newBadge.textContent === 'New') {
                        newBadge.remove();
                    }
                    // Update button to match the read state style
                    this.outerHTML = '<span class="badge bg-secondary">Read</span>';
                    // Update notification counts and dropdown with longer delay
                    setTimeout(() => {
                        updateNotificationBellCount();
                        refreshNotificationDropdown(); // Add this line to refresh dropdown
                    }, 500); // Increased delay to 500ms
                    
                    // Update edit logs badge count
                    updateJourneyEventEditHistoryBadge();
                } else {
                    showToast('Failed to mark event edit log as read', 'danger');
                }
            })
            .catch(error => {
                console.error('Error marking event edit log as read:', error);
                showToast('Error marking event edit log as read', 'danger');
            });
        });
    });
}