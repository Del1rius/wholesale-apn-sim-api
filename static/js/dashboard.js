/* ============================================================
   DASHBOARD.JS — Fleet dashboard page JavaScript
   Backspace Technologies
   ============================================================ */

let currentFilter = 'all';

function filterTable() {
    const query = document.getElementById('simSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#simTable tbody tr[data-status]');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const status = row.dataset.status;
        const matchSearch = text.includes(query);
        const matchFilter = currentFilter === 'all' || status === currentFilter;
        row.style.display = matchSearch && matchFilter ? '' : 'none';
    });
}

function setFilter(status, btn) {
    currentFilter = status;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterTable();
}

// Animate usage bars on page load
function animateUsageBars() {
    const bars = document.querySelectorAll('.usage-bar-fill');
    bars.forEach(bar => {
        const targetWidth = bar.getAttribute('data-width');
        if (targetWidth) {
            // Small delay to ensure CSS transition works
            setTimeout(() => {
                bar.style.width = targetWidth + '%';
            }, 100);
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    animateUsageBars();
});

// Live clock for last update
function updateClock() {
    const lastUpdateEl = document.getElementById('last-update');
    if (lastUpdateEl) {
        lastUpdateEl.textContent = new Date().toLocaleTimeString();
    }
}
setInterval(updateClock, 1000);

// Auto-refresh every 60 seconds
setTimeout(() => location.reload(), 60000);
