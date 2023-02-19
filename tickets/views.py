from django.http import Http404
from django.shortcuts import render
from django.http.response import JsonResponse 
from .models import *
from rest_framework.decorators import api_view
from .serializers import GuestSerializer , MovieSerializer , ReservationSerializer
from rest_framework import status , filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics , mixins , viewsets
from rest_framework import urls
from rest_framework.authentication import BasicAuthentication , TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here. 

#1
def no_rest_no_model(request):
    guests=[
        {
          'id': 1,
          "Name" : "mahmoud",
          "mobile" : 102065656  
        },
        {
          'id': 2, 
          "Name" : "ahmoud",
          "mobile" : 12065656  
        },
    ]
    return JsonResponse(guests,safe=False)

#2
def no_rest_from_model(request):
    data = Guest.objects.all()
    response = {
        'guests': list(data.values('name', 'mobile'))
    }
    return JsonResponse(response)
  
  
#3 Function based views

#3.1 GET POST
@api_view(['GET','POST']) 
def FBV_List(request):
  #GET
  if request.method == 'GET':
    guests = Guest.objects.all()
    serializer = GuestSerializer(guests , many = True)
    return Response(serializer.data)
  
  #POST
  elif request.method =='POST':
    serializer = GuestSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data , status=status.HTTP_201_CREATED)
    return Response(serializer.data , status = status.HTTP_400_BAD_REQUEST)
  
    
  



#3.2 GET PUT DELETE
@api_view(['GET', 'PUT', 'DELETE'])
def FBV_pk(request, pk):
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = GuestSerializer(guest)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = GuestSerializer(guest, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
#class based views
#4.1 List and Create == GET and POST

class CBV_List(APIView):
    def get(self , request): 
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests , many = True)
        return Response(serializer.data)
    def post(self , request):
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(serializer.data , status=status.HTTP_400_BAD_REQUEST)
           
#4.2  GET PUT DELETE class based views -- pk

class CBV_pk(APIView):
    def get_object(self , pk):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Http404
        
    def get(self , request , pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest)
        return Response(serializer.data)     
    
    def put(self , request , pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest , data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)  
        return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
    def delete(self , request , pk):
        guest = self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
#5 mixins
 
#5.1 mixin list
class mixins_list(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
    def get(self , request):
        return self.list(request)
    def post(self , request):
        return self.create(request)
    
    
#5.2 mixin GET PUT DELETE --pk    

class mixins_pk(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
    def get(self,request,pk):
        return self.retrieve(request)
    def put(self,request,pk):
        return self.update(request)
    def delete(self,request,pk):
        return self.destroy(request)
    
    
#6 Generics
#6.1 get post 
class generics_list(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes =[TokenAuthentication]
    #permission_classes = [IsAuthenticated]
    
#6.2 get put delete --pk 
class generics_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset =Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes =[TokenAuthentication]
    #permission_classes = [IsAuthenticated]
        

#7 viewsets
class viewsets_guest(viewsets.ModelViewSet):
    queryset =Guest.objects.all()
    serializer_class = GuestSerializer

class viewsets_movie(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['movie']
    
class viewsets_reservation(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer    
    
    
#8 find movie   
@api_view(['GET'])
def find_movie(request):
    hall = request.data.get('hall')
    movie = request.data.get('movie')
    if hall is None or movie is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    movies = Movie.objects.filter(hall=hall, movie=movie)
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def new_reservation(request):
    movie = Movie.objects.get(
        hall = request.data['hall'],
        movie = request.data['movie']
    )
    guest = Guest()
    guest.name = request.data['name']
    guest.mobile = request.data['mobile']
    guest.save()
    
    reservation = Reservation()
    reservation.guest = guest
    reservation.movie = movie
    reservation.save()
    
    return Response(status=status.HTTP_201_CREATED)