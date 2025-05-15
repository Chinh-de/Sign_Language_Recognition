from django.db import models

# Create your models here.
class Dictionary(models.Model):
    SUBSET_CHOICES = [
        ('train', 'Training'),
        ('val', 'Validation'),
        ('test', 'Testing'),
    ]

    gloss = models.CharField(max_length=255)
    videosrc = models.URLField(max_length=500) 
    subset = models.CharField(max_length=5, choices=SUBSET_CHOICES, default='train')

    def __str__(self):
        return f"{self.id} - {self.gloss}"
