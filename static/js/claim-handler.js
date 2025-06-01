function initializeClaimHandlers() {
    console.log('Initializing claim handlers...');

    document.querySelectorAll('.approve-claim, .reject-claim').forEach(button => {
        console.log('Found button:', button.className);
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.classList.contains('approve-claim') ? 'approve' : 'reject';
            const claimId = this.dataset.claimId;
            const itemId = this.dataset.itemId;

            console.log('Processing claim:', { action, claimId, itemId });

            handleClaimAction(this, action, claimId, itemId);
        });
    });
}

function handleClaimAction(button, action, claimId, itemId) {
    if (!confirm(`Are you sure you want to ${action} this claim?`)) {
        return;
    }

    // Disable button and show loading state
    button.disabled = true;
    const originalText = button.innerHTML;
    button.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Processing...`;

    fetch(`/items/${itemId}/claim/${claimId}/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Claim ${action}ed successfully`, 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            throw new Error(data.message || 'Failed to process claim');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message, 'danger');
        // Reset button state
        button.disabled = false;
        button.innerHTML = originalText;
    });
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <span>${message}</span>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeClaimHandlers);