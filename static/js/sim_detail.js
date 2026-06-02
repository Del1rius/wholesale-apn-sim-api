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
document.getElementById('editModal').addEventListener('click', (e) => {
    if (e.target.id === 'editModal') {
        closeEditModal();
    }
});
