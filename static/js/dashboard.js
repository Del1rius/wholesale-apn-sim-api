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

function setFilter(status, element) {
    currentFilter = status;

    // Remove active class from all filter buttons and stat cards
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.clickable-stat').forEach(c => c.classList.remove('stat-active'));

    // Add active class to the clicked element
    if (element) {
        if (element.classList.contains('filter-btn')) {
            element.classList.add('active');
            // Also highlight corresponding stat card
            const statCard = document.querySelector(`.clickable-stat[data-filter="${status}"]`);
            if (statCard) statCard.classList.add('stat-active');
        } else if (element.classList.contains('clickable-stat')) {
            element.classList.add('stat-active');
            // Also highlight corresponding filter button
            const filterButtons = document.querySelectorAll('.filter-btn');
            filterButtons.forEach(btn => {
                if ((status === 'all' && btn.textContent.trim() === 'All') ||
                    (status === 'Assigned' && btn.textContent.trim() === 'Active') ||
                    (status === 'Suspended' && btn.textContent.trim() === 'Suspended')) {
                    btn.classList.add('active');
                }
            });
        }
    }

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
