function checkNotifications() {
    fetch('/notifications/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notification-badge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline';
                } else {
                    badge.style.display = 'none';
                }
            }
        });
}

// Check notifications every 30 seconds
setInterval(checkNotifications, 30000);
checkNotifications(); // Initial check