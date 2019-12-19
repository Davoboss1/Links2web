from django.db import models
from django.db.models import  F
from django.forms import ModelForm,widgets

# Create your models here.

class Slider(models.Model):
	Info = models.CharField(max_length=250)
	Image_url = models.URLField(null=True,blank=True)
	def __str__(self):
		return self.Info


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
	icon = models.URLField(help_text="Enter Image Link",default="http://")
	category = models.CharField(max_length=500)
	sub_categories = models.ManyToManyField(Sub_Categories,related_name="sub_categories")
	def __str__(self):
		return self.category

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
	Countries = models.ManyToManyField(Countries,null=True,blank=True)
	Number = models.IntegerField(null=True,blank=True)
	category = models.ForeignKey(Categories,related_name="websites",default=1,on_delete=models.CASCADE)
	Tags = models.ManyToManyField(Sub_Categories,related_name="Tags",null=True,blank=True)
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

