from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255, help_text="Title of blog posting")
    body = models.TextField(blank=True, null=True)


class Author(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField(blank=True, null=True)


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.TextField(blank=True, null=True)
