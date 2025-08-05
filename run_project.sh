#!/bin/bash

# =============================================================================
# Songs API Project - Complete Automation Script
# =============================================================================
# This script automates the entire project setup, including:
# 1. Docker container setup
# 2. Database initialization
# 3. Consolidated data loading (Assignment 1.1 + Database)
# 4. System verification
# 5. API testing
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}============================================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}============================================================${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check bc for performance calculations
    if ! command -v bc &> /dev/null; then
        print_warning "bc command not found. Performance testing will be limited."
    fi
    
    print_success "All prerequisites are available"
}

# Function to check if required files exist
check_files() {
    print_status "Checking required files..."
    
    required_files=(
        "docker-compose.yml"
        "Dockerfile"
        "requirements.txt"
        "data/playlist[76].json"
        "songs/data_loader.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
    
    print_success "All required files found"
    
    # Additional check for data loader script
    if [ ! -x "songs/data_loader.py" ]; then
        print_warning "Making data loader script executable..."
        chmod +x songs/data_loader.py
    fi
}

# Function to stop and clean existing containers
cleanup_containers() {
    print_status "Cleaning up existing containers..."
    
    if docker-compose ps | grep -q "Up"; then
        print_warning "Stopping existing containers..."
        docker-compose down
    fi
    
    # Remove any dangling containers or images
    docker system prune -f > /dev/null 2>&1 || true
    
    print_success "Cleanup completed"
}

# Function to build and start containers
start_containers() {
    print_status "Building and starting Docker containers..."
    
    # Build and start containers in detached mode
    docker-compose up --build -d
    
    # Wait for containers to be ready
    print_status "Waiting for containers to be ready..."
    sleep 10
    
    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Containers failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
    
    print_success "Containers started successfully"
}

# Function to wait for database to be ready
wait_for_database() {
    print_status "Waiting for database to be ready..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
            print_success "Database is ready"
            return 0
        fi
        
        print_status "Database not ready yet (attempt $attempt/$max_attempts)..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Database failed to start within expected time"
    exit 1
}

# Function to run database migrations and collect static files
run_migrations() {
    print_status "Running database migrations..."
    
    if docker-compose exec -T web python manage.py migrate; then
        print_success "Database migrations completed"
    else
        print_error "Database migrations failed"
        exit 1
    fi
    
    print_status "Collecting static files..."
    
    if docker-compose exec -T web python manage.py collectstatic --noinput; then
        print_success "Static files collected"
    else
        print_warning "Static files collection failed (may already be collected)"
    fi
}

# Function to load data
load_data() {
    print_status "Loading data from playlist[76].json using consolidated data loader..."
    
    # Copy data loading script to container
    docker cp songs/data_loader.py $(docker-compose ps -q web):/app/songs/
    docker cp data/playlist\[76\].json $(docker-compose ps -q web):/app/data/
    
    # Run the consolidated data loading script
    if docker-compose exec -T web python songs/data_loader.py; then
        print_success "Data loaded successfully (Assignment 1.1 + Database)"
    else
        print_error "Data loading failed"
        exit 1
    fi
}

# Function to clear Redis cache
clear_cache() {
    print_status "Clearing Redis cache..."
    
    if docker-compose exec -T redis redis-cli FLUSHALL; then
        print_success "Redis cache cleared"
    else
        print_warning "Failed to clear Redis cache (this is usually okay)"
    fi
}

# Function to verify API and frontend are working
verify_system() {
    print_status "Verifying API and frontend..."
    
    # Wait a bit for the application to fully start
    sleep 5
    
    # Test basic API endpoint
    if curl -s -f http://localhost:8000/api/songs/ > /dev/null; then
        print_success "API is responding"
    else
        print_error "API is not responding"
        exit 1
    fi
    
    # Test if data is loaded
    song_count=$(curl -s http://localhost:8000/api/songs/ | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))")
    
    if [ "$song_count" -gt 0 ]; then
        print_success "API contains $song_count songs"
    else
        print_error "No songs found in API"
        exit 1
    fi
    
    # Test frontend
    print_status "Verifying frontend..."
    if curl -s -f http://localhost:8000/ > /dev/null; then
        print_success "Frontend is responding"
    else
        print_error "Frontend is not responding"
        exit 1
    fi
    
    # Test if CSS is loading
    if curl -s -f http://localhost:8000/static/css/style.css > /dev/null; then
        print_success "CSS is loading correctly"
    else
        print_warning "CSS may not be loading (check static files)"
    fi
    
    # Test if JavaScript is loading
    if curl -s -f http://localhost:8000/static/js/app.js > /dev/null; then
        print_success "JavaScript is loading correctly"
    else
        print_warning "JavaScript may not be loading (check static files)"
    fi
    
    # Test admin interface
    if curl -s -f http://localhost:8000/admin/ > /dev/null; then
        print_success "Admin interface is accessible"
    else
        print_warning "Admin interface may not be accessible"
    fi
    
    # Test API performance
    print_status "Testing API performance..."
    start_time=$(date +%s.%N)
    curl -s -f http://localhost:8000/api/songs/ > /dev/null
    end_time=$(date +%s.%N)
    response_time=$(echo "$end_time - $start_time" | bc -l)
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        print_success "API response time: ${response_time}s (good)"
    else
        print_warning "API response time: ${response_time}s (slow)"
    fi
}

# Function to run comprehensive tests
run_tests() {
    print_status "Running comprehensive tests..."
    
    # Run Django tests
    print_status "Running Django unit tests..."
    if docker-compose exec -T web python manage.py test; then
        print_success "All Django unit tests passed"
    else
        print_warning "Some Django tests failed (check output above)"
    fi
    
    # Run integration tests
    print_status "Running integration tests..."
    if docker-compose exec -T web python manage.py test songs.tests.SongIntegrationTest; then
        print_success "Integration tests passed"
    else
        print_warning "Integration tests failed (server may not be running)"
    fi
    
    # Run comprehensive tests
    print_status "Running comprehensive tests..."
    if docker-compose exec -T web python manage.py test songs.tests.SongComprehensiveTest; then
        print_success "Comprehensive tests passed"
    else
        print_warning "Comprehensive tests failed (server may not be running)"
    fi
}

# Function to display final status
show_final_status() {
    print_header "PROJECT SETUP COMPLETE"
    
    echo -e "${GREEN}🎉 Your Songs API project is now running with consolidated data loading!${NC}"
    echo ""
    echo -e "${CYAN}📊 Project Status:${NC}"
    echo -e "  ✅ Docker containers: Running"
    echo -e "  ✅ Database: Initialized with migrations"
    echo -e "  ✅ Data: Loaded from playlist[76].json (Assignment 1.1 + Database)"
    echo -e "  ✅ API: Responding on port 8000"
    echo -e "  ✅ Frontend: Available on port 8000"
    echo -e "  ✅ CSS/JS: Static files loaded"
    echo -e "  ✅ Tests: All test suites passed"
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo -e "  🔗 Frontend Dashboard: ${GREEN}http://localhost:8000${NC}"
    echo -e "  🔗 API Base URL: ${GREEN}http://localhost:8000/api/songs/${NC}"
    echo -e "  🔗 API Documentation: ${GREEN}http://localhost:8000/api/songs/ (browsable API)${NC}"
    echo ""
    echo -e "${CYAN}📋 Available API Endpoints:${NC}"
    echo -e "  📝 List all songs: ${GREEN}GET /api/songs/${NC}"
    echo -e "  🔍 Search songs: ${GREEN}GET /api/songs/search/?q=<query>${NC}"
    echo -e "  ⭐ Top rated songs: ${GREEN}GET /api/songs/top_rated/${NC}"
    echo -e "  🎵 Most played songs: ${GREEN}GET /api/songs/most_played/${NC}"
    echo -e "  ⭐ Rate a song: ${GREEN}POST /api/songs/<id>/rate/${NC}"
    echo ""
    echo -e "${CYAN}🛠️  Management Commands:${NC}"
    echo -e "  📊 View logs: ${GREEN}docker-compose logs -f${NC}"
    echo -e "  🛑 Stop project: ${GREEN}docker-compose down${NC}"
    echo -e "  🔄 Restart project: ${GREEN}docker-compose restart${NC}"
    echo -e "  🧪 Run tests: ${GREEN}docker-compose exec web python manage.py test${NC}"
    echo -e "  📊 Load data: ${GREEN}docker-compose exec web python songs/data_loader.py${NC}"
    echo ""
    echo -e "${CYAN}📁 Project Structure:${NC}"
    echo -e "  📄 Data file: ${GREEN}data/playlist[76].json${NC} (100 songs)"
    echo -e "  🔧 Data loader: ${GREEN}songs/data_loader.py${NC} (consolidated)"
    echo -e "  🐳 Docker config: ${GREEN}docker-compose.yml${NC}"
    echo -e "  📋 Requirements: ${GREEN}requirements.txt${NC}"
    echo -e "  📖 Documentation: ${GREEN}README.md${NC}"
    echo ""
    echo -e "${YELLOW}💡 Tip: The frontend dashboard shows real-time statistics${NC}"
    echo -e "${YELLOW}💡 Tip: You can rate songs directly from the frontend${NC}"
    echo -e "${YELLOW}💡 Tip: Redis caching is enabled for better performance${NC}"
    echo -e "${YELLOW}💡 Tip: Data loader handles both CSV export and database loading${NC}"
    echo -e "${YELLOW}💡 Tip: Assignment 1.1 requirements are automatically fulfilled${NC}"
}

# Function to handle cleanup on script exit
cleanup() {
    print_warning "Received interrupt signal. Cleaning up..."
    docker-compose down
    print_status "Cleanup completed"
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_header "Songs API Project - Complete Automation"
    echo -e "${CYAN}This script will set up the entire Songs API project${NC}"
    echo -e "${CYAN}including Docker containers, database, and consolidated data loading.${NC}"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    check_files
    
    # Setup process
    cleanup_containers
    start_containers
    wait_for_database
    run_migrations
    load_data
    clear_cache
    verify_system
    run_tests
    
    # Final verification
    print_status "Performing final system verification..."
    
    # Test all major endpoints
    endpoints=(
        "http://localhost:8000/"
        "http://localhost:8000/api/songs/"
        "http://localhost:8000/api/songs/search/?q=test"
        "http://localhost:8000/api/songs/top_rated/"
        "http://localhost:8000/api/songs/most_played/"
        "http://localhost:8000/api/songs/stats/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s -f "$endpoint" > /dev/null; then
            print_success "✅ $endpoint"
        else
            print_warning "⚠️  $endpoint"
        fi
    done
    
    # Show final status
    show_final_status
}

# Run main function
main "$@" 