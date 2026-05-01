// Modal functions
function openVirtualKeyboard() {
    document.getElementById('virtualKeyboardModal').style.display = 'block';
}

function openWhiteboard() {
    document.getElementById('whiteboardModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Additional utility functions
function startVirtualKeyboard() {
    closeModal('virtualKeyboardModal');
}

function startWhiteboard() {
    closeModal('whiteboardModal');
}

function viewHistory() {
    alert('History feature coming soon!');
}

function exportData() {
    alert('Export feature coming soon!');
}

// Form validation and interaction functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    // Password inputs (no validation suggestions)
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.borderColor = '#5d4037';
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderColor = '#e0e0e0';
            }
        });
    });
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Validation functions
function validateEmail(input) {
    const email = input.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        input.style.borderColor = '#ff6b6b';
        showFieldError(input, 'Please enter a valid email address');
    } else {
        input.style.borderColor = '#5d4037';
        clearFieldError(input);
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// UI feedback functions
function showFieldError(input, message) {
    const errorDiv = input.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.textContent = message;
    } else {
        const newErrorDiv = document.createElement('div');
        newErrorDiv.className = 'field-error';
        newErrorDiv.style.cssText = `
            color: #ff6b6b;
            font-size: 0.8rem;
            margin-top: 0.25rem;
            animation: slideIn 0.3s ease;
        `;
        newErrorDiv.textContent = message;
        input.parentNode.appendChild(newErrorDiv);
    }
}

function clearFieldError(input) {
    const errorDiv = input.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .error-message, .success-message {
        animation: slideIn 0.3s ease;
    }
`;
document.head.appendChild(style);

// Add floating labels effect
document.querySelectorAll('.form-group input').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentNode.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
        if (!this.value) {
            this.parentNode.classList.remove('focused');
        }
    });
    
    // Check if input has value on page load
    if (input.value) {
        input.parentNode.classList.add('focused');
    }
});

// Add smooth transitions for form interactions
document.querySelectorAll('input, button').forEach(element => {
    element.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-1px)';
    });
    
    element.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});
