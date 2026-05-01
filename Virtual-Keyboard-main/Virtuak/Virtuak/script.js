// Form validation and interaction functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Login form handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (validateLoginForm(email, password)) {
                // Simulate login process
                showLoadingState(loginForm);
                setTimeout(() => {
                    showSuccessMessage('Login successful! Redirecting...');
                    setTimeout(() => {
                        window.location.href = 'index.html';
                    }, 1500);
                }, 2000);
            }
        });
    }
    
    // Register form handling
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const terms = document.querySelector('input[name="terms"]').checked;
            
            if (validateRegisterForm(firstName, lastName, email, password, confirmPassword, terms)) {
                // Simulate registration process
                showLoadingState(registerForm);
                setTimeout(() => {
                    showSuccessMessage('Account created successfully! Redirecting to login...');
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 1500);
                }, 2000);
            }
        });
    }
    
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
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
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
function validateLoginForm(email, password) {
    let isValid = true;
    
    if (!email || !isValidEmail(email)) {
        showError('Please enter a valid email address');
        isValid = false;
    }
    
    if (!password || password.length < 6) {
        showError('Password must be at least 6 characters long');
        isValid = false;
    }
    
    return isValid;
}

function validateRegisterForm(firstName, lastName, email, password, confirmPassword, terms) {
    let isValid = true;
    
    if (!firstName || firstName.trim().length < 2) {
        showError('First name must be at least 2 characters long');
        isValid = false;
    }
    
    if (!lastName || lastName.trim().length < 2) {
        showError('Last name must be at least 2 characters long');
        isValid = false;
    }
    
    if (!email || !isValidEmail(email)) {
        showError('Please enter a valid email address');
        isValid = false;
    }
    
    if (!password || password.length < 8) {
        showError('Password must be at least 8 characters long');
        isValid = false;
    }
    
    if (password !== confirmPassword) {
        showError('Passwords do not match');
        isValid = false;
    }
    
    if (!terms) {
        showError('Please agree to the Terms of Service and Privacy Policy');
        isValid = false;
    }
    
    return isValid;
}

function validateEmail(input) {
    const email = input.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        input.style.borderColor = '#ff6b6b';
        showFieldError(input, 'Please enter a valid email address');
    } else {
        input.style.borderColor = '#d4af37';
        clearFieldError(input);
    }
}



function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// UI feedback functions
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid #ff6b6b;
        color: #ff6b6b;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        animation: slideIn 0.3s ease;
    `;
    errorDiv.textContent = message;
    
    const form = document.querySelector('.auth-form');
    form.insertBefore(errorDiv, form.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

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

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.style.cssText = `
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid #4caf50;
        color: #4caf50;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        animation: slideIn 0.3s ease;
        text-align: center;
    `;
    successDiv.textContent = message;
    
    const form = document.querySelector('.auth-form');
    form.insertBefore(successDiv, form.firstChild);
}

function showLoadingState(form) {
    const submitBtn = form.querySelector('.btn-submit');
    const originalText = submitBtn.textContent;
    
    submitBtn.textContent = 'Processing...';
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';
    
    // Store original text to restore later
    submitBtn.dataset.originalText = originalText;
}

function hideLoadingState(form) {
    const submitBtn = form.querySelector('.btn-submit');
    submitBtn.textContent = submitBtn.dataset.originalText || 'Submit';
    submitBtn.disabled = false;
    submitBtn.style.opacity = '1';
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
