from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models.functions import Round
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# from rest_framework.authtoken.admin import User
# from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer

from texnomart.models import Category, Product, ProductAttribute, Key, Value


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.title", read_only=True)  # Bu maydon faqat o'qish uchun
    is_liked = serializers.SerializerMethodField(method_name='get_is_liked', read_only=True)  # Bu maydon faqat o'qish uchun
    image = serializers.SerializerMethodField(method_name='get_image', read_only=True)  # Bu maydon faqat o'qish uchun

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user in obj.is_liked.all()
        return False

    def get_image(self, obj):
        request = self.context.get('request')
        image = next((img for img in obj.images.all() if img.is_primary), None)
        if image:
            return request.build_absolute_uri(image.image.url)
        return None

    class Meta:
        model = Product
        fields = '__all__'


class ProductModelSerializer(ModelSerializer):
    category_name = serializers.CharField(source="category.title")
    is_liked = serializers.SerializerMethodField(method_name='get_is_liked')
    caunt_is_liked = serializers.SerializerMethodField(method_name='get_caunt_is_liked')
    image = serializers.SerializerMethodField(method_name='get_image')
    avg_reting = serializers.SerializerMethodField(method_name='get_avg_reting')
    all_images = serializers.SerializerMethodField(method_name='get_all_images')
    comment_info = serializers.SerializerMethodField(method_name='get_comment_info')
    attributes = serializers.SerializerMethodField(method_name='get_attributes')

    def get_attributes(self,instance):
        attributes=[{str(attribute.key_name): str(attribute.value_name)} for attribute in instance.attributes.all() ]
        return attributes

    def get_comment_info(self,obj):
        comment_count = obj.comments.count()
        return {'Comment_count':comment_count}, obj.comments.all().values('comment','reting','user__username')

    def get_all_images(self, instance):
        request = self.context.get('request')
        images = instance.images.all().order_by('-is_primary','-id')
        all_image = []
        for image in images:
            all_image.append(request.build_absolute_uri(image.image.url))

        return all_image





    def get_avg_reting(self,obj):
        avg_reting = obj.comments.all().aggregate(avg_reting=Round(Avg('reting')))
        return avg_reting

    def get_image(self,obj):
        # image = Image.objects.filter(is_primary=True,pk=obj.pk).first()
        image = obj.images.filter(is_primary=True).first()
        if image:
            image_url = image.image.url
            request = self.context.get('request')
            return request.build_absolute_uri(image_url)


    def get_caunt_is_liked(self, instance):
        return instance.is_liked.count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if user in obj.is_liked.all():
                return True
            return False

    class Meta:
        model = Product
        fields = '__all__'


class AttributeSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()

    def get_attributes(self, products):
        attributes = ProductAttribute.objects.filter(product=products.id)
        attributes_dict = {}
        for attribute in attributes:
            attributes_dict[attribute.key.name] = attribute.value.name
        return attributes_dict

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'attributes']


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = '__all__'


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ['username', 'password']


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password", "password2"]

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise ValidationError({"detail": "User already exists!"})
        return username

    def validate(self, data):
        if data['password'] != data['password2']:
            raise ValidationError({"message": "Both passwords must match!"})

        if User.objects.filter(email=data['email']).exists():
            raise ValidationError({"message": "Email already taken!"})

        return data

    def create(self, validated_data):
        # Remove password2 as it is not needed for user creation
        validated_data.pop('password2')

        # Create the user
        user = User.objects.create_user(**validated_data)
        return user
