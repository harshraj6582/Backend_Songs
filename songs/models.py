from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Song(models.Model):
    # Basic song information
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2024)],
        blank=True, 
        null=True
    )
    genre = models.CharField(max_length=100, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    lyrics = models.TextField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        blank=True,
        null=True
    )
    play_count = models.PositiveIntegerField(default=0)
    
    # Audio analysis features
    danceability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="How suitable a track is for dancing (0.0 to 1.0)"
    )
    energy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="Energy is a measure from 0.0 to 1.0"
    )
    key = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(11)],
        blank=True,
        null=True,
        help_text="The key the track is in (0=C, 1=C#, etc.)"
    )
    loudness = models.FloatField(
        blank=True,
        null=True,
        help_text="The overall loudness of a track in decibels"
    )
    mode = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        blank=True,
        null=True,
        help_text="Mode indicates the modality (major or minor) of a track"
    )
    acousticness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="A confidence measure from 0.0 to 1.0 of whether the track is acoustic"
    )
    instrumentalness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="Predicts whether a track contains no vocals"
    )
    liveness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="Detects the presence of an audience in the recording"
    )
    valence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="A measure from 0.0 to 1.0 describing the musical positiveness"
    )
    tempo = models.FloatField(
        blank=True,
        null=True,
        help_text="The overall estimated tempo of a track in beats per minute (BPM)"
    )
    duration_ms = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The duration of the track in milliseconds"
    )
    time_signature = models.IntegerField(
        validators=[MinValueValidator(3), MaxValueValidator(7)],
        blank=True,
        null=True,
        help_text="An estimated time signature of 3/4, 4/4, 5/4, 6/4, 7/4"
    )
    num_bars = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of bars in the track"
    )
    num_sections = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of sections in the track"
    )
    num_segments = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of segments in the track"
    )
    song_class = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Classification of the song (e.g., 'rock', 'pop', 'jazz')"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['artist']),
            models.Index(fields=['genre']),
            models.Index(fields=['year']),
            models.Index(fields=['rating']),
            models.Index(fields=['danceability']),
            models.Index(fields=['energy']),
            models.Index(fields=['tempo']),
            models.Index(fields=['song_class']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    def increment_play_count(self):
        self.play_count += 1
        self.save(update_fields=['play_count'])
    
    @property
    def duration_seconds(self):
        """Return duration in seconds if available"""
        if self.duration:
            return self.duration.total_seconds()
        elif self.duration_ms:
            return self.duration_ms / 1000
        return None
    
    @property
    def audio_features_summary(self):
        """Return a summary of audio features"""
        features = []
        if self.danceability is not None:
            features.append(f"Danceability: {self.danceability:.2f}")
        if self.energy is not None:
            features.append(f"Energy: {self.energy:.2f}")
        if self.tempo is not None:
            features.append(f"Tempo: {self.tempo:.0f} BPM")
        if self.acousticness is not None:
            features.append(f"Acousticness: {self.acousticness:.2f}")
        return ", ".join(features) if features else "No audio features available"
