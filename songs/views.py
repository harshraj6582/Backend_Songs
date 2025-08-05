from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Avg, Count
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
import logging
import hashlib
import json
import os
import random
from datetime import timedelta

from .models import Song
from .serializers import (
    SongSerializer, 
    SongCreateSerializer, 
    SongUpdateSerializer,
    SongListSerializer
)

logger = logging.getLogger(__name__)


class SongViewSet(viewsets.ModelViewSet):
    """ViewSet for Song model with CRUD operations"""
    
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['artist', 'genre', 'year', 'album']
    search_fields = ['title', 'artist', 'album', 'lyrics']
    ordering_fields = ['title', 'artist', 'year', 'rating', 'play_count', 'created_at']
    ordering = ['-rating', '-created_at']  # Sort by rating first, then by creation date
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return SongCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SongUpdateSerializer
        elif self.action == 'list':
            return SongListSerializer
        return SongSerializer
    
    def list(self, request, *args, **kwargs):
        """List songs with optional filtering and pagination"""
        try:
            # Create cache key based on request parameters
            cache_key = self._get_cache_key(request, 'list')
            
            # Try to get from cache first
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.info(f"Cache HIT for songs list: {cache_key}")
                return Response(cached_response)
            
            logger.info(f"Cache MISS for songs list: {cache_key}")
            
            # Get data from database
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data = self.get_paginated_response(serializer.data).data
            else:
                serializer = self.get_serializer(queryset, many=True)
                response_data = serializer.data
            
            # Cache the response for 5 minutes
            cache.set(cache_key, response_data, 300)
            logger.info(f"Cached songs list response: {cache_key}")
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error in list view: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching songs'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_cache_key(self, request, action):
        """Generate cache key based on request parameters"""
        # Get all query parameters
        params = dict(request.GET.items())
        # Add action to make keys unique
        params['action'] = action
        # Create a hash of the parameters
        param_string = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()
        return f"songs_{action}_{param_hash}"
    
    def create(self, request, *args, **kwargs):
        """Create a new song"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            song = serializer.save()
            logger.info(f"Created new song: {song.title} - {song.artist}")
            
            # Clear related caches
            self._clear_related_caches()
            
            return Response(
                SongSerializer(song).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating song: {str(e)}")
            return Response(
                {'error': 'An error occurred while creating the song'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific song"""
        try:
            song = self.get_object()
            serializer = self.get_serializer(song)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving song: {str(e)}")
            return Response(
                {'error': 'An error occurred while retrieving the song'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Update a song"""
        try:
            song = self.get_object()
            serializer = self.get_serializer(song, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_song = serializer.save()
            logger.info(f"Updated song: {updated_song.title}")
            
            # Clear related caches
            self._clear_related_caches()
            
            return Response(SongSerializer(updated_song).data)
        except Exception as e:
            logger.error(f"Error updating song: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating the song'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a song"""
        try:
            song = self.get_object()
            song_title = song.title
            song.delete()
            logger.info(f"Deleted song: {song_title}")
            
            # Clear related caches
            self._clear_related_caches()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting song: {str(e)}")
            return Response(
                {'error': 'An error occurred while deleting the song'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search songs by title, artist, or album"""
        try:
            query = request.GET.get('q', '').strip()
            
            if not query:
                # If no query, return all songs
                queryset = self.get_queryset()
            else:
                # Search in title, artist, and album fields
                queryset = self.get_queryset().filter(
                    Q(title__icontains=query) |
                    Q(artist__icontains=query) |
                    Q(album__icontains=query)
                )
            
            # Apply pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return Response(
                {'error': 'An error occurred while searching'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Get top rated songs"""
        try:
            queryset = self.get_queryset().filter(rating__isnull=False).order_by('-rating')
            
            # Apply pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting top rated songs: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching top rated songs'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def most_played(self, request):
        """Get most played songs"""
        try:
            queryset = self.get_queryset().order_by('-play_count')
            
            # Apply pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting most played songs: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching most played songs'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get songs statistics"""
        try:
            total_songs = self.get_queryset().count()
            total_plays = self.get_queryset().aggregate(
                total_plays=Sum('play_count')
            )['total_plays'] or 0
            
            # Calculate average rating
            rated_songs = self.get_queryset().filter(rating__isnull=False)
            avg_rating = rated_songs.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
            
            # Get top genres
            top_genres = self.get_queryset().values('genre').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            stats = {
                'total_songs': total_songs,
                'total_plays': total_plays,
                'average_rating': round(float(avg_rating), 2) if avg_rating else 0,
                'top_genres': list(top_genres),
                'songs_with_ratings': rated_songs.count(),
                'songs_without_ratings': total_songs - rated_songs.count()
            }
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[])
    def play(self, request, pk=None):
        """Increment play count for a song"""
        try:
            song = self.get_object()
            song.increment_play_count()
            logger.info(f"Song played: {song.title} (new count: {song.play_count})")
            
            # Clear related caches
            self._clear_related_caches()
            
            return Response({
                'message': f'Play count incremented for {song.title}',
                'play_count': song.play_count
            })
        except Exception as e:
            logger.error(f"Error incrementing play count: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating play count'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[])
    def rate(self, request, pk=None):
        """Rate a song"""
        try:
            song = self.get_object()
            rating = request.data.get('rating')
            
            if rating is None:
                return Response(
                    {'error': 'Rating is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                rating = float(rating)
                if not (0.0 <= rating <= 5.0):
                    return Response(
                        {'error': 'Rating must be between 0.0 and 5.0'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid rating value'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            song.rating = rating
            song.save()
            
            logger.info(f"Song rated: {song.title} - {rating} stars")
            
            # Clear related caches
            self._clear_related_caches()
            
            return Response({
                'message': f'Rating updated for {song.title}',
                'rating': str(song.rating)
            })
        except Exception as e:
            logger.error(f"Error rating song: {str(e)}")
            return Response(
                {'error': 'An error occurred while rating the song'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def load_data(self, request):
        """Load playlist data from JSON file (Alternative to separate script)"""
        try:
            # Check if data already exists
            if Song.objects.exists():
                return Response({
                    'message': 'Data already loaded. Use force=true to reload.',
                    'existing_count': Song.objects.count()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get file path
            json_file = os.path.join(os.path.dirname(__file__), "..", "data", "playlist[76].json")
            
            if not os.path.exists(json_file):
                return Response({
                    'error': f'Data file not found: {json_file}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Load and process data
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            songs_created = 0
            song_count = len(data.get('id', {}))
            
            for i in range(song_count):
                try:
                    # Extract song data
                    song_id = data['id'].get(str(i), f"song_{i}")
                    title = data['title'].get(str(i), f"Song {i}")
                    
                    # Create song object
                    song = Song(
                        title=title,
                        artist=f"Artist {i+1}",
                        album=f"Album {i+1}",
                        year=2024,
                        genre="Pop",
                        duration=timedelta(seconds=int(data['duration_ms'].get(str(i), 0)) // 1000),
                        rating=random.randint(1, 5),
                        play_count=random.randint(1, 100),
                        
                        # Audio features
                        danceability=data['danceability'].get(str(i), 0.0),
                        energy=data['energy'].get(str(i), 0.0),
                        key=data['key'].get(str(i), 0),
                        loudness=data['loudness'].get(str(i), 0.0),
                        mode=data['mode'].get(str(i), 0),
                        acousticness=data['acousticness'].get(str(i), 0.0),
                        instrumentalness=data['instrumentalness'].get(str(i), 0.0),
                        liveness=data['liveness'].get(str(i), 0.0),
                        valence=data['valence'].get(str(i), 0.0),
                        tempo=data['tempo'].get(str(i), 0.0),
                        duration_ms=data['duration_ms'].get(str(i), 0),
                        time_signature=data['time_signature'].get(str(i), 4),
                        num_bars=data['num_bars'].get(str(i), 0),
                        num_sections=data['num_sections'].get(str(i), 0),
                        num_segments=data['num_segments'].get(str(i), 0),
                        song_class=data['class'].get(str(i), 1)
                    )
                    
                    song.save()
                    songs_created += 1
                    
                except Exception as e:
                    logger.error(f"Error creating song {i}: {str(e)}")
                    continue
            
            # Clear all caches
            cache.clear()
            
            return Response({
                'message': f'Successfully loaded {songs_created} songs',
                'songs_created': songs_created,
                'total_songs': song_count
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return Response({
                'error': 'An error occurred while loading data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _clear_related_caches(self):
        """Clear related caches when data changes"""
        try:
            # Clear list cache
            cache.delete_pattern('songs_list_*')
            # Clear search cache
            cache.delete_pattern('songs_search_*')
            # Clear stats cache
            cache.delete_pattern('songs_stats_*')
            logger.info("Cleared related caches")
        except Exception as e:
            logger.error(f"Error clearing caches: {str(e)}")
