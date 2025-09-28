// Klickon Auth - Frontend Script

document.addEventListener('DOMContentLoaded', function() {
    // Form validation və UX enhancements
    
    // Password strength indicator and length limit
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        // Set max length attribute
        passwordInput.setAttribute('maxlength', '128');
        
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            
            // Check length limit
            if (password.length > 128) {
                this.value = password.substring(0, 128);
                showInputError(this, 'Şifrə maksimum 128 simvol ola bilər');
                return;
            } else {
                clearInputError(this);
            }
            
            const strength = getPasswordStrength(password);
            showPasswordStrength(strength);
        });
    }

    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !isValidEmail(this.value)) {
                showInputError(this, 'E-mail formatı düzgün deyil');
            } else {
                clearInputError(this);
            }
        });
    });

    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            } else {
                showLoading(this);
            }
        });
    });

    // Auto-hide messages after 5 seconds
    const message = document.querySelector('.message');
    if (message) {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    }
});

function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (password.match(/[a-z]/)) strength += 1;
    if (password.match(/[A-Z]/)) strength += 1;
    if (password.match(/[0-9]/)) strength += 1;
    if (password.match(/[^a-zA-Z0-9]/)) strength += 1;
    return strength;
}

function showPasswordStrength(strength) {
    // Remove existing strength indicator
    const existingIndicator = document.querySelector('.password-strength');
    if (existingIndicator) {
        existingIndicator.remove();
    }

    const passwordInput = document.getElementById('password');
    if (!passwordInput || !passwordInput.value) return;

    const indicator = document.createElement('div');
    indicator.className = 'password-strength';
    indicator.style.cssText = `
        margin-top: 5px;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    `;

    let message, color;
    switch (strength) {
        case 0:
        case 1:
            message = 'Çox zəif';
            color = '#dc3545';
            break;
        case 2:
            message = 'Zəif';
            color = '#ffc107';
            break;
        case 3:
            message = 'Orta';
            color = '#17a2b8';
            break;
        case 4:
            message = 'Güclü';
            color = '#28a745';
            break;
        case 5:
            message = 'Çox güclü';
            color = '#155724';
            break;
    }

    indicator.textContent = `Şifrə gücü: ${message}`;
    indicator.style.backgroundColor = color + '20';
    indicator.style.color = color;
    indicator.style.border = `1px solid ${color}40`;

    passwordInput.parentNode.appendChild(indicator);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showInputError(input, message) {
    clearInputError(input);
    
    input.classList.add('error');
    input.parentNode.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'input-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: #dc3545;
        font-size: 12px;
        margin-top: 4px;
        font-weight: 500;
    `;
    
    input.parentNode.appendChild(errorDiv);
}

function clearInputError(input) {
    input.classList.remove('error');
    input.parentNode.classList.remove('error');
    
    const existingError = input.parentNode.querySelector('.input-error');
    if (existingError) {
        existingError.remove();
    }
}

function validateForm(form) {
    let isValid = true;
    
    // Clear previous errors
    const inputs = form.querySelectorAll('input[required]');
    inputs.forEach(input => clearInputError(input));
    
    // Check required fields
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showInputError(input, 'Bu sahə mütləqdir');
            isValid = false;
        }
    });
    
    // Email validation
    const emailInput = form.querySelector('input[type="email"]');
    if (emailInput && emailInput.value && !isValidEmail(emailInput.value)) {
        showInputError(emailInput, 'E-mail formatı düzgün deyil');
        isValid = false;
    }
    
    // Password length check for registration
    const passwordInput = form.querySelector('#password');
    if (passwordInput) {
        if (passwordInput.value.length < 8) {
            showInputError(passwordInput, 'Şifrə ən az 8 simvol olmalıdır');
            isValid = false;
        } else if (passwordInput.value.length > 128) {
            showInputError(passwordInput, 'Şifrə maksimum 128 simvol ola bilər');
            isValid = false;
        }
    }
    
    return isValid;
}

function showLoading(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Gözləyin...';
        submitBtn.disabled = true;
        
        // Re-enable after 10 seconds (fallback)
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 10000);
    }
}

// Smooth scroll and animations
function addSmoothAnimations() {
    const boxes = document.querySelectorAll('.box');
    boxes.forEach((box, index) => {
        box.style.animationDelay = `${index * 0.1}s`;
    });
}

// Initialize animations
document.addEventListener('DOMContentLoaded', addSmoothAnimations);

// Auto-focus first input
window.addEventListener('load', function() {
    const firstInput = document.querySelector('input:not([type="hidden"])');
    if (firstInput) {
        firstInput.focus();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + R for register form focus
    if (e.altKey && e.key === 'r') {
        e.preventDefault();
        const registerInput = document.querySelector('.register-box input');
        if (registerInput) registerInput.focus();
    }
    
    // Alt + L for login form focus  
    if (e.altKey && e.key === 'l') {
        e.preventDefault();
        const loginInput = document.querySelector('.login-box input');
        if (loginInput) loginInput.focus();
    }
});

// Theme detection and handling
function detectTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark-theme');
    }
}

// Initialize theme detection
document.addEventListener('DOMContentLoaded', detectTheme);