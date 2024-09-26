from django.db import models
from users.models import *

#model schema for interests
class Interests(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    sender = models.ForeignKey(User,related_name='sent_interests',on_delete=models.CASCADE)
    receiver = models.ForeignKey(User,related_name='received_interests',on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender} - {self.receiver} - {self.status} - {self.created_at} - {self.updated_at}"
    
    
    