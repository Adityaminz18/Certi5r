// Certificate Download App - Zenith Club (Tailwind Theme)
let currentEmail = '';
let currentRollNumber = '';

document.addEventListener('DOMContentLoaded', function() {
    // Step 1: Details Form
    const detailsForm = document.getElementById('detailsForm');
    
    // Handle details form submission
    detailsForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        
        if (!email) {
            showError('Please enter your university email');
            return;
        }
        
        // Validate email format
        if (!email.endsWith('@sushantuniversity.edu.in')) {
            showError('Please use your sushantuniversity.edu.in email address');
            return;
        }
        
        // Extract roll number from email
        const emailParts = email.split('@')[0].split('.');
        if (emailParts.length < 2) {
            showError('Email format should be: name.rollnumber@sushantuniversity.edu.in');
            return;
        }
        
        const rollNumber = emailParts[emailParts.length - 1];
        
        currentEmail = email;
        currentRollNumber = rollNumber;
        
        await sendOTP(email);
    });

    // Step 2: OTP Form
    const otpForm = document.getElementById('otpForm');
    otpForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const otp = document.getElementById('otp').value;
        
        if (!otp || otp.length !== 6) {
            showError('Please enter a valid 6-digit OTP');
            return;
        }
        
        await verifyOTP(currentEmail, otp);
    });

    // Auto-focus OTP input and format
    const otpInput = document.getElementById('otp');
    otpInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, ''); // Only digits
    });

    // Add visual feedback for form inputs
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.add('ring-2', 'ring-accent/60');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('ring-2', 'ring-accent/60');
        });
    });
});

async function sendOTP(email) {
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('email', email);
        
        const response = await fetch('/send-otp', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            showStep2();
            // Auto-focus OTP input
            setTimeout(() => {
                document.getElementById('otp').focus();
            }, 300);
        } else {
            showError(data.error || 'Failed to send OTP');
        }
    } catch (error) {
        hideLoading();
        showError('Network error. Please try again.');
    }
}

async function verifyOTP(email, otp) {
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('email', email);
        formData.append('otp', otp);
        
        const response = await fetch('/verify-otp', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (response.ok && data.success) {
            showStep3();
        } else {
            showError(data.error || 'Invalid OTP');
        }
    } catch (error) {
        hideLoading();
        showError('Network error. Please try again.');
    }
}

function previewCertificate() {
    const url = `/preview/${currentRollNumber}?email=${encodeURIComponent(currentEmail)}`;
    window.open(url, '_blank');
}

function downloadCertificate() {
    const url = `/download/${currentRollNumber}?email=${encodeURIComponent(currentEmail)}`;
    
    // Create a temporary anchor element to trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentRollNumber}_certificate.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // Show success feedback
    setTimeout(() => {
        showSuccessToast('Certificate downloaded successfully! 🎉');
    }, 1000);
}

function showStep1() {
    hideAllSteps();
    document.getElementById('step1').classList.remove('hidden');
    animateStep('step1');
}

function showStep2() {
    hideAllSteps();
    document.getElementById('step2').classList.remove('hidden');
    animateStep('step2');
}

function showStep3() {
    hideAllSteps();
    document.getElementById('step3').classList.remove('hidden');
    animateStep('step3');
}

function hideAllSteps() {
    const steps = ['step1', 'step2', 'step3', 'errorContainer', 'loadingContainer'];
    steps.forEach(stepId => {
        const element = document.getElementById(stepId);
        if (element) {
            element.classList.add('hidden');
        }
    });
}

function animateStep(stepId) {
    const element = document.getElementById(stepId);
    if (element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 50);
    }
}

function showError(message) {
    hideAllSteps();
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorContainer').classList.remove('hidden');
    animateStep('errorContainer');
}

function showSuccessToast(message) {
    // Create a toast notification
    const toast = document.createElement('div');
    toast.className = 'fixed top-20 right-6 bg-accent text-black px-6 py-3 rounded-lg font-semibold shadow-neon z-50 transform translate-x-full transition-transform duration-300';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

function showLoading() {
    hideAllSteps();
    document.getElementById('loadingContainer').classList.remove('hidden');
    animateStep('loadingContainer');
}

function hideLoading() {
    document.getElementById('loadingContainer').classList.add('hidden');
}

function hideError() {
    document.getElementById('errorContainer').classList.add('hidden');
    showStep1();
}

function goBack() {
    showStep1();
    // Clear OTP input
    document.getElementById('otp').value = '';
}

function startOver() {
    // Clear all form data
    document.getElementById('email').value = '';
    document.getElementById('otp').value = '';
    currentEmail = '';
    currentRollNumber = '';
    
    showStep1();
}

// Enhanced keyboard navigation
document.addEventListener('keydown', function(e) {
    // Enter key on OTP input auto-submits
    if (e.key === 'Enter' && document.activeElement.id === 'otp') {
        const otpForm = document.getElementById('otpForm');
        if (otpForm && !document.getElementById('step2').classList.contains('hidden')) {
            otpForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape key to go back or close error
    if (e.key === 'Escape') {
        if (!document.getElementById('errorContainer').classList.contains('hidden')) {
            hideError();
        } else if (!document.getElementById('step2').classList.contains('hidden')) {
            goBack();
        }
    }
});

// Auto-clear form validation styles
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', function() {
        this.classList.remove('border-red-500');
        if (this.validity.valid) {
            this.classList.add('border-accent');
        } else {
            this.classList.remove('border-accent');
        }
    });
});

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    showStep1();
});
