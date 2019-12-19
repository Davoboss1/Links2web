from django.shortcuts import render,redirect
from django.contrib.auth.models import User,UserManager , Permission
from django.urls import reverse,reverse_lazy
from django.http import HttpResponse,JsonResponse,HttpRequest
from django.http.response import Http404
from .models import Websites,Slider, Categories,add_Websites, add_Categories
from rest_framework import viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer
from rest_framework.status import *
from Websites.serializers import json_serializers, categories_serializers
from django.views.generic import UpdateView,DeleteView
# Create your views here.
@api_view(['GET','POST'])
def home(request):
	print(request.method)
	if request.method == "GET":
		if request.GET.__contains__("search_all_result"):
			Category = Categories.objects.all()
			slider = Slider.objects.all()
			searched_categories = Categories.objects.filter(category__contains=request.GET.get("search_all_result"))
			searched_websites = Websites.objects.filter(website__contains=request.GET.get("search_all_result"))
			print(searched_websites.exists())
			return render(request,"home/search.html",{'category':Category,'slider':slider,'result':searched_categories,'result_websites':searched_websites})
		elif request.GET.__contains__("search_categories_result"):
			Category = Categories.objects.all()
			slider = Slider.objects.all()
			searched_categories = Categories.objects.filter(category__contains=request.GET.get("search_categories_result"))
			return render(request,"home/search.html",{'category':Category,'slider':slider,'result':searched_categories})
		elif request.GET.__contains__("search_website_result"):
			Category = Categories.objects.all()
			slider = Slider.objects.all()
			searched_websites = Websites.objects.filter(website__contains=request.GET.get("search_website_result"))
			
			
			return render(request,"home/search.html",{'category':Category,'slider':slider,'result_websites':searched_websites})
			
	template = "home/index.html"
	Category = Categories.objects.all()
	slider = Slider.objects.all()
	return render(request,template,{'category':Category,'slider':slider,})


def control_panel(request):
	
	context = {}
	return render(request,"home/control_panel.html",context)

def all_websites(request,**kwargs):
	categories = Categories.objects.all()
	queryset = Categories.objects.get(id=kwargs['pk'],category=kwargs['name'])
		
	
	if queryset.List_Type  == 'UL':
		template = 'home/all_websites.html'
		if 'sub_category' in kwargs.keys():
			context = {'websites':queryset.websites.all().filter(Tags__contains=[kwargs['sub_category']]),}
		else:
			context = {'websites':queryset.websites.all()}
	elif queryset.List_Type  == 'OL':
		template = 'home/all_websites_ordered.html'
		if 'sub_category' in kwargs.keys():
			context = {'websites':queryset.websites.order_by('Number').filter(Tags__contains=[kwargs['sub_category']]),}
		else:
			context = {'websites':queryset.websites.order_by('Number')}
	print(kwargs)
	context['Category_name'] = queryset.category
	context['category'] = categories
	return render(request,template,context)
				
def search(request):
	return render(request,"home/index.html",{'category':Category,'slider':slider,})	
				
def add_category(HttpRequest):
	print(dir(HttpRequest.user))
	for i in Permission.objects.all():
		print(i.name)
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can add categories")):
		form = add_Categories()
		if HttpRequest.method == "POST":
			form = add_Categories(HttpRequest.POST)
			if form.is_valid():
				form = form.save(commit=False)
				form.sub_categories = HttpRequest.POST.getlist('sub_categories')
				form.save()
				return
				redirect(reverse("add_category"))
		return render(HttpRequest,'home/category-form.html',{'form' : form })
	else:
		raise Http404()
	
	

def update_category_select(request):
	if request.user.has_perm(Permission.objects.get(name = "Can add categories")):
		return render(request,"home/update_select.html",{'name' : 'Select Categories to update' ,"category":Categories.objects.all(),})
	else:
		pass	
		
class update_category(UpdateView):
	
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can change categories")):
		model = Categories
		fields = ('__all__')
		template_name = "home/update_category.html"
		def get_success_url(self):
			return reverse('update_category')
		
		def form_valid(self,form):
			self.object = form.save(commit=False)
			self.object.sub_categories = self.request.POST.getlist('sub_categories')
			self.object.save()
			return super().form_valid(form)

def delete_category_select(request):
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can delete categories")):
		return render(request,"home/update_select.html",{'name' : 'Select Categories to delete',"category":Categories.objects.all(),})

class delete_category(DeleteView):
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can delete categories")):
		model = Categories
		template_name = 'home/delete.html'
		success_url = reverse_lazy('delete_category_select')

	
	

def add_websites(request):
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can add websites")):
		Category = Categories.objects.all()
		form = add_Websites()
		if request.method == 'POST':
			form = add_Websites(request.POST)
			if form.is_valid():		
				form = form.save(commit=False)
				inc = 0
				all_numbers = request.POST.getlist('Number')
				all_added_websites = request.POST.getlist('website')
				all_url = request.POST.getlist('url')
				while inc < len(all_added_websites):
					if all_numbers[inc].isdigit():
						form.Number = int(all_numbers[inc])
					else:
						form.Number = None
					form.website = all_added_websites[inc]
					form.url = all_url[inc]
					form.Tags = request.POST.getlist('Tags')
					form.category = Categories.objects.get(id = int(request.POST.get('category')))
					form.save()
					inc+=1
			else:
				return HttpResponse(form.errors.as_ul())
			print(request.POST)
		return render(request,"home/form.html",{'form':form,'Category' : Category,})

def update_websites_select(request):
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can change websites")):
		return render(request,"home/update_select.html",{'name' : 'Select Categories of websites to update',"category":Categories.objects.all(),})
	
class update_websites(UpdateView):
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can change websites")):
		model = Websites
		fields = ('__all__')
		template_name = "home/update_website.html"
		success_url = reverse_lazy('update_website')
	

		def get_queryset(self):
			print(self.kwargs)
			return Categories.objects.all()
		def get_success_url(self):
			return reverse('update_website')
		
		def form_valid(self,form):
			form_queryset = Categories.objects.get(pk=self.kwargs['pk'])
			print(self.request.POST)
			form_websites = form_queryset.websites.all()
			all_numbers = self.request.POST.getlist('Number')
			all_added_websites = self.request.POST.getlist('website')
			all_url = self.request.POST.getlist('url')
			inc = 0
			for websites_objects in form_websites:
				websites_form = Websites.objects.get(website=websites_objects.website)
				websites_form.delete()
				if all_numbers[inc].isdigit():
					print(True)
					websites_form.Number = int(all_numbers[inc])
				else:
					print(False)
					websites_form.Number = None
			
				websites_form.pk = all_added_websites[inc]
				websites_form.url = all_url[inc]
				websites_form.Tags = self.request.POST.getlist('Tags')
				websites_form.category = Categories.objects.get(id = int(self.request.POST.get('category')))
				
				websites_form.save()
				inc+=1
			print(self.request.POST)
			print("Saving.....")
		
	#	self.object.sub_categories = self.request.POST.getlist('sub_categories')

			return super().form_valid(form)
	
		def form_invalid(self,form):
			print(form.errors)
			print(self.request.POST)
			return super().form_invalid(form)
		
		
		extra_context = {'categories':Categories.objects.all()}
	
		
def delete_websites(request):
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can delete websites")):
		categories = Categories.objects.all()
		if request.method == "POST":
			website = Websites.objects.get(pk=request.POST.get('website'))
			website.delete()
		return render(request,'home/delete_websites.html',{'categories':categories})
	
	
class delete_website(DeleteView):
	if HttpRequest.user.has_perm(Permission.objects.get(name = "Can add websites")):
		model = Websites
		template_name = 'home/delete.html'
		success_url = reverse_lazy('home')



@api_view(['GET','POST'])
#@renderer_classes((TemplateHTMLRenderer,))
def Categories_and_websites(request):
	if request.method == 'GET':
		print(dir(request))
		print('User : ',request.data)
		Category = Categories.objects.all()
		serializer = categories_serializers(Category,many=True)
		return Response(serializer.data)
		

@api_view(['GET','POST'])
@renderer_classes((TemplateHTMLRenderer,))
def jsondata(request):
	
	if request.method == 'GET':
		website = Websites.objects.get(id=1)
		serializer = json_serializers(website,many=True)
		return Response(serializer.data,template_name="home/index.html")
		
		
	elif request.method == 'POST':
		serializer = json_serializers(data=request.data)
		if serializer.is_valid():
			print(type(request.data))
			print(request.data)
			serializer.save()
			print("New Object added")
			return JsonResponse(serializer.data,status=HTTP_201_CREATED)
		return JsonResponse(serializer.errors,status=HTTP_400_BAD_REQUEST)
	

@api_view(['GET','POST','PUT','DELETE'])
def json_data(request,id):
	try:
		website = Websites.objects.get(pk=id)
	except Websites.DoesNotExist:
		if request.method == 'POST':
			print("Posted")
			serializer = json_serializers(data=request.data)
			if serializer.is_valid():
				print(type(request.data))
				print(request.data)
				serializer.save()
				print("New Object added")
				return JsonResponse(serializer.data,status=HTTP_201_CREATED)
			
		
		return Response(HTTP_404_NOT_FOUND)
		
	if request.method == 'GET':
		print('Get')
		serializer = json_serializers(website)
		return Response(serializer.data)
		
	elif request.method == 'PUT':
		print("Posted")
		serializer = json_serializers(data=request.data)
		if serializer.is_valid():
			print(type(request.data))
			print(request.data)
			serializer.save()
			print("New Object added")
			return JsonResponse(serializer.data,status=HTTP_201_CREATED)
			
	elif request.method == 'POST':
		print("Posted")
		serializer = json_serializers(data=request.data)
		if serializer.is_valid():
			print(type(request.data))
			print(request.data)
			serializer.save()
			print("New Object added")
			return JsonResponse(serializer.data,status=HTTP_201_CREATED)
			
	elif request.method == 'DELETE':
			print("Delete")
			website.delete()
			return Response(status=HTTP_204_NO_CONTENT)
	return JsonResponse(serializer.errors,status=HTTP_400_BAD_REQUEST)
	
		
		
		
		
			
		
		
		