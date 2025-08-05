// Main JavaScript file for Songs API frontend

class SongsAPI {
    constructor() {
        this.baseURL = '/api/songs/';
        this.init();
    }

    init() {
        // Add event listeners
        this.addEventListeners();
        
        // Initialize any components
        this.initializeComponents();
    }

    addEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add active class to current nav link
        this.updateActiveNavLink();
    }

    initializeComponents() {
        // Initialize any components that need setup
        console.log('Songs API frontend initialized');
    }

    updateActiveNavLink() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    // API methods
    async fetchSongs(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = `${this.baseURL}${queryString ? '?' + queryString : ''}`;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching songs:', error);
            throw error;
        }
    }

    async createSong(songData) {
        try {
            const response = await fetch(this.baseURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(songData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating song:', error);
            throw error;
        }
    }

    async updateSong(id, songData) {
        try {
            const response = await fetch(`${this.baseURL}${id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(songData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating song:', error);
            throw error;
        }
    }

    async deleteSong(id) {
        try {
            const response = await fetch(`${this.baseURL}${id}/`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return true;
        } catch (error) {
            console.error('Error deleting song:', error);
            throw error;
        }
    }

    async searchSongs(query) {
        try {
            const response = await fetch(`${this.baseURL}search/?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error searching songs:', error);
            throw error;
        }
    }

    async getTopRated(limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}top_rated/?limit=${limit}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching top rated songs:', error);
            throw error;
        }
    }

    async getMostPlayed(limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}most_played/?limit=${limit}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching most played songs:', error);
            throw error;
        }
    }

    async playSong(id) {
        try {
            const response = await fetch(`${this.baseURL}${id}/play/`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error playing song:', error);
            throw error;
        }
    }

    // Utility methods
    showMessage(message, type = 'success') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        // Insert at the top of main content
        const main = document.querySelector('.main .container');
        if (main) {
            main.insertBefore(messageDiv, main.firstChild);
            
            // Remove message after 5 seconds
            setTimeout(() => {
                messageDiv.remove();
            }, 5000);
        }
    }

    showLoading(element) {
        element.innerHTML = '<div class="loading"></div>';
    }

    hideLoading(element, content) {
        element.innerHTML = content;
    }

    formatDuration(seconds) {
        if (!seconds) return 'Unknown';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    // Form validation
    validateSongForm(formData) {
        const errors = [];
        
        if (!formData.title || formData.title.trim() === '') {
            errors.push('Title is required');
        }
        
        if (!formData.artist || formData.artist.trim() === '') {
            errors.push('Artist is required');
        }
        
        if (formData.year) {
            const year = parseInt(formData.year);
            if (isNaN(year) || year < 1900 || year > new Date().getFullYear()) {
                errors.push('Year must be between 1900 and current year');
            }
        }
        
        if (formData.rating) {
            const rating = parseFloat(formData.rating);
            if (isNaN(rating) || rating < 0 || rating > 5) {
                errors.push('Rating must be between 0 and 5');
            }
        }
        
        return errors;
    }
}

// Initialize the API when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.songsAPI = new SongsAPI();
});

// Add some interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});

// Add CSS for ripple effect
const appStyle = document.createElement('style');
appStyle.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(appStyle); 