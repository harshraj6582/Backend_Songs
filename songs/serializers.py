from rest_framework import serializers
from .models import Song


class SongSerializer(serializers.ModelSerializer):
    """Full song serializer with all fields including audio features"""
    audio_features_summary = serializers.ReadOnlyField()
    duration_seconds = serializers.ReadOnlyField()
    
    class Meta:
        model = Song
        fields = [
            'id', 'title', 'artist', 'album', 'year', 'genre', 
            'duration', 'lyrics', 'rating', 'play_count',
            'danceability', 'energy', 'key', 'loudness', 'mode',
            'acousticness', 'instrumentalness', 'liveness', 'valence',
            'tempo', 'duration_ms', 'time_signature', 'num_bars',
            'num_sections', 'num_segments', 'song_class',
            'audio_features_summary', 'duration_seconds',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SongCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new songs"""
    
    class Meta:
        model = Song
        fields = [
            'title', 'artist', 'album', 'year', 'genre', 
            'duration', 'lyrics', 'rating',
            'danceability', 'energy', 'key', 'loudness', 'mode',
            'acousticness', 'instrumentalness', 'liveness', 'valence',
            'tempo', 'duration_ms', 'time_signature', 'num_bars',
            'num_sections', 'num_segments', 'song_class'
        ]


class SongUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating songs"""
    
    class Meta:
        model = Song
        fields = [
            'title', 'artist', 'album', 'year', 'genre', 
            'duration', 'lyrics', 'rating',
            'danceability', 'energy', 'key', 'loudness', 'mode',
            'acousticness', 'instrumentalness', 'liveness', 'valence',
            'tempo', 'duration_ms', 'time_signature', 'num_bars',
            'num_sections', 'num_segments', 'song_class'
        ]


class SongListSerializer(serializers.ModelSerializer):
    """Limited serializer for list views with audio features"""
    audio_features_summary = serializers.ReadOnlyField()
    
    class Meta:
        model = Song
        fields = [
            'id', 'title', 'artist', 'album', 'year', 'genre', 
            'rating', 'play_count',
            'danceability', 'energy', 'tempo', 'acousticness',
            'audio_features_summary', 'created_at'
        ] 