/* ============================================================
   SIM_DETAIL.JS — SIM detail page JavaScript
   Backspace Technologies
   Version: 1.3 - Circle capped at 360 degrees (100%)
   ============================================================ */

// Animate usage ring on load
document.addEventListener('DOMContentLoaded', () => {
    const circle = document.getElementById('usageCircle');
    if (!circle) return;
    const actualPct = parseFloat(circle.dataset.targetPct) || 0;

    // HARD CAP at 100% for visual display
    // This prevents the circle from ever going past 360 degrees
    const displayPct = actualPct > 100 ? 100 : actualPct;

    const circumference = 427;
    // Calculate offset for display percentage only
    // 0% = offset 427 (empty), 100% = offset 0 (full 360 degree circle)
    const calculatedOffset = circumference - (displayPct / 100) * circumference;

    // Extra safety: never allow negative offset
    const finalOffset = calculatedOffset < 0 ? 0 : calculatedOffset;

    console.log(`Actual: ${actualPct}% | Display: ${displayPct}% | Offset: ${finalOffset}`);

    // Start with empty circle
    circle.style.strokeDashoffset = circumference;

    // Animate to target
    setTimeout(() => {
        circle.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)';
        circle.style.strokeDashoffset = finalOffset;
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

// Validate data limit input
function validateDataLimit() {
    const input = document.getElementById('data_limit_mb');
    const value = parseInt(input.value);
    const form = input.closest('form');
    const submitBtn = form.querySelector('button[type="submit"]');

    // Remove any existing error message
    let existingError = input.parentElement.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }

    // Validate
    if (isNaN(value) || value < 1) {
        showValidationError(input, 'Data limit must be at least 1 MB');
        submitBtn.disabled = true;
        return false;
    } else if (value > 100000) {
        showValidationError(input, 'Data limit cannot exceed 100,000 MB');
        submitBtn.disabled = true;
        return false;
    } else {
        submitBtn.disabled = false;
        return true;
    }
}

function showValidationError(input, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-error';
    errorDiv.style.color = 'var(--red-danger)';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.5rem';
    errorDiv.textContent = message;
    input.parentElement.appendChild(errorDiv);
}

// Add validation on input
document.addEventListener('DOMContentLoaded', () => {
    const dataLimitInput = document.getElementById('data_limit_mb');
    if (dataLimitInput) {
        dataLimitInput.addEventListener('input', validateDataLimit);
        dataLimitInput.addEventListener('blur', validateDataLimit);

        // Validate on form submit
        const form = dataLimitInput.closest('form');
        form.addEventListener('submit', (e) => {
            if (!validateDataLimit()) {
                e.preventDefault();
            }
        });
    }
});

// Close modal on ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeEditModal();
    }
});

// Close modal on background click
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'editModal') {
                closeEditModal();
            }
        });
    }
});
