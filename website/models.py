from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
class Horoscope(models.Model):
    name = models.CharField('Name', max_length=40, unique=True)
    slug = models.SlugField(unique=True)
    description = RichTextField(blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.name

    class Meta:
        """docstring for meta"""
        ordering = ('id',)
        verbose_name_plural = "Horoscope Management"




class PageContent(models.Model):
    name = models.CharField('Name', max_length=40, unique=True)
    slug = models.SlugField(unique=True)
    description = RichTextField(blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.name

    class Meta:
        """docstring for meta"""
        ordering = ('id',)
        verbose_name_plural = "Content Management"


class HomeAbout(models.Model):
    title = models.CharField('Title', max_length=40, unique=True)
    image = models.ImageField(upload_to='',blank=True)
    description = RichTextField(blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.title

    class Meta:
        """docstring for meta"""
        ordering = ('id',)
        verbose_name_plural = "Home About Content"       



class HomePageService(models.Model):
    title = models.CharField('Title', max_length=40, unique=True)
    image = models.ImageField(upload_to='',blank=True)
    description = RichTextField(blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.title

    class Meta:
        """docstring for meta"""
        ordering = ('id',)
        verbose_name_plural = "Home Service Management"        


class Testimonials(models.Model):
    name = models.CharField('Name', max_length=40, unique=True)
    designation = models.CharField('Designation', max_length=40, unique=True)
    image = models.ImageField(upload_to='',blank=True)
    description = RichTextField(blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.name

    class Meta:
        """docstring for meta"""
        ordering = ('id',)
        verbose_name_plural = "Testimonials Management"              


class UsStock(models.Model):
    name = models.CharField('Name', max_length=40, unique=True)
    #slug = models.SlugField(unique=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        :return: the Category name
        """
        return self.name

    class Meta:
        """docstring for meta"""
        ordering = ('id',)
        verbose_name_plural = "US Stock"