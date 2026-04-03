// ==================== FORM VALIDATION ====================

function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input, textarea, select');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim() && input.required) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// ==================== FORM INTERACTIONS ====================

document.addEventListener('DOMContentLoaded', function() {
    // Real-time form validation
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.required && !this.value.trim()) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });

        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    });

    // Number inputs - prevent negative values
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.min && parseFloat(this.value) < parseFloat(this.min)) {
                this.value = this.min;
            }
            if (this.max && parseFloat(this.value) > parseFloat(this.max)) {
                this.value = this.max;
            }
        });
    });
});

// ==================== NAVBAR INTERACTIONS ====================

function toggleNavbar() {
    const menu = document.getElementById('navbarMenu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.querySelector('.user-menu');
    if (userMenu && !userMenu.contains(event.target)) {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.classList.remove('active');
        }
    }
});

// ==================== TOAST NOTIFICATIONS ====================

function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.createElement('div');
    toastContainer.className = `toast toast-${type}`;
    toastContainer.innerHTML = `
        <div class="toast-content">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    document.body.appendChild(toastContainer);

    setTimeout(() => {
        toastContainer.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toastContainer.remove(), 300);
    }, duration);
}

function showSuccessToast(message) {
    showToast(message, 'success');
}

function showErrorToast(message) {
    showToast(message, 'error');
}

function showWarningToast(message) {
    showToast(message, 'warning');
}

function showInfoToast(message) {
    showToast(message, 'info');
}

// ==================== MODAL ====================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// ==================== TABLE UTILITIES ====================

function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const cellA = a.cells[columnIndex].textContent.trim();
        const cellB = b.cells[columnIndex].textContent.trim();

        // Try numeric comparison
        const numA = parseFloat(cellA);
        const numB = parseFloat(cellB);

        if (!isNaN(numA) && !isNaN(numB)) {
            return numA - numB;
        }

        // String comparison
        return cellA.localeCompare(cellB);
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

function filterTable(tableId, searchValue) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tbody tr');
    const searchLower = searchValue.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchLower) ? '' : 'none';
    });
}

// ==================== CLIPBOARD ====================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccessToast('Copied to clipboard!');
    }).catch(() => {
        showErrorToast('Failed to copy');
    });
}

// ==================== FORMATTING ====================

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

// ==================== LOADING STATE ====================

function setButtonLoading(buttonElement, isLoading = true) {
    if (isLoading) {
        buttonElement.disabled = true;
        buttonElement.innerHTML = '<span class="spinner"></span> Loading...';
    } else {
        buttonElement.disabled = false;
        buttonElement.innerHTML = buttonElement.dataset.originalText || 'Submit';
    }
}

// ==================== DEBOUNCE ====================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== LOCAL STORAGE ====================

function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Error saving to localStorage:', e);
        return false;
    }
}

function getFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return defaultValue;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (e) {
        console.error('Error removing from localStorage:', e);
        return false;
    }
}

// ==================== DARK MODE ====================

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    saveToLocalStorage('darkMode', isDarkMode);
}

// Initialize dark mode on page load
document.addEventListener('DOMContentLoaded', function() {
    const isDarkMode = getFromLocalStorage('darkMode', false);
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
});

// ==================== ANIMATIONS ====================

function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease`;

    setTimeout(() => {
        element.style.opacity = '1';
    }, 10);
}

function fadeOut(element, duration = 300) {
    element.style.opacity = '1';
    element.style.transition = `opacity ${duration}ms ease`;

    setTimeout(() => {
        element.style.opacity = '0';
    }, 10);
}

// ==================== SCROLL UTILITIES ====================

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function smoothScroll(targetId) {
    const target = document.getElementById(targetId);
    if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
    }
}

// Show "scroll to top" button on scroll
window.addEventListener('scroll', function() {
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (scrollTopBtn) {
        if (window.pageYOffset > 300) {
            scrollTopBtn.style.display = 'block';
        } else {
            scrollTopBtn.style.display = 'none';
        }
    }
});

// ==================== DEVICE DETECTION ====================

function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function isTablet() {
    return /iPad|Android|Android/i.test(navigator.userAgent);
}

// ==================== API HELPERS ====================

async function fetchJSON(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// ==================== PRINT FUNCTIONALITY ====================

function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const printWindow = window.open('', '', 'height=500,width=800');
    printWindow.document.write(element.innerHTML);
    printWindow.document.close();
    printWindow.print();
}

// ==================== EXPORT DATA ====================

function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        cols.forEach(col => {
            csvRow.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(csvRow.join(','));
    });

    const csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', filename);
    link.click();
}

// ==================== UTILITY FUNCTIONS ====================

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

function getURLParam(paramName) {
    const url = new URL(window.location);
    return url.searchParams.get(paramName);
}

console.log('%c DiaPredict Interactive Utilities Loaded', 'color: #667eea; font-size: 16px; font-weight: bold;');
