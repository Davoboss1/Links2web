from django.shortcuts import render,redirect
from django.core.mail import send_mail,BadHeaderError
from django.db.models import F
from django.contrib.auth.models import User,UserManager , Permission
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger,Page
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse,reverse_lazy
from django.template import loader
from django.http import HttpResponse,JsonResponse,HttpRequest
from django.http.response import Http404
from .models import Websites,Slider, Categories,add_Websites, add_Categories,Countries,Sub_Categories
from rest_framework import viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer
from rest_framework.status import *
from Websites.serializers import json_serializers, categories_serializers,Slider_serializers
from django.views.generic import UpdateView,DeleteView
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def permission(permission_name):
	def function(func):
		 def permission_request(request):

		 	if request.user.has_perm(permission_name):
		 		return func(request)
		 	else:
		 		raise Http404
		 return permission_request
	return function

def permission_generic(permission_name):
	def function(func):
		 def permission_request(self,request,*args,**kwargs):
		 	if request.user.has_perm(permission_name):
		 		return func(self,request,*args,**kwargs)
		 	else:
		 		raise Http404
		 return permission_request
	return function



def visitor_ip_address(request):
	x_forwarded_for = request.META.get('REMOTE_ADDR')
	real_ip = request.META.get('HTTP_X_REAL_IP')
	if real_ip:
		ip = real_ip
	elif x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def visitors_location(ip):
	geoip = GeoIP2()
	user_country = geoip.country(ip)
	if user_country["country_code"] is None:
		user_country["country_code"] = "OT"
	try:
		country = Countries.objects.get(Country_code=user_country['country_code'],Country_name=user_country['country_name'])
	except Countries.DoesNotExist:
		country = Countries(Country_code=user_country['country_code'],Country_name=user_country['country_name'])
		country.save()

	return country


@api_view(['GET','POST'])
def home(request):

	context = {}

	if request.method == "GET":
		if request.GET.__contains__("search_all_result"):
			Category = Categories.objects.all()
			slider = Slider.objects.all()
			searched_categories = Categories.objects.filter(category__icontains=request.GET.get("search_all_result"))
			searched_websites = Websites.objects.order_by(F('website').asc(nulls_last=True)).filter(website__icontains=request.GET.get("search_all_result"))
			website_set = searched_websites
			page = request.GET.get('page')
			paginator = Paginator(website_set,20)	
			if request.is_ajax():
				try:
					print("page :",page)
					context['websites'] = paginator.page(page)
					print(context['websites'])
					web_html = loader.render_to_string('home/load_more_websites.html',{ 'websites' : context['websites'], })
					return HttpResponse(web_html)
				except EmptyPage:
					return HttpResponse("EMPTY")		
			context['websites'] = paginator.page(1)
			return render(request,"home/search.html",{'category':Category,'slider':slider,'result':searched_categories,'result_websites':context['websites'],'type':'all','search_query':request.GET.get("search_all_result"),})
		elif request.GET.__contains__("search_categories_result"):
			Category = Categories.objects.all()
			searched_categories = Categories.objects.filter(category__icontains=request.GET.get("search_categories_result"))
			return render(request,"home/search.html",{'category':Category,'result':searched_categories,'type':'category','search_query':request.GET.get("search_categories_result"),})
		elif request.GET.__contains__("search_website_result"):
			Category = Categories.objects.all()
			searched_websites = Websites.objects.order_by(F('website').asc(nulls_last=True)).filter(website__icontains=request.GET.get("search_website_result"))

			website_set = searched_websites
			page = request.GET.get('page')
			paginator = Paginator(website_set,20)	
			if request.is_ajax():
				try:
					print("page :",page)
					context['websites'] = paginator.page(page)
					print(context['websites'])
					web_html = loader.render_to_string('home/load_more_websites.html',{ 'websites' : context['websites'] })
					return HttpResponse(web_html)
				except EmptyPage:
					return HttpResponse("EMPTY")		
			context['websites'] = paginator.page(1)
			return render(request,"home/search.html",{'category':Category,'result_websites':context['websites'],'type':'website','search_query':request.GET.get("search_website_result"),})

	template = "home/index.html"
	Category = Categories.objects.all()
	slider = Slider.objects.all()
	return render(request,template,{'category':Category,'slider':slider,})


def control_panel(request):
	if request.user.is_authenticated:
		print(request.session.items())
		print(request.session.get("_auth_user_id"))
		context = {}
		return render(request,"home/control_panel.html",context)
	else:
		raise Http404

def contact(request,type):
	print(request.POST)
	if request.method == "POST":
		print("Post")
		name = request.POST.get('name','')
		subject = request.POST.get('subject','')
		email = request.POST.get('email','')
		message = request.POST.get('message','')
		message = str(message) + "\nname : "+ name
		try:
			send_mail(subject,message,email,['Links2webContact@gmail.com'])
			print('Mail sent')
		except BadHeaderError:
			return HttpResponse("Invalid Header present")
		return redirect(reverse('home'))
	return render(request,'home/contact.html',{'type':type})

def all_websites(request,**kwargs):

	categories = Categories.objects.all()
	queryset = Categories.objects.get(id=kwargs['pk'],category=kwargs['name'])
	context = {}
	if queryset.List_Type  == 'UL':
		template = 'home/all_websites.html'
		if 'sub_category' in kwargs.keys() and kwargs['sub_category'] != 'None':

			context['websites'] = queryset.websites.all().filter(Tags=Sub_Categories.objects.get(Sub_Category=kwargs['sub_category']))
			context['Sub_category'] = kwargs['sub_category']
		else:
			context['websites'] = queryset.websites.all()


	elif queryset.List_Type  == 'OL':
		template = 'home/all_websites_ordered.html'
		if 'sub_category' in kwargs.keys() and kwargs['sub_category'] != 'None':
			context['websites'] = queryset.websites.order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True)).filter(Tags=Sub_Categories.objects.get(Sub_Category=kwargs['sub_category']))
			context['Sub_category'] = kwargs['sub_category']
		else:
			context['websites'] = queryset.websites.order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True))

	try:
		country = visitors_location(visitor_ip_address(request))
	except AddressNotFoundError:
		country = None
	context['Category_name'] = queryset.category
	website_obj = context['websites'].order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True))
	
	context['websites'] = website_obj.exclude(Countries=country)
	websites = website_obj.filter(Countries=country)
	context['websites'] = list(context['websites'])
	websites = list(websites)
	try:
		for i in range(len(websites)):
			context['websites'].insert(i,websites[i])
	except IndexError:
		print("Index error")


	website_set = context['websites']
	print("Final result" , website_set)
	
	page = request.GET.get('page')
	paginator = Paginator(website_set,20)
	
	if request.is_ajax():
		try:
			print("page :",page)
			context['websites'] = paginator.page(page)
			print(context['websites'])
			web_html = loader.render_to_string('home/load_more_websites.html',{ 'websites' : context['websites'],'Category':queryset, })
			return HttpResponse(web_html)
		except EmptyPage:
			return HttpResponse("EMPTY")

	context['websites'] = paginator.page(1)
	context['category'] = categories
	return render(request,template,context)

def Login(request):
	context = {}

	if request.user.is_authenticated:
		return redirect(reverse('control_panel'))

	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request,username=username,password=password)
		print(user)
		if user is not None:
			login(request,user)
			return redirect(reverse('control_panel'))
		else:
			context['error'] = "Wrong Username or Password"
			return render(request,"home/login-page.html",context)


	return render(request,"home/login-page.html",context)

def Logout(request):
	logout(request)
	print(request.user)
	return render(request,"home/Logout.html",{})


@permission('Websites.add_categories')
def add_category(HttpRequest):
	form = add_Categories()
	if HttpRequest.method == "POST":
		form = add_Categories(HttpRequest.POST)
		print("Checking validity")
		if form.is_valid():
			print("Form valid")
			form = form.save(commit=False)
			form.icon = HttpRequest.FILES.get("icon")
			form.save()
			print("saved......")
			category = Categories(pk=form.pk)
			for sub_category in HttpRequest.POST.getlist('sub_categories'):
				sub_Category = Sub_Categories(Category=category.category,Sub_Category=sub_category)
				sub_Category.save()
				category.sub_categories.add(sub_Category.pk)
			print("Sub_Category saved and added")
			return redirect(reverse("add_category"))
	return render(HttpRequest,'home/category-form.html',{'form' : form })


@permission('Websites.change_categories')
def update_category_select(request):
	return render(request,"home/update_select.html",{'name' : 'Select Categories to update' ,"category":Categories.objects.all(),})

class update_category(UpdateView):
	model = Categories
	fields = ('List_Type','icon','category')
	template_name = "home/update_category.html"
	@permission_generic('Websites.change_categories')
	def get(self,request,*args,**kwargs):
		self.object = Categories.objects.get(pk=kwargs['pk'])
		context = self.get_context_data(**kwargs)
		context['Sub_Categories'] = Sub_Categories.objects.filter(Category=self.object.category).exclude(id__in = self.object.sub_categories.all().values("id"))
		return self.render_to_response(context)
		
	
	def get_success_url(self):
		
		return reverse('update_category')
	def form_invalid(self,form):
		print("Form Invalid",form.errors)
		return HttpResponse(form.errors)
	def form_valid(self,form):
		form = form.save(commit=False)
		print(self.request.FILES)
		if self.request.FILES.get("icon"):
			print("icon exists")
			form.icon = self.request.FILES.get("icon")
		category = form
		print(self.request.POST)
		sub_categories_list = self.request.POST.getlist('sub_categories')
		new_sub_categories = self.request.POST.getlist('new_sub_categories')
		for sub_category in new_sub_categories:
			sub_category = Sub_Categories.objects.create(Category=form.category,Sub_Category=sub_category)
			sub_categories_list.append(sub_category.pk)
		category.sub_categories.set(sub_categories_list)
		unselected_subcategories_list = Sub_Categories.objects.filter(categories=None)
		print(unselected_subcategories_list)
		unselected_subcategories_list.delete()
		return super().form_valid(form)


@permission('Websites.delete_categories')
def delete_category_select(request):
	return render(request,"home/update_select.html",{'name' : 'Select Categories to delete',"category":Categories.objects.all(),})

class delete_category(DeleteView):
	model = Categories
	template_name = 'home/delete.html'
	@permission_generic('Websites.delete_categories')
	def get(self,request,*args,**kwargs):
		self.object = Categories.objects.get(pk=kwargs['pk'])
		context = self.get_context_data(**kwargs)
		return self.render_to_response(context)
	success_url = reverse_lazy('delete_category_select')



@permission('Websites.add_websites')
def add_websites(request):
	Category = Categories.objects.all()
	form = add_Websites()
	if request.method == 'POST':
		print(request.POST)
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

				form.category = Categories.objects.get(id = int(request.POST.get('category')))
				
				form = Websites(category=form.category,website=form.website,url=form.url,Number=form.Number)
				form.save()
				print(form,form.pk)
				form.Tags.add(*request.POST.getlist('Tags'))
				print("Adding tags.For pk :",form.pk)
				form.Countries.add(*request.POST.getlist('Countries'))

				form.save()
				print(form.Tags.all())

				inc+=1
		else:
			return HttpResponse(form.errors.as_ul())
		return redirect(reverse('add_websites'))
	return render(request,"home/form.html",{'form':form,'Category' : Category,})


@permission('Websites.update_websites')
def update_single_website_select(request):
	category = Categories.objects.all()
	context = {"categories":category,}
	return render(request,"home/update_single_website_select.html",context)

class update_website(UpdateView):
	model = Websites
	fields = ('__all__')
	template_name = "home/update_single_website.html"
	success_url = reverse_lazy('update_single_website_select')

	def form_valid(self,form):
		self.object = form.save(commit=False)

		print("Valid")
		print(self.request.POST)
		self.object.save()
		self.object.Tags.set(self.request.POST.getlist('Tags'))
		return super().form_valid(form)

	def get_context_data(self,**kwargs):
		context = super().get_context_data(**kwargs)
		context['category'] = Categories.objects.get(pk=self.object.category.pk)
		return context
	@permission_generic('Websites.update_websites')
	def get(self,request,*args,**kwargs):
		print(self.kwargs)
		self.object = Websites.objects.get(pk=kwargs['pk'])

		context = self.get_context_data(**kwargs)
		return self.render_to_response(context)

@permission('Websites.update_websites')
def update_websites_select(request):
	return render(request,"home/update_select.html",{'name' : 'Select Categories of websites to update',"type" : "UW","category":Categories.objects.all(),})


def update_websites(request,**kwargs):
	object = Categories.objects.get(pk=kwargs['pk'])
	kwargs['object'] = object
	paginator = Paginator(Websites.objects.filter(category=object).order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True)),5)
	page = request.GET.get('p')
	queryset = paginator.get_page(page)
	kwargs['page_range'] = paginator.page_range
	kwargs['queryset'] = queryset
	kwargs['categories'] = Categories.objects.all()
	kwargs['Countries'] = Countries.objects.all()

	if request.method == "POST":
		form_queryset = Categories.objects.get(pk=kwargs['pk'])
		all_numbers = request.POST.getlist('Number')
		all_added_websites = request.POST.getlist('website')
		all_url = request.POST.getlist('url')
		category =  Categories.objects.get(id = int(request.POST.get('category')))
		inc = 0
		for website_pk in request.POST.getlist('pk'):
			print(request.POST)
			websites_form = Websites.objects.get(pk=website_pk)
			if all_numbers[inc].isdigit():
				print(True)
				websites_form.Number = int(all_numbers[inc])
			else:
				print(False)
				websites_form.Number = None
			websites_form.website = all_added_websites[inc]
			websites_form.url = all_url[inc]

			websites_form.category = category
			print(websites_form.category)
			websites_form.save()
			websites_form.Tags.set(request.POST.getlist('Tags_'+str(websites_form.pk)))
			websites_form.Countries.set(request.POST.getlist('Countries_'+str(websites_form.pk,)))
			print(inc)
			inc+=1
		print(request.POST)
		print("Saving.....")
		return redirect(reverse_lazy('update_website'))

	return render(request,"home/update_website.html",kwargs)


@permission('Websites.delete_websites')
def delete_websites(request):
	categories = Categories.objects.all()
	if request.method == "POST":
		website = Websites.objects.get(pk=request.POST.get('pk'))
		website.delete()
	return render(request,'home/delete_websites.html',{'categories':categories})

@api_view(['GET'])
def Slider_data(request):
	slider = Slider.objects.all()
	slider_serializer = Slider_serializers(slider,many=True)
	return Response(slider_serializer.data)

@api_view(['GET','POST'])
#@renderer_classes((TemplateHTMLRenderer,))
def Categories_and_websites(request):
	if request.method == 'GET':
		print(dir(request))
		print('User : ',request.data)
		if 'search' in request.GET:
			Category = Categories.objects.filter(category__icontains = request.GET.get('search'))
			print(request.GET.get('search'))
		else:
			Category = Categories.objects.all()
		print("'Categories search'",Category)
		serializer = categories_serializers(Category,context={"request":request},many=True)
		return Response(serializer.data)

@api_view(['GET'])
def categories(request,id):
	Category = Categories.objects.get(pk=id)
	Category_serializer = categories_serializers(Category)
	return Response(Category_serializer.data)

@api_view(['GET'])
def websites_data(request,**kwargs):
	#Get page number from request
	page = request.GET.get('p')
	#Check if id is in url arguments kwargs
	Category = None
	if 'id' in kwargs.keys():				
		Category = Categories.objects.get(pk=kwargs['id'])
		#check if subcategory exists in the url arguments
		if 'subCategory' in kwargs.keys():
			#if subcatrgory exists, check if it ia an ordered list
			if Category.List_Type == "OL":
				if "search" in request.GET:
					websites = Websites.objects.order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True)).filter(category=Category,Tags = Sub_Categories.objects.get(Sub_Category=kwargs['subCategory']),website__icontains=request.GET.get("search"))
				else:
					websites = Websites.objects.order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True)).filter(category=Category,Tags = Sub_Categories.objects.get(Sub_Category=kwargs['subCategory']))	
			else:
				#if Category object is an Unordered list just filter by category and subcategory
				if "search" in request.GET:
					websites = Websites.objects.order_by(F('website').asc(nulls_last=True)).filter(category=Category,Tags = Sub_Categories.objects.get(Sub_Category=kwargs['subCategory']),website__icontains=request.GET.get("search"))
				else:
					websites = Websites.objects.order_by(F('website').asc(nulls_last=True)).filter(category=Category,Tags = Sub_Categories.objects.get(Sub_Category=kwargs['subCategory']))
				

		else:
		#if category is an ordered list
			if Category.List_Type == "OL":
			#Order category by number attribute and filter it by category
				if 'search' in request.GET:
					websites = Websites.objects.order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True)).filter(category=Category,website__icontains = request.GET.get("search"))

				else:
					websites = Websites.objects.order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True)).filter(category=Category)
			#Paginate it. Just 20 items visible
			

			else:
			#if unordered list filter websites just by categories
				if "search" in request.GET:
					websites = Websites.objects.order_by(F('website').asc(nulls_last=True)).filter(category=Category,website__icontains=request.GET.get("search"))
					print("Here")
				else:
					websites = Websites.objects.filter(category=Category)
		
	else:
		if 'search' in request.GET:
			print(True)
			websites = Websites.objects.order_by(F('website').asc(nulls_last=True)).filter(website__icontains=request.GET.get('search'))
		else:
				websites = Websites.objects.order_by(F('website').asc(nulls_last=True))
	try:
		country = visitors_location(visitor_ip_address(request))
	except AddressNotFoundError:
		country = None

	website_obj = websites.order_by(F('Number').asc(nulls_last=True),F('website').asc(nulls_last=True))
	print(website_obj)
	other_websites = website_obj.exclude(Countries=country)
	websites = website_obj.filter(Countries=country)
	other_websites = list(other_websites)
	websites = list(websites)
	try:
		for i in range(len(websites)):
			other_websites.insert(i,websites[i])
	except IndexError:
		print("Index error")

	websites=other_websites
	print(websites)

	paginator = Paginator(websites,20)
	try:
		websites = paginator.page(page)
	except EmptyPage:
		return Response(None,)
	except PageNotAnInteger:
		websites = paginator.page(1)


	websites_Serializer = json_serializers(websites,many=True)
	if Category is not None:
		websites_Serializer.List_Type = Category.List_Type
	
	
	return Response(websites_Serializer.data)

@api_view(['GET','POST'])
def jsondata(request):

	if request.method == 'GET':
		website = Websites.objects.all()
		serializer = json_serializers(website,many=True)
		return Response(serializer.data)


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
		print("Hello")
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

@csrf_exempt
def add_website_external(request):
	categories = Categories.objects.all()
	if request.method == "POST":
		category_id = request.POST.get("category_id")
		category = Categories.objects.get(pk=category_id)
		website_url =request.POST.get("website")
		sub_categories = request.POST.getlist("sub_category_id")
		print(request.POST)		
		website = website_url
		prefix = ["http://www.","https://www.","http://","https://","www."]
		for pre in prefix:
			if website.startswith(pre):
				website = website[len(pre):]
				break
		website = website.rstrip("/")
		if website.endswith(".com"):
			website = website.rstrip(".com")
			
		
		website = Websites.objects.create(website=website,url=website_url,category=category)
		print(type(sub_categories))
		if sub_categories:
			print("Sub categories")
			website.Tags.set(sub_categories)
		return HttpResponse(f"{website_url} has been added successfully")
	else:
		data_list = []
		for category in categories:
			obj = {"category":category.category,"id":category.id,"sub_categories":list(category.sub_categories.values("id","Sub_Category"))}
			data_list.append(obj)
		return JsonResponse(data_list,safe=False)





