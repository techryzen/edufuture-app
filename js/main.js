// Initialize AOS (Animate on Scroll)
AOS.init({
    duration: 1000,
    easing: 'ease-in-out',
    once: true,
    mirror: false
});

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if(mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
            mobileMenu.classList.add('hidden');
        }
    });

    // Animated Counters
    const counterElements = document.querySelectorAll('.counter-value');
    
    // Function to animate counters
    const animateCounters = () => {
        counterElements.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const duration = 2000; // 2 seconds
            const steps = 50;
            const stepValue = target / steps;
            let current = 0;
            
            const updateCounter = setInterval(() => {
                current += stepValue;
                if (current > target) {
                    counter.textContent = target;
                    clearInterval(updateCounter);
                } else {
                    counter.textContent = Math.ceil(current);
                }
            }, duration / steps);
        });
    };

    // Animate counters when they come into view
    const observeCounters = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                observeCounters.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        observeCounters.observe(statsSection);
    }

    // Fade Up Animation for elements
    const fadeElements = document.querySelectorAll('.fade-up');
    
    const observeFadeElements = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observeFadeElements.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    fadeElements.forEach(element => {
        observeFadeElements.observe(element);
    });

    // Smooth Scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Close mobile menu if open
                mobileMenu.classList.add('hidden');
                
                // Scroll to the target with a smooth animation
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Testimonial Carousel
    const testimonialContainer = document.querySelector('.testimonial-container');
    const testimonialItems = document.querySelectorAll('.testimonial-item');
    
    if (testimonialContainer && testimonialItems.length > 0) {
        let currentIndex = 0;
        
        // Set up initial state
        testimonialItems.forEach((item, index) => {
            item.style.transform = `translateX(${100 * (index - currentIndex)}%)`;
        });
        
        // Function to move to next testimonial
        function nextTestimonial() {
            currentIndex = (currentIndex + 1) % testimonialItems.length;
            updateTestimonialPosition();
        }
        
        // Function to move to previous testimonial
        function prevTestimonial() {
            currentIndex = (currentIndex - 1 + testimonialItems.length) % testimonialItems.length;
            updateTestimonialPosition();
        }
        
        // Update the position of all testimonials
        function updateTestimonialPosition() {
            testimonialItems.forEach((item, index) => {
                item.style.transition = 'transform 0.5s ease';
                item.style.transform = `translateX(${100 * (index - currentIndex)}%)`;
            });
        }
        
        // Create navigation buttons
        const prevButton = document.createElement('button');
        prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevButton.className = 'testimonial-prev absolute left-0 top-1/2 transform -translate-y-1/2 bg-white rounded-full p-3 shadow-md text-primary z-10 focus:outline-none';
        prevButton.addEventListener('click', prevTestimonial);
        
        const nextButton = document.createElement('button');
        nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextButton.className = 'testimonial-next absolute right-0 top-1/2 transform -translate-y-1/2 bg-white rounded-full p-3 shadow-md text-primary z-10 focus:outline-none';
        nextButton.addEventListener('click', nextTestimonial);
        
        testimonialContainer.appendChild(prevButton);
        testimonialContainer.appendChild(nextButton);
        
        // Auto-advance every 5 seconds
        setInterval(nextTestimonial, 5000);
    }

    // Form Validation
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            let isValid = true;
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const messageInput = document.getElementById('message');
            
            // Reset previous error messages
            document.querySelectorAll('.error-message').forEach(el => el.remove());
            
            // Validate name
            if (!nameInput.value.trim()) {
                displayError(nameInput, 'Please enter your name');
                isValid = false;
            }
            
            // Validate email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailInput.value.trim() || !emailRegex.test(emailInput.value)) {
                displayError(emailInput, 'Please enter a valid email');
                isValid = false;
            }
            
            // Validate message
            if (!messageInput.value.trim()) {
                displayError(messageInput, 'Please enter your message');
                isValid = false;
            }
            
            if (isValid) {
                // Here you would typically send the form data to a server
                // For now, we'll just show a success message
                const formContainer = contactForm.parentElement;
                formContainer.innerHTML = `
                    <div class="text-center py-12">
                        <div class="text-5xl text-green-500 mb-4">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <h3 class="text-2xl font-bold mb-2">Message Sent Successfully!</h3>
                        <p class="text-gray-600 mb-6">Thank you for reaching out. We'll get back to you shortly.</p>
                        <button type="button" class="btn-primary" onclick="location.reload()">Send Another Message</button>
                    </div>
                `;
            }
        });
        
        function displayError(inputElement, message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message text-red-500 text-sm mt-1';
            errorDiv.textContent = message;
            inputElement.parentElement.appendChild(errorDiv);
            inputElement.classList.add('border-red-500');
        }
    }

    // Newsletter Form
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = document.getElementById('newsletter-email');
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            // Reset previous states
            document.querySelectorAll('.newsletter-message').forEach(el => el.remove());
            emailInput.classList.remove('border-red-500', 'border-green-500');
            
            if (!emailInput.value.trim() || !emailRegex.test(emailInput.value)) {
                // Show error
                const errorDiv = document.createElement('div');
                errorDiv.className = 'newsletter-message text-red-500 text-sm mt-1';
                errorDiv.textContent = 'Please enter a valid email';
                newsletterForm.appendChild(errorDiv);
                emailInput.classList.add('border-red-500');
            } else {
                // Show success
                emailInput.value = '';
                const successDiv = document.createElement('div');
                successDiv.className = 'newsletter-message text-green-500 text-sm mt-1';
                successDiv.textContent = 'Thank you for subscribing!';
                newsletterForm.appendChild(successDiv);
                emailInput.classList.add('border-green-500');
            }
        });
    }

    // Parallax Effect
    window.addEventListener('scroll', function() {
        const scrollPosition = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.getAttribute('data-speed') || 0.5;
            element.style.transform = `translateY(${scrollPosition * speed}px)`;
        });
    });

    // Back to Top Button
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTopButton.className = 'fixed bottom-6 right-6 bg-primary text-white rounded-full p-3 shadow-lg opacity-0 transition-opacity duration-300 focus:outline-none';
    backToTopButton.id = 'back-to-top';
    document.body.appendChild(backToTopButton);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.remove('opacity-0');
            backToTopButton.classList.add('opacity-100');
        } else {
            backToTopButton.classList.remove('opacity-100');
            backToTopButton.classList.add('opacity-0');
        }
    });
    
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// Preloader
window.addEventListener('load', function() {
    const preloader = document.getElementById('preloader');
    if (preloader) {
        preloader.classList.add('fade-out');
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    }
}); 