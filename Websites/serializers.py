from Websites.models import Websites,Categories,Slider
from rest_framework import serializers

class Slider_serializers(serializers.ModelSerializer):
	class Meta:
		model = Slider
		fields = '__all__'
class Categories_serializers(serializers.ModelSerializer):
	sub_categories = serializers.StringRelatedField(many=True)

	class Meta:
		model = Categories
		fields = '__all__'		

class json_serializers(serializers.ModelSerializer):
	category = Categories_serializers()
	Tags = serializers.StringRelatedField(many=True)

	class Meta:
		model = Websites
		fields = ('__all__')	
		
class websites_serializers(serializers.ModelSerializer):
	class Meta:
		model = Websites
		fields = '__all__'		


class categories_serializers(serializers.ModelSerializer):
	sub_categories = serializers.StringRelatedField(many=True)
	icon = serializers.SerializerMethodField("get_icon_url")
	def get_icon_url(self,obj):
		try:
			request = self.context['request']
			return "http://"+request.get_host()+str(obj.icon.url)
		except:
			return None
	class Meta:
		model = Categories
		fields = ('pk','List_Type','icon','category','sub_categories',)
	
	
	
	
	
	
	
	
	
	