from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Nursery
from .serializers import NurserySerializer
from rest_framework.permissions import IsAuthenticated

# # Create your views here.
# class NurseryListCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         nurseries = Nursery.objects.all()
#         serializer = NurserySerializer(nurseries, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = NurserySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class NurseryDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get_object(self, pk):
#         try:
#             return Nursery.objects.get(pk=pk)
#         except Nursery.DoesNotExist:
#             return None

#     def get(self, request, pk):
#         nursery = self.get_object(pk)
#         if not nursery:
#             return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = NurserySerializer(nursery)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         nursery = self.get_object(pk)
#         if not nursery:
#             return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
#         # Exemple : on exige que seul le manager modifie la crèche
#         if nursery.manager != request.user:
#             return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

#         serializer = NurserySerializer(nursery, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, pk):
#         nursery = self.get_object(pk)
#         if not nursery:
#             return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
#         if nursery.manager != request.user:
#             return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

#         serializer = NurserySerializer(nursery, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         nursery = self.get_object(pk)
#         if not nursery:
#             return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
#         if nursery.manager != request.user:
#             return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
#         nursery.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# from rest_framework import generics
# from .models import Classroom
# from .serializers import ClassroomSerializer
# from rest_framework.permissions import IsAuthenticatedOrReadOnly

# class ClassroomListCreateView(generics.ListCreateAPIView):
#     queryset = Classroom.objects.all()
#     serializer_class = ClassroomSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     def perform_create(self, serializer):
#         # Exemple : on peut vérifier que seul un manager peut créer
#         if not self.request.user.type == 'nursery_manager':
#             raise PermissionDenied("Seuls les managers peuvent créer une classe.")
#         serializer.save()

# from rest_framework import generics
# from .models import Group
# from .serializers import GroupSerializer
# from rest_framework.permissions import IsAuthenticated

# class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_update(self, serializer):
#         # Exemple : vérification métier
#         group = self.get_object()
#         if group.classroom.nursery.manager != self.request.user:
#             raise PermissionDenied("Non autorisé.")
#         serializer.save()
# from rest_framework import generics
# from .models import Group
# from .serializers import GroupSerializer
# from rest_framework.permissions import IsAuthenticated

# class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_update(self, serializer):
#         # Exemple : vérification métier
#         group = self.get_object()
#         if group.classroom.nursery.manager != self.request.user:
#             raise PermissionDenied("Non autorisé.")
#         serializer.save()

# from rest_framework import viewsets
# from .models import Child
# from .serializers import ChildSerializer
# from rest_framework.permissions import IsAuthenticated

# class ChildViewSet(viewsets.ModelViewSet):
#     """
#     Fournit : 
#     - GET /children/            (liste)
#     - POST /children/           (création)
#     - GET /children/{pk}/       (détail)
#     - PUT /children/{pk}/       (mise à jour complète)
#     - PATCH /children/{pk}/     (mise à jour partielle)
#     - DELETE /children/{pk}/    (suppression)
#     """
#     queryset = Child.objects.all()
#     serializer_class = ChildSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         # Exemple de filtrage : seuls les parents peuvent voir leurs enfants
#         user = self.request.user
#         if user.type == 'parent':
#             return Child.objects.filter(user_type=user)
#         # Les managers/assistants peuvent lister tous les enfants de leur crèche
#         if user.type in ['nursery_manager', 'nursery_assistant']:
#             return Child.objects.filter(classroom__nursery=user.nursery)
#         # Admin (staff) voit tout
#         return super().get_queryset()

#     def perform_create(self, serializer):
#         # Si parent, on assigne automatiquement le parent actuel
#         if self.request.user.type == 'parent':
#             serializer.save(user_type=self.request.user)
#         else:
#             raise PermissionDenied("Seuls les parents peuvent créer un enfant.")
