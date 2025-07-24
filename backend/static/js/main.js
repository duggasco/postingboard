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
        const response = await fetch('/api/user/notifications');
        const data = await response.json();
        
        console.log('Notification API response:', data);
        
        const notificationsList = document.getElementById('notifications-list');
        const notificationCount = document.getElementById('notification-count');
        
        if (!notificationsList || !notificationCount) {
            return; // Elements not found on this page
        }
        
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
                        <div class="notification-item ${unreadClass}" onclick="handleNotificationClick(${notif.id}, ${notif.idea_id || 'null'})">
                            <div class="notification-title">
                                ${notif.title}
                                <span class="notification-type-badge ${typeClass}">${formatNotificationType(notif.type)}</span>
                            </div>
                            <div class="notification-message">${notif.message}</div>
                            <div class="notification-time">${notif.time_ago}</div>
                        </div>
                    `;
                });
                notificationsList.innerHTML = html;
                
                // Update badge
                if (data.unread_count > 0) {
                    notificationCount.textContent = data.unread_count;
                    notificationCount.style.display = 'inline-block';
                } else {
                    notificationCount.style.display = 'none';
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
        'assigned': 'Assigned',
        'new_team_member': 'Team Update',
        'manager_approved': 'Manager Approved',
        'manager_denied': 'Manager Denied',
        'team_approval_request': 'Team Request',
        'team_approved': 'Team Approved',
        'team_denied': 'Team Denied'
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

async function handleNotificationClick(notificationId, ideaId) {
    // Mark as read
    await fetch(`/api/user/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    // Refresh notifications
    loadNotifications();
    
    // Navigate to idea if applicable
    if (ideaId) {
        window.location.href = `/idea/${ideaId}`;
    }
}

// Initialize notifications when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is logged in (notification bell exists)
    const notificationBell = document.getElementById('notification-bell');
    if (notificationBell) {
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
});

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