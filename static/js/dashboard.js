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

    console.log('=== setFilter called ===');
    console.log('Status:', status);
    console.log('Clicked element:', element);

    // FIRST: Remove active class from ALL stat cards
    const allStatCards = document.querySelectorAll('.clickable-stat');
    allStatCards.forEach(card => {
        card.classList.remove('stat-active');
    });

    // Remove active class from all filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // SECOND: Add active class ONLY to the clicked element
    if (element) {
        if (element.classList.contains('filter-btn')) {
            // Filter button was clicked
            element.classList.add('active');
            // Also highlight corresponding stat card
            const statCard = document.querySelector(`.clickable-stat[data-filter="${status}"]`);
            if (statCard) {
                statCard.classList.add('stat-active');
                console.log('Activated stat card for:', status);
            }
        } else if (element.classList.contains('clickable-stat')) {
            // Stat card was clicked directly
            element.classList.add('stat-active');
            console.log('Activated clicked stat card');

            // Also highlight corresponding filter button
            const filterButtons = document.querySelectorAll('.filter-btn');
            filterButtons.forEach(btn => {
                const btnText = btn.textContent.trim();
                if ((status === 'all' && btnText === 'All') ||
                    (status === 'Assigned' && btnText === 'Active') ||
                    (status === 'Suspended' && btnText === 'Suspended')) {
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

    // Set "Total SIMs" (all) as active by default on page load
    const totalSimsCard = document.querySelector('.clickable-stat[data-filter="all"]');
    if (totalSimsCard) {
        totalSimsCard.classList.add('stat-active');
        console.log('Total SIMs card set as active on load');
    }

    // Also highlight the "All" filter button
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        if (btn.textContent.trim() === 'All') {
            btn.classList.add('active');
        }
    });
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
