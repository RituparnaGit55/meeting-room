function escapeHtmlBase(text) {
    if (!text) return '';
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}
window.escapeHtmlBase = escapeHtmlBase;

document.addEventListener('DOMContentLoaded', function() {
    console.log('MeetFlow platform loaded with Notification Toast & Confirmation Modal system');

    // Delegate click for any element with data-confirm-delete="true"
    document.body.addEventListener('click', function(e) {
        const deleteBtn = e.target.closest('[data-confirm-delete="true"]');
        if (deleteBtn) {
            e.preventDefault();
            const itemName = deleteBtn.getAttribute('data-item-name') || '';
            const title = deleteBtn.getAttribute('data-confirm-title') || 'Confirm Deletion';
            const message = deleteBtn.getAttribute('data-confirm-message') || 'Are you sure you want to delete this item? This action cannot be undone.';
            
            if (typeof promptConfirmDelete === 'function') {
                promptConfirmDelete({
                    title: title,
                    message: message,
                    itemName: itemName,
                    onConfirm: () => {
                        const form = deleteBtn.closest('form');
                        if (form) {
                            form.submit();
                        } else if (deleteBtn.href) {
                            window.location.href = deleteBtn.href;
                        }
                    }
                });
            } else if (confirm(`${message} ${itemName ? `("${itemName}")` : ''}`)) {
                const form = deleteBtn.closest('form');
                if (form) form.submit();
                else if (deleteBtn.href) window.location.href = deleteBtn.href;
            }
        }
    });
});
