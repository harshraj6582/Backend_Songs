from django.contrib import admin
from .models import Song


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    """Admin interface for Song model"""
    
    list_display = [
        'title', 'artist', 'album', 'year', 'genre', 
        'rating', 'play_count', 'tempo', 'danceability', 'energy'
    ]
    list_filter = [
        'genre', 'year', 'song_class', 'mode', 'rating'
    ]
    search_fields = ['title', 'artist', 'album', 'lyrics']
    readonly_fields = ['created_at', 'updated_at', 'audio_features_summary']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'album', 'year', 'genre', 'lyrics')
        }),
        ('Audio Analysis Features', {
            'fields': (
                'danceability', 'energy', 'key', 'loudness', 'mode',
                'acousticness', 'instrumentalness', 'liveness', 'valence',
                'tempo', 'duration_ms', 'time_signature'
            ),
            'classes': ('collapse',)
        }),
        ('Advanced Audio Features', {
            'fields': ('num_bars', 'num_sections', 'num_segments', 'song_class'),
            'classes': ('collapse',)
        }),
        ('Playback & Rating', {
            'fields': ('duration', 'rating', 'play_count')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'audio_features_summary'),
            'classes': ('collapse',)
        }),
    )
    
    def audio_features_summary(self, obj):
        """Display audio features summary in admin"""
        return obj.audio_features_summary
    audio_features_summary.short_description = 'Audio Features Summary'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related()
