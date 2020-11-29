from itertools import chain
from django.shortcuts import render,redirect
from django.core.mail import send_mail,BadHeaderError
from django.db.models import F
from django.contrib.auth.models import User,UserManager , Permission
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger,Page
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse,reverse_lazy
from django.template import loader
from django.http import HttpResponse,JsonResponse,HttpRequest,HttpResponseServerError
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
		context = {}
		return render(request,"home/control_panel.html",context)
	else:
		raise Http404

def contact(request,type):
	#Delete email sent session variable
	if "email_sent" in request.session:
		del request.session["email_sent"]

	if request.method == "POST":
		name = request.POST.get('name','')
		subject = request.POST.get('subject','')
		email = request.POST.get('email','')
		message = request.POST.get('message','')
		message += "\n\nName: "+ name + "\nEmail: "+email
		try:
			send_mail(subject,message,email,['Links2webContact@gmail.com'])
		except BadHeaderError:
			return HttpResponse("Invalid Header present")
		request.session["email_sent"] = True
	return render(request,'home/contact.html',{'type':type,"email_sent":request.session.get("email_sent")})

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
		print(context['websites'].values("Number","website"))

	try:
		country = visitors_location(visitor_ip_address(request))
	except:
		country = None
	context['Category_name'] = queryset.category
	website_obj = context["websites"]	
	context['websites'] = website_obj.exclude(Countries=country)
	websites = website_obj.filter(Countries=country)
	context['websites'] = list(chain(websites,context["websites"]))

	website_set = context['websites']
	
	page = request.GET.get('page')
	paginator = Paginator(website_set,20)
	
	if request.is_ajax():
		try:
			context['websites'] = paginator.page(page)
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
		if user is not None:
			login(request,user)
			return redirect(reverse('control_panel'))
		else:
			context['error'] = "Wrong Username or Password"
			return render(request,"home/login-page.html",context)

	return render(request,"home/login-page.html",context)

def Logout(request):
	logout(request)
	return render(request,"home/Logout.html",{})


@permission('Websites.add_categories')
def add_category(HttpRequest):
	form = add_Categories()
	if HttpRequest.method == "POST":
		form = add_Categories(HttpRequest.POST)
		if form.is_valid():
			form = form.save(commit=False)
			form.icon = HttpRequest.FILES.get("icon")
			form.save()
			category = Categories(pk=form.pk)
			for sub_category in HttpRequest.POST.getlist('sub_categories'):
				sub_Category = Sub_Categories(Category=category.category,Sub_Category=sub_category)
				sub_Category.save()
				category.sub_categories.add(sub_Category.pk)
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
		return HttpResponse(form.errors)
	def form_valid(self,form):
		form = form.save(commit=False)
		if self.request.FILES.get("icon"):
			form.icon = self.request.FILES.get("icon")
		category = form
		sub_categories_list = self.request.POST.getlist('sub_categories')
		new_sub_categories = self.request.POST.getlist('new_sub_categories')
		for sub_category in new_sub_categories:
			sub_category = Sub_Categories.objects.create(Category=form.category,Sub_Category=sub_category)
			sub_categories_list.append(sub_category.pk)
		category.sub_categories.set(sub_categories_list)
		unselected_subcategories_list = Sub_Categories.objects.filter(categories=None)
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
		form = add_Websites(request.POST)
		if form.is_valid():
			form = form.save(commit=False)
			website_url = form.url
			if website_url.startswith("http://"):
				website_url = website_url.lstrip("http://")
			elif website_url.startswith("https://"):
				website_url = website_url.lstrip("https://")
			form.url = website_url
			form.save()
			form.Countries.set(request.POST.getlist("Countries"))
			form.Tags.set(request.POST.getlist("Tags"))
			return HttpResponse(form.website + " has been added successfully.")
		else:
			return HttpResponseServerError(form.errors.as_ul())
		return redirect(reverse('add_websites'))
	return render(request,"home/form.html",{'form':form,'Category' : Category,})


@permission('Websites.update_websites')
def update_websites(request):

	if request.is_ajax():
		if request.method == "POST":
			data = request.POST
			website = Websites.objects.get(pk=data.get("website-pk"))
			website.website = data.get("website")
			website.url = data.get("url")
			if data.get("Number"):
				website.Number = data.get("Number")
			if "category" in data:
				website.category = Categories.objects.get(pk=data.get("category"))
			if "sub-category-default" not in data:
				website.Tags.set(data.getlist("Tags"))
			if "countries-default" not in data:
				website.Countries.set(data.getlist("Countries"))
			website.save()
			return HttpResponse("Success")
		elif "get_website_info" in request.GET:
			website = Websites.objects.get(pk=request.GET.get("get_website_info"))
			data = {
				"number": website.Number,
				"website": website.website,
				"url": website.url,
				"category":website.category.category,
				"tags": list(website.Tags.values_list("Sub_Category",flat=True)),
				"countries":list(website.Countries.values_list("Country_name",flat=True))
			}
			return JsonResponse(data)
		elif "fetch_website_text" in request.GET:
			text = request.GET.get("fetch_website_text")
			search_type = request.GET.get("type")
			if search_type == 'website':
				website = Websites.objects.filter(website__icontains=text)
			elif search_type == 'url':
				website = Websites.objects.filter(url__icontains=text)
			elif search_type == 'category':
				website = Websites.objects.filter(category__category__icontains=text)
			elif search_type == 'sub-category':
				website = Websites.objects.filter(Tags__Sub_Category__icontains=text).distinct()

			paginator = Paginator(website,20)
			try:
				if "page_no" in request.GET:
					websites = paginator.page(request.GET.get("page_no"))
				else:
					websites = paginator.page(1)
				websites = list(websites.object_list.values())
				return JsonResponse(websites,safe=False)
			except EmptyPage:
				return HttpResponse("EMPTY")
	Category = Categories.objects.all()
	countries = Countries.objects.all()
	return render(request,"home/update_website.html",{'Category' : Category,"Countries":countries})


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
		if 'search' in request.GET:
			Category = Categories.objects.filter(category__icontains = request.GET.get('search'))
		else:
			Category = Categories.objects.all()
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


