from django.db import models
from django.db.models import  F
from django.forms import ModelForm,widgets
import sys
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

#Image compressor
def compressImage(image_field,width,height):
        imageTemproary = Image.open(image_field)
        outputIoStream = BytesIO()
        imageTemproaryResized = imageTemproary.resize( (width,height) ) 
        imageTemproary.save(outputIoStream,format="JPEG")
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" % image_field.name.split('.')[0], 'image/png', sys.getsizeof(outputIoStream), None)
        return uploadedImage

# Create your models here.

class Slider(models.Model):
	Info = models.CharField(max_length=250)
	Image = models.ImageField(upload_to="slider",null=True,blank=True)
	def __str__(self):
		return self.Info
	def save(self, *args, **kwargs):
		if not self.pk:
			self.Image = compressImage(self.Image,500,400)
		super(Slider, self).save(*args, **kwargs)

class Sub_Categories(models.Model):
	Category = models.CharField(max_length=100)
	Sub_Category = models.CharField(max_length=100)
	def __str__(self):
		return self.Sub_Category

class Categories(models.Model):

	LIST_CHOICES = (
	('OL','Numbered List'),
	('UL','List')
	)

	List_Type = models.CharField(max_length=2,choices=LIST_CHOICES,default='UL')
	icon = models.ImageField(help_text="Select image to upload",upload_to = 'categories',null=True,blank=True)
	category = models.CharField(max_length=500)
	sub_categories = models.ManyToManyField(Sub_Categories,related_name="categories")
	def __str__(self):
		return self.category
	def save(self, *args, **kwargs):
		if not self.pk:
			self.icon = compressImage(self.icon,50,50)
		super(Categories, self).save(*args, **kwargs)

	class Meta:
		ordering = ['category']


class add_Categories(ModelForm):
	class Meta:
		model = Categories
		fields = ('__all__')
		exclude = ('sub_categories',)


class Countries(models.Model):
	Country_code = models.CharField(max_length=2)
	Country_name = models.CharField(max_length=50)
	def __str__(self):
		return "{} : {}".format(self.Country_code,self.Country_name)
class Websites(models.Model):
	Countries = models.ManyToManyField(Countries,blank=True)
	Number = models.IntegerField(null=True,blank=True)
	category = models.ForeignKey(Categories,related_name="websites",default=1,on_delete=models.CASCADE)
	Tags = models.ManyToManyField(Sub_Categories,related_name="Tags",blank=True)
	url = models.URLField(default="http://")
	website =models.CharField(max_length=250,default="None")
	def __str__(self):
		if self.website != None:
			return str(self.category) +" " + str(self.Number) + ". " + self.website
		else:
			return self.website

	class Meta:
		ordering = [F('category').asc(nulls_last=True),'category',F('Number').asc(nulls_last=True)]

class add_Websites(ModelForm):
	class Meta:
		model = Websites
		fields = ('__all__')
		widgets = {'category':widgets.Select(attrs={'class':'form-control'}),'Countries':widgets.SelectMultiple(attrs={'class':'form-control w-75','id':'countriesSelect'}),}

