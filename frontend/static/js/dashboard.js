/**
 * Songs API Professional Dashboard
 * Advanced JavaScript for interactive API testing and monitoring
 * WITH COMPREHENSIVE CONSOLE LOGGING FOR DEBUGGING
 */

// Global functions for HTML onclick handlers - defined first for immediate availability
function testSearch() {
    console.log('🔍 Global testSearch function called');
    if (typeof dashboard !== 'undefined' && dashboard) {
        dashboard.testSearch();
    } else {
        console.warn('⚠️ Dashboard not ready yet, retrying in 100ms...');
        setTimeout(() => testSearch(), 100);
    }
}

function testTopRated() {
    console.log('🏆 Global testTopRated function called');
    if (typeof dashboard !== 'undefined' && dashboard) {
        dashboard.testTopRated();
    } else {
        console.warn('⚠️ Dashboard not ready yet, retrying in 100ms...');
        setTimeout(() => testTopRated(), 100);
    }
}

function testMostPlayed() {
    console.log('🎧 Global testMostPlayed function called');
    if (typeof dashboard !== 'undefined' && dashboard) {
        dashboard.testMostPlayed();
    } else {
        console.warn('⚠️ Dashboard not ready yet, retrying in 100ms...');
        setTimeout(() => testMostPlayed(), 100);
    }
}

function testPlaySong() {
    console.log('▶️ Global testPlaySong function called');
    if (typeof dashboard !== 'undefined' && dashboard) {
        dashboard.testPlaySong();
    } else {
        console.warn('⚠️ Dashboard not ready yet, retrying in 100ms...');
        setTimeout(() => testPlaySong(), 100);
    }
}

function runLoadTest() {
    console.log('⚡ Global runLoadTest function called');
    if (typeof dashboard !== 'undefined' && dashboard) {
        dashboard.runLoadTest();
    } else {
        console.warn('⚠️ Dashboard not ready yet, retrying in 100ms...');
        setTimeout(() => runLoadTest(), 100);
    }
}

function analyzeResponseTimes() {
    console.log('📊 Global analyzeResponseTimes function called');
    if (typeof dashboard !== 'undefined' && dashboard) {
        dashboard.analyzeResponseTimes();
    } else {
        console.warn('⚠️ Dashboard not ready yet, retrying in 100ms...');
        setTimeout(() => analyzeResponseTimes(), 100);
    }
}

function switchTab(tabName) {
    console.log(`📑 Switching to tab: ${tabName}`);
    // Remove active class from all tabs and content
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    const targetTab = document.querySelector(`[onclick="switchTab('${tabName}')"]`);
    const targetContent = document.getElementById(tabName);
    
    if (targetTab) targetTab.classList.add('active');
    if (targetContent) targetContent.classList.add('active');
    
    console.log(`✅ Tab switched to: ${tabName}`);
}

class SongsAPIDashboard {
    constructor() {
        console.log('🎵 Initializing Songs API Dashboard...');
        this.baseURL = '/api/songs/';
        this.responseTimes = [];
        this.init();
    }

    init() {
        console.log('🚀 Starting dashboard initialization...');
        this.loadDashboardStats();
        this.loadSongsData();
        this.populateSongSelect();
        this.setupEventListeners();
        this.startAutoRefresh();
        console.log('✅ Dashboard initialization complete');
    }

    // Load dashboard statistics
    async loadDashboardStats() {
        console.log('📊 Loading dashboard statistics...');
        try {
            const startTime = performance.now();
            console.log(`🔗 Fetching stats from: ${this.baseURL}`);
            
            // Fetch all songs to calculate total plays
            const allSongs = await this.fetchAllSongs();
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            console.log(`📡 API Response Status: 200`);
            console.log(`⏱️ Response Time: ${responseTime.toFixed(2)}ms`);
            console.log(`📈 Received data: ${allSongs.length} songs`);
            
            this.updateStats(allSongs, responseTime);
        } catch (error) {
            console.error('❌ Error loading dashboard stats:', error);
        }
    }

    async fetchAllSongs() {
        console.log('🔗 Fetching all songs for statistics...');
        const allSongs = [];
        let nextPage = this.baseURL;
        
        while (nextPage) {
            try {
                const response = await fetch(nextPage);
                if (response.ok) {
                    const data = await response.json();
                    allSongs.push(...data.results);
                    nextPage = data.next;
                    console.log(`📄 Fetched page with ${data.results.length} songs, total so far: ${allSongs.length}`);
                } else {
                    console.error(`❌ Error fetching page: ${response.status}`);
                    break;
                }
            } catch (error) {
                console.error('❌ Error fetching songs:', error);
                break;
            }
        }
        
        console.log(`✅ Fetched all ${allSongs.length} songs`);
        return allSongs;
    }

    updateStats(allSongs, responseTime) {
        console.log('📊 Updating dashboard statistics...');
        
        // Update total songs
        const totalSongs = allSongs.length;
        console.log(`🎵 Total Songs: ${totalSongs}`);
        document.getElementById('total-songs').textContent = totalSongs;
        
        // Calculate average rating
        if (allSongs.length > 0) {
            const ratings = allSongs
                .filter(song => song.rating)
                .map(song => parseFloat(song.rating));
            
            const avgRating = ratings.length > 0 
                ? (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(2)
                : '0.00';
            
            console.log(`⭐ Average Rating: ${avgRating} (from ${ratings.length} songs)`);
            document.getElementById('avg-rating').textContent = avgRating;
            
            // Calculate total plays from all songs
            const totalPlays = allSongs
                .reduce((sum, song) => sum + (song.play_count || 0), 0);
            console.log(`🎧 Total Plays: ${totalPlays}`);
            document.getElementById('total-plays').textContent = totalPlays;
        }
        
        // Update response time
        console.log(`⚡ API Response Time: ${responseTime.toFixed(2)}ms`);
        document.getElementById('api-response-time').textContent = `${responseTime.toFixed(2)}ms`;
        
        console.log('✅ Dashboard statistics updated successfully');
    }

    // Load songs data for display
    async loadSongsData() {
        console.log('🎵 Loading songs data for display...');
        try {
            console.log('🔄 Fetching all songs data...');
            const [allSongs, topRated, mostPlayed] = await Promise.all([
                this.fetchSongs(),
                this.fetchTopRated(),
                this.fetchMostPlayed()
            ]);

            console.log('📊 Displaying songs data...');
            this.displaySongs(allSongs, 'songs-grid');
            this.displaySongs(topRated, 'top-rated-grid');
            this.displaySongs(mostPlayed, 'most-played-grid');
            
            console.log('✅ Songs data loaded and displayed successfully');
        } catch (error) {
            console.error('❌ Error loading songs data:', error);
        }
    }

    async fetchSongs() {
        console.log('🔗 Fetching all songs...');
        const response = await fetch(this.baseURL);
        const data = await response.json();
        console.log(`📈 All songs fetched: ${data.count || 0} songs`);
        return data;
    }

    async fetchTopRated() {
        console.log('🔗 Fetching top rated songs...');
        const response = await fetch(`${this.baseURL}top_rated/`);
        const data = await response.json();
        console.log(`🏆 Top rated songs fetched: ${data.count || 0} songs`);
        return data;
    }

    async fetchMostPlayed() {
        console.log('🔗 Fetching most played songs...');
        const response = await fetch(`${this.baseURL}most_played/`);
        const data = await response.json();
        console.log(`🎧 Most played songs fetched: ${data.count || 0} songs`);
        return data;
    }

    displaySongs(data, containerId) {
        console.log(`🎨 Displaying songs in container: ${containerId}`);
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`❌ Container not found: ${containerId}`);
            return;
        }

        container.innerHTML = '';
        
        if (data.results && data.results.length > 0) {
            console.log(`📝 Creating ${data.results.length} song cards...`);
            data.results.forEach((song, index) => {
                const songCard = this.createSongCard(song);
                container.appendChild(songCard);
                console.log(`✅ Song card ${index + 1} created: ${song.title}`);
            });
        } else {
            console.log('⚠️ No songs found to display');
            container.innerHTML = '<p class="no-data">No songs found</p>';
        }
        
        console.log(`✅ Songs displayed in ${containerId}`);
    }

    createSongCard(song) {
        console.log(`🎵 Creating song card for: ${song.title} - ${song.artist}`);
        
        const card = document.createElement('div');
        card.className = 'song-card';
        
        const rating = song.rating ? parseFloat(song.rating) : 0;
        const stars = this.generateStars(rating);
        
        card.innerHTML = `
            <div class="song-title">${song.title}</div>
            <div class="song-artist">${song.artist}</div>
            <div class="song-details">
                <span>${song.genre || 'Unknown Genre'}</span>
                <span>${song.year || 'Unknown Year'}</span>
                <span class="song-rating">
                    ${stars} ${rating.toFixed(1)}
                </span>
                <span>${song.play_count || 0} plays</span>
            </div>
            <div class="song-actions">
                <div class="rating-stars" data-song-id="${song.id}" data-current-rating="${rating}">
                    <span class="star" data-rating="1">☆</span>
                    <span class="star" data-rating="2">☆</span>
                    <span class="star" data-rating="3">☆</span>
                    <span class="star" data-rating="4">☆</span>
                    <span class="star" data-rating="5">☆</span>
                </div>
                <button class="btn-rate" onclick="dashboard.rateSong(${song.id})">Rate Song</button>
            </div>
        `;
        
        // Add audio features if available
        if (song.audio_features_summary) {
            const audioDiv = document.createElement('div');
            audioDiv.className = 'song-audio-features';
            audioDiv.innerHTML = `<small>${song.audio_features_summary}</small>`;
            card.appendChild(audioDiv);
            console.log(`🎵 Audio features added: ${song.audio_features_summary}`);
        }
        
        // Add event listeners for interactive rating stars
        this.addRatingStarListeners(card, song.id, rating);
        
        console.log(`✅ Song card created successfully for: ${song.title}`);
        return card;
    }

    generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        return '★'.repeat(fullStars) + 
               (hasHalfStar ? '☆' : '') + 
               '☆'.repeat(emptyStars);
    }

    addRatingStarListeners(card, songId, currentRating) {
        console.log(`⭐ Adding rating listeners for song ${songId} with current rating ${currentRating}`);
        
        const starsContainer = card.querySelector('.rating-stars');
        const stars = starsContainer.querySelectorAll('.star');
        
        // Set initial state based on current rating
        this.updateStarDisplay(stars, currentRating);
        
        // Add hover effects
        stars.forEach((star, index) => {
            const rating = index + 1;
            
            star.addEventListener('mouseenter', () => {
                console.log(`⭐ Hovering over star ${rating} for song ${songId}`);
                this.updateStarDisplay(stars, rating);
            });
            
            star.addEventListener('mouseleave', () => {
                console.log(`⭐ Leaving stars for song ${songId}, reverting to current rating ${currentRating}`);
                this.updateStarDisplay(stars, currentRating);
            });
            
            star.addEventListener('click', () => {
                console.log(`⭐ Clicked star ${rating} for song ${songId}`);
                this.rateSong(songId, rating);
            });
        });
    }

    updateStarDisplay(stars, rating) {
        stars.forEach((star, index) => {
            const starRating = index + 1;
            if (starRating <= rating) {
                star.textContent = '★';
                star.style.color = '#ffd700';
            } else {
                star.textContent = '☆';
                star.style.color = '#ccc';
            }
        });
    }

    async rateSong(songId, rating = null) {
        console.log(`⭐ Rating song ${songId} with rating ${rating}`);
        
        if (rating === null) {
            // If no rating provided, get it from the selected stars
            const starsContainer = document.querySelector(`[data-song-id="${songId}"]`);
            if (starsContainer) {
                const selectedStars = starsContainer.querySelectorAll('.star[style*="color: rgb(255, 215, 0)"]');
                rating = selectedStars.length;
            }
        }
        
        if (!rating || rating < 1 || rating > 5) {
            console.warn('⚠️ Invalid rating value');
            alert('Please select a rating between 1 and 5 stars');
            return;
        }
        
        try {
            console.log(`📡 Sending rating request for song ${songId} with rating ${rating}`);
            const response = await fetch(`${this.baseURL}${songId}/rate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ rating: rating })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log(`✅ Rating successful: ${result.message}`);
                alert(`Successfully rated "${result.song}" with ${rating} stars!`);
                
                // Update the display
                this.loadSongsData();
                this.loadDashboardStats();
            } else {
                const error = await response.json();
                console.error(`❌ Rating failed: ${error.error}`);
                alert(`Rating failed: ${error.error}`);
            }
        } catch (error) {
            console.error('❌ Error rating song:', error);
            alert('Error rating song. Please try again.');
        }
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Populate song select for play count testing
    async populateSongSelect() {
        console.log('🎵 Populating song select dropdown...');
        try {
            const response = await fetch(this.baseURL);
            const data = await response.json();
            
            const select = document.getElementById('play-song-select');
            if (!select) {
                console.error('❌ Play song select element not found');
                return;
            }
            
            select.innerHTML = '<option value="">Select a song...</option>';
            
            if (data.results) {
                console.log(`📝 Adding ${data.results.length} songs to select dropdown...`);
                data.results.forEach(song => {
                    const option = document.createElement('option');
                    option.value = song.id;
                    option.textContent = `${song.title} - ${song.artist}`;
                    select.appendChild(option);
                });
                console.log('✅ Song select dropdown populated successfully');
            }
        } catch (error) {
            console.error('❌ Error populating song select:', error);
        }
    }

    // API Testing Functions
    async testSearch() {
        console.log('🔍 Testing search functionality...');
        const query = document.getElementById('search-query').value;
        const statusEl = document.getElementById('search-status');
        const contentEl = document.getElementById('search-content');
        
        console.log(`🔍 Search query: "${query}"`);
        
        if (!query.trim()) {
            console.warn('⚠️ Empty search query');
            this.showError('Please enter a search term', contentEl);
            return;
        }

        statusEl.textContent = 'Loading...';
        statusEl.className = 'status loading';
        contentEl.textContent = 'Searching...';
        console.log('⏳ Starting search...');

        try {
            const startTime = performance.now();
            const response = await fetch(`${this.baseURL}search/?q=${encodeURIComponent(query)}`);
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            console.log(`📡 Search response status: ${response.status}`);
            console.log(`⏱️ Search response time: ${responseTime.toFixed(2)}ms`);
            
            const data = await response.json();
            console.log(`📊 Search results:`, data);
            
            statusEl.textContent = 'Success';
            statusEl.className = 'status success';
            contentEl.textContent = JSON.stringify(data, null, 2);
            
            this.recordResponseTime(responseTime);
            console.log('✅ Search test completed successfully');
        } catch (error) {
            console.error('❌ Search test error:', error);
            statusEl.textContent = 'Error';
            statusEl.className = 'status error';
            contentEl.textContent = `Error: ${error.message}`;
        }
    }

    async testTopRated() {
        console.log('🏆 Testing top rated functionality...');
        const statusEl = document.getElementById('top-rated-status');
        const contentEl = document.getElementById('top-rated-content');
        
        statusEl.textContent = 'Loading...';
        statusEl.className = 'status loading';
        contentEl.textContent = 'Fetching top rated songs...';
        console.log('⏳ Fetching top rated songs...');

        try {
            const startTime = performance.now();
            const response = await fetch(`${this.baseURL}top_rated/`);
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            console.log(`📡 Top rated response status: ${response.status}`);
            console.log(`⏱️ Top rated response time: ${responseTime.toFixed(2)}ms`);
            
            const data = await response.json();
            console.log(`📊 Top rated results:`, data);
            
            statusEl.textContent = 'Success';
            statusEl.className = 'status success';
            contentEl.textContent = JSON.stringify(data, null, 2);
            
            this.recordResponseTime(responseTime);
            console.log('✅ Top rated test completed successfully');
        } catch (error) {
            console.error('❌ Top rated test error:', error);
            statusEl.textContent = 'Error';
            statusEl.className = 'status error';
            contentEl.textContent = `Error: ${error.message}`;
        }
    }

    async testMostPlayed() {
        console.log('🎧 Testing most played functionality...');
        const statusEl = document.getElementById('most-played-status');
        const contentEl = document.getElementById('most-played-content');
        
        statusEl.textContent = 'Loading...';
        statusEl.className = 'status loading';
        contentEl.textContent = 'Fetching most played songs...';
        console.log('⏳ Fetching most played songs...');

        try {
            const startTime = performance.now();
            const response = await fetch(`${this.baseURL}most_played/`);
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            console.log(`📡 Most played response status: ${response.status}`);
            console.log(`⏱️ Most played response time: ${responseTime.toFixed(2)}ms`);
            
            const data = await response.json();
            console.log(`📊 Most played results:`, data);
            
            statusEl.textContent = 'Success';
            statusEl.className = 'status success';
            contentEl.textContent = JSON.stringify(data, null, 2);
            
            this.recordResponseTime(responseTime);
            console.log('✅ Most played test completed successfully');
        } catch (error) {
            console.error('❌ Most played test error:', error);
            statusEl.textContent = 'Error';
            statusEl.className = 'status error';
            contentEl.textContent = `Error: ${error.message}`;
        }
    }

    async testPlaySong() {
        console.log('▶️ Testing play song functionality...');
        const songId = document.getElementById('play-song-select').value;
        const statusEl = document.getElementById('play-status');
        const contentEl = document.getElementById('play-content');
        
        console.log(`🎵 Selected song ID: ${songId}`);
        
        if (!songId) {
            console.warn('⚠️ No song selected');
            this.showError('Please select a song', contentEl);
            return;
        }

        statusEl.textContent = 'Loading...';
        statusEl.className = 'status loading';
        contentEl.textContent = 'Incrementing play count...';
        console.log('⏳ Incrementing play count...');

        try {
            const startTime = performance.now();
            const response = await fetch(`${this.baseURL}${songId}/play/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            console.log(`📡 Play response status: ${response.status}`);
            console.log(`⏱️ Play response time: ${responseTime.toFixed(2)}ms`);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`📊 Play response data:`, data);
                statusEl.textContent = 'Success';
                statusEl.className = 'status success';
                contentEl.textContent = JSON.stringify(data, null, 2);
                
                // Refresh data
                console.log('🔄 Refreshing dashboard data...');
                this.loadDashboardStats();
                this.loadSongsData();
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.recordResponseTime(responseTime);
            console.log('✅ Play song test completed successfully');
        } catch (error) {
            console.error('❌ Play song test error:', error);
            statusEl.textContent = 'Error';
            statusEl.className = 'status error';
            contentEl.textContent = `Error: ${error.message}`;
        }
    }

    // Performance Testing Functions
    async runLoadTest() {
        console.log('⚡ Starting load test...');
        const requests = parseInt(document.getElementById('load-requests').value) || 10;
        const statusEl = document.getElementById('load-status');
        const contentEl = document.getElementById('load-content');
        
        console.log(`📊 Load test configuration: ${requests} requests`);
        
        statusEl.textContent = 'Running...';
        statusEl.className = 'status loading';
        contentEl.textContent = `Starting load test with ${requests} requests...`;

        const results = {
            totalRequests: requests,
            successfulRequests: 0,
            failedRequests: 0,
            responseTimes: [],
            startTime: Date.now()
        };

        console.log('🚀 Starting load test requests...');
        const promises = [];
        
        for (let i = 0; i < requests; i++) {
            promises.push(this.makeTestRequest(i + 1, results));
        }

        await Promise.all(promises);
        
        const endTime = Date.now();
        const totalTime = endTime - results.startTime;
        
        const avgResponseTime = results.responseTimes.length > 0 
            ? results.responseTimes.reduce((a, b) => a + b, 0) / results.responseTimes.length 
            : 0;
        
        const successRate = (results.successfulRequests / requests * 100).toFixed(2);
        
        console.log(`📊 Load test results:`, {
            totalRequests: results.totalRequests,
            successfulRequests: results.successfulRequests,
            failedRequests: results.failedRequests,
            successRate: `${successRate}%`,
            totalTime: `${totalTime}ms`,
            avgResponseTime: `${avgResponseTime.toFixed(2)}ms`
        });
        
        statusEl.textContent = 'Complete';
        statusEl.className = 'status success';
        
        contentEl.textContent = `Load Test Results:
Total Requests: ${results.totalRequests}
Successful: ${results.successfulRequests}
Failed: ${results.failedRequests}
Success Rate: ${successRate}%
Total Time: ${totalTime}ms
Average Response Time: ${avgResponseTime.toFixed(2)}ms
Min Response Time: ${Math.min(...results.responseTimes).toFixed(2)}ms
Max Response Time: ${Math.max(...results.responseTimes).toFixed(2)}ms`;
        
        console.log('✅ Load test completed successfully');
    }

    async makeTestRequest(requestNum, results) {
        try {
            const startTime = performance.now();
            const response = await fetch(this.baseURL);
            const endTime = performance.now();
            const responseTime = endTime - startTime;
            
            if (response.ok) {
                results.successfulRequests++;
                results.responseTimes.push(responseTime);
                console.log(`✅ Request ${requestNum}: Success (${responseTime.toFixed(2)}ms)`);
            } else {
                results.failedRequests++;
                console.log(`❌ Request ${requestNum}: Failed (${response.status})`);
            }
        } catch (error) {
            results.failedRequests++;
            console.log(`❌ Request ${requestNum}: Error - ${error.message}`);
        }
    }

    async analyzeResponseTimes() {
        console.log('📊 Starting response time analysis...');
        const statusEl = document.getElementById('response-status');
        const contentEl = document.getElementById('response-content');
        
        statusEl.textContent = 'Analyzing...';
        statusEl.className = 'status loading';
        contentEl.textContent = 'Testing response times for all endpoints...';

        const endpoints = [
            { name: 'Songs List', url: this.baseURL },
            { name: 'Search', url: `${this.baseURL}search/?q=test` },
            { name: 'Top Rated', url: `${this.baseURL}top_rated/` },
            { name: 'Most Played', url: `${this.baseURL}most_played/` }
        ];

        const results = [];

        for (const endpoint of endpoints) {
            try {
                const startTime = performance.now();
                const response = await fetch(endpoint.url);
                const endTime = performance.now();
                const responseTime = endTime - startTime;
                
                results.push({
                    endpoint: endpoint.name,
                    responseTime: responseTime,
                    status: response.status,
                    success: response.ok
                });
                
                console.log(`✅ ${endpoint.name}: ${responseTime.toFixed(2)}ms (${response.status})`);
            } catch (error) {
                results.push({
                    endpoint: endpoint.name,
                    responseTime: 0,
                    status: 'Error',
                    success: false,
                    error: error.message
                });
                console.log(`❌ ${endpoint.name}: Error - ${error.message}`);
            }
        }

        const avgResponseTime = results
            .filter(r => r.success)
            .reduce((sum, r) => sum + r.responseTime, 0) / results.filter(r => r.success).length;

        statusEl.textContent = 'Complete';
        statusEl.className = 'status success';
        
        contentEl.textContent = `Response Time Analysis:
${results.map(r => `${r.endpoint}: ${r.success ? r.responseTime.toFixed(2) + 'ms' : 'Failed'} (${r.status})`).join('\n')}

Average Response Time: ${avgResponseTime.toFixed(2)}ms
Fastest Endpoint: ${results.filter(r => r.success).sort((a, b) => a.responseTime - b.responseTime)[0]?.endpoint || 'N/A'}
Slowest Endpoint: ${results.filter(r => r.success).sort((a, b) => b.responseTime - a.responseTime)[0]?.endpoint || 'N/A'}`;
        
        console.log('✅ Response time analysis completed successfully');
    }

    // Utility Functions
    recordResponseTime(responseTime) {
        this.responseTimes.push(responseTime);
        if (this.responseTimes.length > 100) {
            this.responseTimes.shift();
        }
        console.log(`📊 Response time recorded: ${responseTime.toFixed(2)}ms`);
    }

    showError(message, element) {
        console.error(`❌ Error: ${message}`);
        element.textContent = `Error: ${message}`;
    }

    setupEventListeners() {
        console.log('🎧 Setting up event listeners...');
        
        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    console.log(`🎯 Scrolled to: ${this.getAttribute('href')}`);
                }
            });
        });

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const targetTab = this.textContent.toLowerCase().replace(' ', '-');
                switchTab(targetTab);
                console.log(`📑 Switched to tab: ${targetTab}`);
            });
        });
        
        console.log('✅ Event listeners setup complete');
    }

    startAutoRefresh() {
        console.log('🔄 Starting auto-refresh (30 second intervals)...');
        // Refresh dashboard stats every 30 seconds
        setInterval(() => {
            console.log('🔄 Auto-refreshing dashboard stats...');
            this.loadDashboardStats();
        }, 30000);
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌐 DOM loaded, initializing dashboard...');
    dashboard = new SongsAPIDashboard();
    
    // Add loading animation
    document.body.classList.add('loaded');
    
    // Add some nice animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                console.log(`🎨 Animation triggered for: ${entry.target.className}`);
            }
        });
    });
    
    document.querySelectorAll('.stat-card, .test-card, .endpoint-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    console.log('🎉 Dashboard initialization complete!');
});

// Add some CSS for loading animation
const dashboardStyle = document.createElement('style');
dashboardStyle.textContent = `
    body:not(.loaded) {
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    body.loaded {
        opacity: 1;
    }
    
    .no-data {
        text-align: center;
        color: #6b7280;
        font-style: italic;
        padding: 2rem;
    }
    
    .song-audio-features {
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: #f3f4f6;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #6b7280;
    }
`;
document.head.appendChild(dashboardStyle);

console.log('🎵 Songs API Dashboard JavaScript loaded successfully!'); 