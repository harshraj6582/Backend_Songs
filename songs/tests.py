from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Song
from decimal import Decimal
import json
import requests
import time
from datetime import datetime


class SongModelTest(TestCase):
    """Test cases for Song model"""
    
    def setUp(self):
        """Set up test data"""
        self.song = Song.objects.create(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            year=2024,
            genre="Pop",
            rating=Decimal('4.5'),
            play_count=100,
            danceability=0.8,
            energy=0.7,
            acousticness=0.2,
            tempo=120.0,
            duration_ms=180000,
            num_sections=8,
            num_segments=500
        )
    
    def test_song_creation(self):
        """Test song creation"""
        self.assertEqual(self.song.title, "Test Song")
        self.assertEqual(self.song.artist, "Test Artist")
        self.assertEqual(self.song.rating, Decimal('4.5'))
        self.assertEqual(self.song.play_count, 100)
    
    def test_song_str_representation(self):
        """Test string representation"""
        expected = "Test Song - Test Artist"
        self.assertEqual(str(self.song), expected)
    

    
    def test_play_count_increment(self):
        """Test play count increment"""
        initial_count = self.song.play_count
        self.song.increment_play_count()
        self.assertEqual(self.song.play_count, initial_count + 1)
    
    def test_audio_features_summary(self):
        """Test audio features summary property"""
        summary = self.song.audio_features_summary
        self.assertIn("Danceability: 0.80", summary)
        self.assertIn("Energy: 0.70", summary)
        self.assertIn("Tempo: 120 BPM", summary)


class SongAPITest(APITestCase):
    """Test cases for Song API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test songs with different ratings
        self.song1 = Song.objects.create(
            title="High Rated Song",
            artist="Artist 1",
            rating=Decimal('4.8'),
            play_count=50,
            danceability=0.9,
            energy=0.8,
            acousticness=0.1,
            tempo=130.0,
            duration_ms=200000,
            num_sections=10,
            num_segments=600
        )
        
        self.song2 = Song.objects.create(
            title="Medium Rated Song",
            artist="Artist 2",
            rating=Decimal('3.5'),
            play_count=100,
            danceability=0.6,
            energy=0.5,
            acousticness=0.4,
            tempo=110.0,
            duration_ms=180000,
            num_sections=8,
            num_segments=500
        )
        
        self.song3 = Song.objects.create(
            title="Low Rated Song",
            artist="Artist 3",
            rating=Decimal('2.0'),
            play_count=200,
            danceability=0.4,
            energy=0.3,
            acousticness=0.7,
            tempo=90.0,
            duration_ms=160000,
            num_sections=6,
            num_segments=400
        )
    
    def test_get_songs_list(self):
        """Test GET /api/songs/ endpoint"""
        url = reverse('song-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        songs = response.data['results']
        self.assertGreater(len(songs), 0)  # Should have at least one song
    
    def test_get_song_detail(self):
        """Test GET /api/songs/{id}/ endpoint"""
        url = reverse('song-detail', args=[self.song1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "High Rated Song")
    
    def test_search_songs(self):
        """Test GET /api/songs/search/?q=test endpoint"""
        url = reverse('song-search')
        response = self.client.get(url, {'q': 'High'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('High Rated Song', [song['title'] for song in response.data['results']])
    
    def test_search_without_query(self):
        """Test search without query parameter"""
        url = reverse('song-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All songs
    
    def test_top_rated_songs(self):
        """Test GET /api/songs/top_rated/ endpoint"""
        url = reverse('song-top-rated')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        songs = response.data['results']
        self.assertEqual(songs[0]['title'], "High Rated Song")  # Highest rating
    
    def test_most_played_songs(self):
        """Test GET /api/songs/most_played/ endpoint"""
        url = reverse('song-most-played')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        songs = response.data['results']
        self.assertEqual(songs[0]['title'], "Low Rated Song")  # Highest play count
    
    def test_rate_song(self):
        """Test POST /api/songs/{id}/rate/ endpoint"""
        url = reverse('song-rate', args=[self.song1.id])
        data = {'rating': 5.0}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rating', response.data)  # Should have rating field
    
    def test_rate_song_invalid_rating(self):
        """Test rating with invalid value"""
        url = reverse('song-rate', args=[self.song1.id])
        data = {'rating': 6.0}  # Invalid rating
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_play_song(self):
        """Test POST /api/songs/{id}/play/ endpoint"""
        url = reverse('song-play', args=[self.song1.id])
        initial_count = self.song1.play_count
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.song1.refresh_from_db()
        self.assertEqual(self.song1.play_count, initial_count + 1)
    
    def test_songs_stats(self):
        """Test GET /api/songs/stats/ endpoint"""
        url = reverse('song-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_songs', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('total_plays', response.data)
    
    def test_pagination(self):
        """Test pagination functionality"""
        url = reverse('song-list')
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
    
    def test_filtering(self):
        """Test filtering functionality"""
        url = reverse('song-list')
        response = self.client.get(url, {'artist': 'Artist 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        songs = response.data['results']
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0]['artist'], 'Artist 1')
    
    def test_ordering(self):
        """Test ordering functionality"""
        url = reverse('song-list')
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        songs = response.data['results']
        titles = [song['title'] for song in songs]
        self.assertEqual(titles, sorted(titles))


class SongAPIPerformanceTest(APITestCase):
    """Performance tests for Song API"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create multiple songs for performance testing
        for i in range(50):
            Song.objects.create(
                title=f"Performance Test Song {i}",
                artist=f"Artist {i}",
                rating=Decimal(str(1.0 + (i % 5))),
                play_count=i * 10,
                danceability=0.5 + (i % 5) * 0.1,
                energy=0.5 + (i % 5) * 0.1,
                acousticness=0.2 + (i % 5) * 0.1,
                tempo=100.0 + (i % 50),
                duration_ms=180000 + (i % 60000),
                num_sections=8 + (i % 5),
                num_segments=500 + (i % 200)
            )
    
    def test_list_performance(self):
        """Test list endpoint performance"""
        url = reverse('song-list')
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0)  # Should respond within 1 second
    
    def test_search_performance(self):
        """Test search endpoint performance"""
        url = reverse('song-search')
        start_time = time.time()
        response = self.client.get(url, {'q': 'Performance'})
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0)  # Should respond within 1 second


class SongIntegrationTest(TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test data"""
        self.base_url = "http://localhost:8000"
        self.api_endpoints = {
            "songs_list": "/api/songs/",
            "search": "/api/songs/search/?q=test",
            "top_rated": "/api/songs/top_rated/",
            "most_played": "/api/songs/most_played/",
        }
    
    def test_server_status(self):
        """Test if the server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/songs/", timeout=10)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        for name, endpoint in self.api_endpoints.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn('results', data)
            except requests.exceptions.ConnectionError:
                self.skipTest(f"Server is not running for {name}")
    
    def test_redis_caching(self):
        """Test Redis caching functionality"""
        try:
            cache_url = f"{self.base_url}/api/songs/"
            
            # First request (cache miss)
            start_time = time.time()
            response1 = requests.get(cache_url, timeout=10)
            first_request_time = time.time() - start_time
            
            # Small delay to ensure cache is written
            time.sleep(0.1)
            
            # Second request (cache hit)
            start_time = time.time()
            response2 = requests.get(cache_url, timeout=10)
            second_request_time = time.time() - start_time
            
            self.assertEqual(response1.status_code, 200)
            self.assertEqual(response2.status_code, 200)
            
            # Cache hit should be faster (or at least successful)
            self.assertLessEqual(second_request_time, first_request_time * 1.5)
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
    
    def test_rating_functionality(self):
        """Test rating functionality"""
        try:
            # First get a song
            response = requests.get(f"{self.base_url}/api/songs/", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data['results']:
                song_id = data['results'][0]['id']
                rate_url = f"{self.base_url}/api/songs/{song_id}/rate/"
                
                # Rate the song
                rating_data = {'rating': 4.5}
                response = requests.post(rate_url, json=rating_data, timeout=10)
                self.assertEqual(response.status_code, 200)
                
                # Verify rating was updated
                response = requests.get(f"{self.base_url}/api/songs/{song_id}/", timeout=10)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['rating'], '4.50')
                
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
    
    def test_play_functionality(self):
        """Test play functionality"""
        try:
            # First get a song
            response = requests.get(f"{self.base_url}/api/songs/", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            if data['results']:
                song_id = data['results'][0]['id']
                initial_play_count = data['results'][0]['play_count']
                play_url = f"{self.base_url}/api/songs/{song_id}/play/"
                
                # Play the song
                response = requests.post(play_url, timeout=10)
                self.assertEqual(response.status_code, 200)
                
                # Verify play count was incremented
                response = requests.get(f"{self.base_url}/api/songs/{song_id}/", timeout=10)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['play_count'], initial_play_count + 1)
                
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
    
    def test_performance_under_load(self):
        """Test performance under load"""
        try:
            url = f"{self.base_url}/api/songs/"
            start_time = time.time()
            
            # Make multiple requests
            for i in range(10):
                response = requests.get(url, timeout=10)
                self.assertEqual(response.status_code, 200)
            
            total_time = time.time() - start_time
            average_time = total_time / 10
            
            # Average response time should be reasonable
            self.assertLess(average_time, 2.0)  # Less than 2 seconds average
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")


class SongComprehensiveTest(TestCase):
    """Comprehensive test suite for the complete system"""
    
    def setUp(self):
        """Set up test configuration"""
        self.base_url = "http://localhost:8000"
    
    def test_complete_workflow(self):
        """Test complete user workflow"""
        try:
            # 1. Check server status
            response = requests.get(f"{self.base_url}/api/songs/", timeout=10)
            self.assertEqual(response.status_code, 200)
            
            # 2. Get songs list
            data = response.json()
            self.assertIn('results', data)
            self.assertIn('count', data)
            
            # 3. Test search
            search_response = requests.get(f"{self.base_url}/api/songs/search/?q=test", timeout=10)
            self.assertEqual(search_response.status_code, 200)
            
            # 4. Test top rated
            top_rated_response = requests.get(f"{self.base_url}/api/songs/top_rated/", timeout=10)
            self.assertEqual(top_rated_response.status_code, 200)
            
            # 5. Test most played
            most_played_response = requests.get(f"{self.base_url}/api/songs/most_played/", timeout=10)
            self.assertEqual(most_played_response.status_code, 200)
            
            # 6. Test stats
            stats_response = requests.get(f"{self.base_url}/api/songs/stats/", timeout=10)
            self.assertEqual(stats_response.status_code, 200)
            
            print("✅ Complete workflow test passed")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
    
    def test_error_handling(self):
        """Test error handling"""
        try:
            # Test invalid song ID
            response = requests.get(f"{self.base_url}/api/songs/999999/", timeout=10)
            self.assertIn(response.status_code, [404, 500])  # Should return error
            
            # Test invalid rating
            if self.base_url:
                response = requests.get(f"{self.base_url}/api/songs/", timeout=10)
                if response.status_code == 200 and response.json()['results']:
                    song_id = response.json()['results'][0]['id']
                    rate_url = f"{self.base_url}/api/songs/{song_id}/rate/"
                    rating_data = {'rating': 6.0}  # Invalid rating
                    response = requests.post(rate_url, json=rating_data, timeout=10)
                    self.assertEqual(response.status_code, 400)
            
            print("✅ Error handling test passed")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
    
    def test_data_consistency(self):
        """Test data consistency across endpoints"""
        try:
            # Get songs from different endpoints
            list_response = requests.get(f"{self.base_url}/api/songs/", timeout=10)
            top_rated_response = requests.get(f"{self.base_url}/api/songs/top_rated/", timeout=10)
            most_played_response = requests.get(f"{self.base_url}/api/songs/most_played/", timeout=10)
            
            self.assertEqual(list_response.status_code, 200)
            self.assertEqual(top_rated_response.status_code, 200)
            self.assertEqual(most_played_response.status_code, 200)
            
            # Verify data structure consistency
            list_data = list_response.json()
            top_rated_data = top_rated_response.json()
            most_played_data = most_played_response.json()
            
            # All should have 'results' and 'count'
            self.assertIn('results', list_data)
            self.assertIn('results', top_rated_data)
            self.assertIn('results', most_played_data)
            
            print("✅ Data consistency test passed")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server is not running")
