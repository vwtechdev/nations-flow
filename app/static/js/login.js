'use strict'

$(function() {
    console.log('Login.js loaded successfully');
    
    // Add login-page class to html and body
    $('html, body').addClass('login-page');
    
    // Hide sidebar on login page
    $('.sidebar').hide();
    
    // Get current year
    const year = new Date().getFullYear();
    
    // Auto-hide alert messages after 3 seconds
    $('.alert').delay(500).fadeOut(500);
    
    // Add copyright footer
    $('.login-card').append('<footer class="text-center py-3 mt-4"><p class="text-muted">Copyright © 2019-' + year + ' VWTech Dev</p></footer>');
    
    // Add smooth transitions to form elements
    $('.form-control').on('focus', function() {
        $(this).addClass('shadow-sm');
    }).on('blur', function() {
        $(this).removeClass('shadow-sm');
    });
    
    // Add loading state to submit button
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        
        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Entrando...');
        
        // Re-enable button after 5 seconds if form submission fails
        setTimeout(function() {
            submitBtn.prop('disabled', false);
            submitBtn.html(originalText);
        }, 5000);
    });
    
    // Add enter key support for form submission
    $('input').on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            $(this).closest('form').submit();
        }
    });
    
    // Initialize password toggle functionality
    initPasswordToggle();
    
    console.log('Login.js initialization completed');
});

// Password toggle function
function togglePassword() {
    console.log('togglePassword function called');
    const passwordInput = document.getElementById('id_password');
    const passwordIcon = document.getElementById('password-icon');
    
    if (!passwordInput || !passwordIcon) {
        console.error('Password input or icon not found');
        console.log('passwordInput:', passwordInput);
        console.log('passwordIcon:', passwordIcon);
        return;
    }
    
    console.log('Current password type:', passwordInput.type);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        passwordIcon.className = 'bi bi-eye-slash';
        passwordIcon.style.color = 'var(--primary-color)';
        passwordIcon.title = 'Ocultar senha';
        console.log('Password shown');
    } else {
        passwordInput.type = 'password';
        passwordIcon.className = 'bi bi-eye';
        passwordIcon.style.color = '#6c757d';
        passwordIcon.title = 'Mostrar senha';
        console.log('Password hidden');
    }
}

// Initialize password toggle
function initPasswordToggle() {
    console.log('Initializing password toggle');
    
    // Add click event to password toggle button
    $(document).on('click', '.password-toggle', function(e) {
        console.log('Password toggle button clicked');
        e.preventDefault();
        e.stopPropagation();
        togglePassword();
    });
    
    // Add hover effects for password toggle
    $(document).on('mouseenter', '.password-toggle', function() {
        $(this).css('background-color', 'rgba(103, 58, 183, 0.1)');
    }).on('mouseleave', '.password-toggle', function() {
        $(this).css('background-color', 'transparent');
    });
    
    // Add keyboard support (Space and Enter keys)
    $(document).on('keydown', '.password-toggle', function(e) {
        if (e.key === ' ' || e.key === 'Enter') {
            e.preventDefault();
            togglePassword();
        }
    });
    
    console.log('Password toggle initialized');
}