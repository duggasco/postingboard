// Common JavaScript functionality

// Flash message auto-hide
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Common utility functions
const utils = {
    // Format date
    formatDate: function(dateString) {
        // Parse date string as local date to avoid timezone issues
        // When given 'YYYY-MM-DD', treat it as a local date, not UTC
        const [year, month, day] = dateString.split('-').map(num => parseInt(num, 10));
        const date = new Date(year, month - 1, day); // month is 0-indexed
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    // Escape HTML
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Fetch with error handling
    fetchJson: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }
};

// Notification System
let notificationsPanelOpen = false;

async function loadNotifications() {
    try {
        console.log('Loading notifications...');
        const response = await fetch('/api/user/notifications');
        
        if (!response.ok) {
            console.error('Failed to fetch notifications:', response.status, response.statusText);
            return;
        }
        
        const data = await response.json();
        
        console.log('Notification API response:', JSON.stringify(data, null, 2));
        
        const notificationsList = document.getElementById('notifications-list');
        const notificationCount = document.getElementById('notification-count');
        
        if (!notificationsList || !notificationCount) {
            console.log('Notification elements not found - notificationsList:', notificationsList, 'notificationCount:', notificationCount);
            return; // Elements not found on this page
        }
        
        console.log('Notification elements found, unread count:', data.unread_count);
        
        if (data.success) {
            if (data.notifications.length === 0) {
                notificationsList.innerHTML = '<div class="empty-notifications">No notifications</div>';
                notificationCount.style.display = 'none';
            } else {
                let html = '';
                data.notifications.forEach(notif => {
                    const typeClass = `type-${notif.type}`;
                    const unreadClass = notif.is_read ? '' : 'unread';
                    
                    html += `
                        <div class="notification-item ${unreadClass}">
                            <button class="notification-delete" onclick="event.stopPropagation(); deleteNotification(${notif.id})" title="Delete notification">×</button>
                            <div class="notification-content" onclick="handleNotificationClick(${notif.id}, ${notif.idea_id || 'null'}, '${notif.type}')">
                                <div class="notification-title">
                                    ${notif.title}
                                    <span class="notification-type-badge ${typeClass}">${formatNotificationType(notif.type)}</span>
                                </div>
                                <div class="notification-message">${notif.message}</div>
                                <div class="notification-time">${notif.time_ago}</div>
                            </div>
                        </div>
                    `;
                });
                notificationsList.innerHTML = html;
                
                // Update badge
                if (data.unread_count > 0) {
                    console.log('Setting notification count to:', data.unread_count);
                    notificationCount.textContent = data.unread_count;
                    // Use important to override any conflicting styles
                    notificationCount.style.cssText = 'display: inline-block !important; visibility: visible !important; opacity: 1 !important;';
                    console.log('Badge updated - text:', notificationCount.textContent, 'styles:', notificationCount.style.cssText);
                    
                    // Double-check the element is visible
                    const computedStyle = window.getComputedStyle(notificationCount);
                    console.log('Computed styles - display:', computedStyle.display, 'visibility:', computedStyle.visibility, 'opacity:', computedStyle.opacity);
                    
                    // Force a reflow to ensure the browser updates
                    notificationCount.offsetHeight;
                } else {
                    console.log('No unread notifications, hiding badge');
                    notificationCount.style.cssText = 'display: none !important;';
                }
            }
        } else {
            // Handle error case - show "No notifications" instead of leaving "Loading..."
            notificationsList.innerHTML = '<div class="empty-notifications">No notifications</div>';
            notificationCount.style.display = 'none';
            if (data.error) {
                console.error('Notification API error:', data.error);
            }
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        // Also handle network errors - show "No notifications" instead of leaving "Loading..."
        const notificationsList = document.getElementById('notifications-list');
        const notificationCount = document.getElementById('notification-count');
        if (notificationsList) {
            notificationsList.innerHTML = '<div class="empty-notifications">Unable to load notifications</div>';
        }
        if (notificationCount) {
            notificationCount.style.display = 'none';
        }
    }
}

function formatNotificationType(type) {
    const typeMap = {
        'claim_request': 'Claim Request',
        'claim_approved': 'Approved',
        'claim_denied': 'Denied',
        'status_change': 'Status Update',
        'idea_completed': 'Completed',
        'assigned': 'Assigned',
        'new_team_member': 'Team Update',
        'new_manager': 'New Manager',
        'manager_approved': 'Manager Approved',
        'manager_denied': 'Manager Denied',
        'team_approval_request': 'Team Request',
        'team_approved': 'Team Approved',
        'team_denied': 'Team Denied',
        'test_notification': 'Test'
    };
    return typeMap[type] || type;
}

function toggleNotifications() {
    const panel = document.getElementById('notifications-panel');
    if (!panel) return;
    
    notificationsPanelOpen = !notificationsPanelOpen;
    panel.style.display = notificationsPanelOpen ? 'flex' : 'none';
    
    if (notificationsPanelOpen) {
        loadNotifications();
    }
}

async function handleNotificationClick(notificationId, ideaId, notificationType) {
    // Mark as read
    await fetch(`/api/user/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    // Refresh notifications
    loadNotifications();
    
    // Navigate based on notification type
    let destination = null;
    
    // Routing logic based on notification type
    switch(notificationType) {
        // Team-related notifications
        case 'team_approval_request':
            // Admin notifications for team approval
            destination = '/admin/teams';
            break;
            
        case 'team_approved':
        case 'team_denied':
            // User should check their profile to see team status
            destination = '/profile';
            break;
            
        // Manager-related notifications
        case 'manager_approved':
        case 'manager_denied':
            // User can see their manager status
            destination = '/profile';
            break;
            
        case 'new_manager':
        case 'new_team_member':
            // Go to team page to see team members
            destination = '/my-team';
            break;
            
        // Claim-related notifications
        case 'claim_request':
            // Idea owner goes to my-ideas to approve/deny
            destination = '/my-ideas';
            break;
            
        case 'claim_approved':
        case 'claim_denied':
            // If we have an idea ID, go to the idea, otherwise my-ideas
            destination = ideaId ? `/idea/${ideaId}` : '/my-ideas';
            break;
            
        // Idea-related notifications
        case 'status_change':
        case 'idea_completed':
        case 'assigned':
            // Go to the specific idea if we have the ID
            if (ideaId) {
                destination = `/idea/${ideaId}`;
            } else {
                destination = '/my-ideas';
            }
            break;
            
        // Default case - if idea ID exists, go to idea, otherwise my-ideas
        default:
            if (ideaId) {
                destination = `/idea/${ideaId}`;
            }
            break;
    }
    
    // Navigate to the destination if we have one
    if (destination) {
        window.location.href = destination;
    }
}

async function deleteNotification(notificationId) {
    try {
        const response = await fetch(`/api/user/notifications/${notificationId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Refresh the notifications list
            loadNotifications();
        } else {
            console.error('Failed to delete notification:', data.message || data.error);
            alert('Failed to delete notification. Please try again.');
        }
    } catch (error) {
        console.error('Error deleting notification:', error);
        alert('Error deleting notification. Please try again.');
    }
}

// Initialize notifications when DOM is ready
function initializeNotifications() {
    if (window.notificationsInitialized) {
        console.log('Notifications already initialized, skipping...');
        return;
    }
    
    console.log('Initializing notifications...');
    window.notificationsInitialized = true;
    
    // Only initialize if user is logged in (notification bell exists)
    const notificationBell = document.getElementById('notification-bell');
    const notificationCount = document.getElementById('notification-count');
    
    console.log('Found notification bell:', notificationBell);
    console.log('Found notification count:', notificationCount);
    
    if (notificationBell) {
        console.log('Notification bell found, loading notifications...');
        loadNotifications();
        
        // Refresh notifications every 30 seconds
        setInterval(loadNotifications, 30000);
        
        // Close notifications panel when clicking outside
        document.addEventListener('click', function(event) {
            const bell = document.getElementById('notification-bell');
            const panel = document.getElementById('notifications-panel');
            
            if (notificationsPanelOpen && bell && panel && 
                !bell.contains(event.target) && !panel.contains(event.target)) {
                toggleNotifications();
            }
        });
    }
}

// Set up multiple initialization strategies
document.addEventListener('DOMContentLoaded', initializeNotifications);

// Also try to initialize if DOM is already loaded
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    console.log('DOM already loaded, initializing notifications immediately...');
    initializeNotifications();
}

// Fallback: initialize after a short delay
setTimeout(function() {
    const notificationBell = document.getElementById('notification-bell');
    if (notificationBell && !window.notificationsInitialized) {
        console.log('Fallback initialization of notifications...');
        window.notificationsInitialized = true;
        initializeNotifications();
    }
}, 500);

// Extra fallback for admin pages that may have complex initialization
if (window.location.pathname.includes('/admin')) {
    setTimeout(function() {
        const notificationBell = document.getElementById('notification-bell');
        const notificationCount = document.getElementById('notification-count');
        if (notificationBell && notificationCount && !window.adminNotificationsLoaded) {
            console.log('Admin page fallback - forcing notification load...');
            window.adminNotificationsLoaded = true;
            loadNotifications();
        }
    }, 1000);
    
    // Additional fallback specifically for fixing the inline style issue
    setTimeout(function() {
        const notificationCount = document.getElementById('notification-count');
        if (notificationCount && notificationCount.textContent !== '0') {
            console.log('Fixing notification badge visibility - current text:', notificationCount.textContent);
            notificationCount.removeAttribute('style');
            notificationCount.style.display = 'inline-block';
            notificationCount.style.visibility = 'visible';
            notificationCount.style.opacity = '1';
        }
    }, 1500);
}

// Debug function that can be called from console
window.debugNotifications = async function() {
    console.log('=== Debug Notifications ===');
    const bell = document.getElementById('notification-bell');
    const count = document.getElementById('notification-count');
    console.log('Bell element:', bell);
    console.log('Count element:', count);
    console.log('Count text:', count?.textContent);
    console.log('Count display:', count?.style.display);
    console.log('Count inline style:', count?.getAttribute('style'));
    
    console.log('\nForcing notification load...');
    await loadNotifications();
    
    console.log('\nAfter load:');
    console.log('Count text:', count?.textContent);
    console.log('Count display:', count?.style.display);
    console.log('Count inline style:', count?.getAttribute('style'));
};

// Manual fix function for testing
window.fixNotificationBadge = function() {
    const count = document.getElementById('notification-count');
    if (count) {
        const currentText = count.textContent;
        console.log('Current badge text:', currentText);
        if (currentText && currentText !== '0') {
            count.setAttribute('style', 'display: inline-block !important;');
            console.log('Badge should now be visible');
        }
    }
};

// User Dropdown Menu
let userDropdownOpen = false;

function toggleUserMenu(event) {
    event.stopPropagation();
    const button = event.target.closest('.user-menu-button');
    const menu = document.getElementById('user-dropdown-menu');
    
    userDropdownOpen = !userDropdownOpen;
    
    if (userDropdownOpen) {
        button.classList.add('active');
        menu.classList.add('active');
    } else {
        button.classList.remove('active');
        menu.classList.remove('active');
    }
}

// Close user dropdown when clicking outside
document.addEventListener('click', function(event) {
    const button = document.querySelector('.user-menu-button');
    const menu = document.getElementById('user-dropdown-menu');
    
    if (userDropdownOpen && button && menu && 
        !button.contains(event.target) && !menu.contains(event.target)) {
        userDropdownOpen = false;
        button.classList.remove('active');
        menu.classList.remove('active');
    }
});