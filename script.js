document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    // Smooth Scroll
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            target.scrollIntoView({ behavior: 'smooth' });
            navMenu.classList.remove('active');
        });
    });

    // Navbar Hide on Scroll
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        const currentScroll = window.pageYOffset;

        if (currentScroll > lastScroll && currentScroll > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        lastScroll = currentScroll;
    });

    // Scroll Animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0) rotateX(0)';
                }, index * 200);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.warm-glow, .section-title').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(50px)';
        observer.observe(el);
    });

    // Load next event for index.html
    if (document.getElementById('next-event-card')) {
        loadNextEvent();
    }

});

let eventsData = [];

// Load events from JSON file
async function loadEventsData() {
    try {
        const response = await fetch('events.json');
        eventsData = await response.json();
    } catch (error) {
        console.error('Error loading events data:', error);
        // Fallback to empty array if JSON fails to load
        eventsData = [];
    }
}

// Functions for events.html
function loadEvents(filter = 'all') {
    const container = document.getElementById('events-container');
    container.innerHTML = '';

    const filteredEvents = filter === 'all' ? eventsData : eventsData.filter(event => event.type === filter);

    filteredEvents.forEach(event => {
        const eventCard = document.createElement('div');
        eventCard.className = 'event-card';
        eventCard.innerHTML = `
            <img src="${event.image}" alt="${event.title}" class="event-image">
            <div class="event-content">
                <h3 class="event-title">${event.title}</h3>
                <p class="event-date"><i class="fas fa-calendar"></i> ${event.date}</p>
                <p class="event-location"><i class="fas fa-map-marker-alt"></i> ${event.location}</p>
                <p class="event-desc">${event.desc}</p>
                <button class="btn-details" data-id="${event.id}">Dettagli</button>
            </div>
        `;
        container.appendChild(eventCard);
    });

    // Add event listeners for details buttons
    document.querySelectorAll('.btn-details').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const eventId = parseInt(e.target.getAttribute('data-id'));
            showEventDetails(eventId);
        });
    });
}

function initFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');
            // Get filter type
            const filter = btn.getAttribute('data-filter');
            // Load events with filter
            loadEvents(filter);
        });
    });
}

function initModal() {
    const modal = document.getElementById('eventModal');
    const closeBtn = modal.querySelector('.close');

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function showEventDetails(eventId) {
    const event = eventsData.find(e => e.id === eventId);
    if (!event) return;

    const modal = document.getElementById('eventModal');
    const modalBody = document.getElementById('modal-body');

    modalBody.innerHTML = `
        <h2>${event.title}</h2>
        <img src="${event.image}" alt="${event.title}" style="width:100%; max-height:300px; object-fit:cover; border-radius:10px; margin:20px 0;">
        <p><strong>Data:</strong> ${event.date}</p>
        <p><strong>Luogo:</strong> ${event.location}</p>
        <p><strong>Descrizione:</strong> ${event.details}</p>
        ${event.map ? `<iframe src="${event.map}" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>` : ''}
        ${event.rsvp ? '<button class="btn-primary">Partecipa</button>' : ''}
    `;

    modal.style.display = 'block';
}

function initNavbar() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        hamburger.classList.toggle('active');
    });
}

// Membership Page Functions
function initMembershipPage() {
    // Tier selection buttons
    const tierButtons = document.querySelectorAll('.tier-btn');
    tierButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const tier = btn.getAttribute('data-tier');
            selectTier(tier);
        });
    });

    // Tier radio buttons in form
    const tierRadios = document.querySelectorAll('input[name="membershipTier"]');
    tierRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const tier = e.target.value;
            selectTier(tier);
        });
    });

    // Form submission
    const membershipForm = document.getElementById('membershipForm');
    if (membershipForm) {
        membershipForm.addEventListener('submit', handleFormSubmission);
    }

    // Initialize leveling system
    initLevelingSystem();
}

function selectTier(tier) {
    // Update tier buttons
    const tierButtons = document.querySelectorAll('.tier-btn');
    tierButtons.forEach(btn => {
        btn.classList.remove('selected');
        if (btn.getAttribute('data-tier') === tier) {
            btn.classList.add('selected');
        }
    });

    // Update tier cards
    const tierCards = document.querySelectorAll('.tier-card');
    tierCards.forEach(card => {
        card.classList.remove('selected');
        if (card.getAttribute('data-tier') === tier) {
            card.classList.add('selected');
        }
    });

    // Update form radio button
    const radio = document.querySelector(`input[name="membershipTier"][value="${tier}"]`);
    if (radio) {
        radio.checked = true;
    }
}

function handleFormSubmission(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Basic validation
    if (!data.membershipTier) {
        alert('Please select a membership tier.');
        return;
    }

    if (!data.fullName || !data.email || !data.password) {
        alert('Please fill in all required fields.');
        return;
    }

    if (!data.privacy) {
        alert('Please accept the Privacy Policy and Terms of Service.');
        return;
    }

    // Simulate form submission
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.textContent = 'Processing...';
    submitBtn.disabled = true;

    setTimeout(() => {
        alert('Thank you for joining TablHero! Your account has been created successfully.');
        submitBtn.textContent = 'Create Account & Join';
        submitBtn.disabled = false;
        e.target.reset();
    }, 2000);
}

function initLevelingSystem() {
    const milestones = document.querySelectorAll('.milestone');
    const progressFill = document.querySelector('.progress-fill');

    // Simulate current XP (you can replace this with actual user data)
    const currentXP = 1250; // Example: 1250 XP
    const maxXP = 7500; // Diamond level

    // Calculate progress percentage
    const progressPercent = (currentXP / maxXP) * 100;
    progressFill.style.width = `${progressPercent}%`;

    // Highlight current level
    milestones.forEach(milestone => {
        milestone.classList.remove('current');
        const xpRange = milestone.getAttribute('data-xp');
        const [minXP, maxXP] = xpRange.split('-').map(x => parseInt(x.replace(',', '')));

        if (currentXP >= minXP && currentXP <= maxXP) {
            milestone.classList.add('current');
        }
    });

    // Add click handlers for milestones
    milestones.forEach(milestone => {
        milestone.addEventListener('click', () => {
            const level = milestone.getAttribute('data-level');
            const xpRange = milestone.getAttribute('data-xp');
            alert(`${level.charAt(0).toUpperCase() + level.slice(1)} Level: ${xpRange} XP`);
        });
    });
}

// Function to load and display the next event on index.html
async function loadNextEvent() {
    try {
        const response = await fetch('events.json');
        const events = await response.json();
        const nextEvent = events[0]; // Take the first event as the next event

        const eventCard = document.getElementById('next-event-card');
        eventCard.innerHTML = `
            <img src="${nextEvent.image}" alt="${nextEvent.title}" class="event-image">
            <div class="event-content">
                <h3 class="event-title">${nextEvent.title}</h3>
                <p class="event-date"><i class="fas fa-calendar"></i> ${nextEvent.date}</p>
                <p class="event-location"><i class="fas fa-map-marker-alt"></i> ${nextEvent.location}</p>
                <p class="event-desc">${nextEvent.desc}</p>
                <p class="event-details">${nextEvent.details}</p>
                <div class="event-description-placeholder">
                    <p><strong>Descrizione aggiuntiva:</strong> Spazio riservato per aggiungere ulteriori dettagli sull'evento.</p>
                </div>
                ${nextEvent.rsvp ? '<a href="events.html" class="btn-primary" style="margin-top: 1rem; display: inline-block;">Partecipa</a>' : ''}
            </div>
        `;
    } catch (error) {
        console.error('Error loading next event:', error);
        const eventCard = document.getElementById('next-event-card');
        eventCard.innerHTML = '<p>Errore nel caricamento dell\'evento.</p>';
    }
}


