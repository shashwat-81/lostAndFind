function checkNotifications() {
    fetch('/notifications/count')
        .then(response => response.json())
        .then(data => {
            const count = data.count;
            const badge = document.getElementById('notification-badge');
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        });
}

// Check notifications every minute
setInterval(checkNotifications, 60000);
checkNotifications(); // Initial check