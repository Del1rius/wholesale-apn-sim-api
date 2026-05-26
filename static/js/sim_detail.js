/* ============================================================
   SIM_DETAIL.JS — SIM detail page JavaScript
   Backspace Technologies
   ============================================================ */

// Animate usage ring on load
document.addEventListener('DOMContentLoaded', () => {
    const circle = document.getElementById('usageCircle');
    if (!circle) return;
    const pct = parseFloat(circle.dataset.targetPct) || 0;
    const circumference = 427;
    const offset = circumference - (pct / 100) * circumference;
    circle.style.strokeDashoffset = circumference; // start at 0
    setTimeout(() => {
        circle.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
        circle.style.strokeDashoffset = offset;
    }, 300);
});

// Modal functions
function openEditModal() {
    document.getElementById('editModal').style.display = 'flex';
    document.getElementById('data_limit_mb').focus();
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// Close modal on ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeEditModal();
    }
});

// Close modal on background click
document.getElementById('editModal').addEventListener('click', (e) => {
    if (e.target.id === 'editModal') {
        closeEditModal();
    }
});
