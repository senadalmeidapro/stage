**Voici un guide exhaustif et détaillé, module par module, pour maîtriser chaque brique de Django REST Framework :**
Nous allons aborder les **Serializers**, les **Views**, les **URLs**, les **types de requêtes (GET, POST, etc.)**, les **filtres**, ainsi que les aspects de **permissions**, **authentification** et **throttling**. Chaque section présente tous les cas de figure et manipulations courantes.

---

## 1. **Serializers : transformer objets Python ↔ JSON**

Les **Serializers** sont responsables de :

1. **Sérialiser** (objet Python → JSON)
2. **Désérialiser** (JSON → objet Python validé)

### 1.1 Types de Serializers

1. **`Serializer` (de base)**

   * Vous définissez manuellement chaque champ (`CharField`, `IntegerField`, etc.).
   * Contrôle total sur la validation et sur la transformation.
   * Utile pour des payloads non directement liés à un modèle Django.

   ```python
   from rest_framework import serializers

   class ExampleSerializer(serializers.Serializer):
       name = serializers.CharField(max_length=100)
       age = serializers.IntegerField(min_value=0)
       email = serializers.EmailField()

       def validate_age(self, value):
           # Validation spécifique sur le champ age
           if value < 3:
               raise serializers.ValidationError("L'âge minimum est 3 ans.")
           return value

       def validate(self, attrs):
           # Validation sur l'ensemble des données
           if "@" not in attrs['email']:
               raise serializers.ValidationError("Email invalide.")
           return attrs
   ```

2. **`ModelSerializer`**

   * Lie automatiquement le serializer à un modèle Django (`Meta.model`).
   * Génère automatiquement les champs correspondant aux champs du modèle.
   * Propose `create()` et `update()` par défaut (on peut les surcharger).

   ```python
   from rest_framework import serializers
   from .models import Child

   class ChildSerializer(serializers.ModelSerializer):
       class Meta:
           model = Child
           # fields = '__all__' ou liste explicite ['id', 'first_name', ...]
           fields = ['id', 'first_name', 'last_name', 'birthday', 'user_type', 'subscription']
           read_only_fields = ['id']

       def validate_birthday(self, value):
           # Exemple de validation métier : un enfant doit avoir moins de 18 ans
           from datetime import date
           if (date.today().year - value.year) > 18:
               raise serializers.ValidationError("L'enfant ne peut pas avoir plus de 18 ans.")
           return value

       def create(self, validated_data):
           # Exemple : on peut injecter automatiquement la date d'enregistrement
           validated_data['register_date'] = timezone.now()
           return super().create(validated_data)

       def update(self, instance, validated_data):
           # Exemple : on pourrait empêcher de changer le parent après création
           if 'user_type' in validated_data and instance.user_type != validated_data['user_type']:
               raise serializers.ValidationError("Impossible de modifier le parent d'un enfant déjà créé.")
           return super().update(instance, validated_data)
   ```

### 1.2 Champs particuliers

* **`read_only=True`** : le champ n’est pas pris en compte dans `POST`/`PUT`/`PATCH`. Exemples : `created_at`, `id`.
* **`write_only=True`** : champ reçu dans `POST`/`PUT`/`PATCH` mais non renvoyé dans la réponse. Ex. : mot de passe.
* **`required=False`** : champ facultatif lors de la sérialisation entrante.
* **`allow_null=True`** : autorise explicitement la valeur `null`.
* **`default=`** : valeur par défaut si le champ est absent.

### 1.3 Champs relationnels

* **ForeignKey (clé étrangère)**

  ```python
  class SubscriptionSerializer(serializers.ModelSerializer):
      class Meta:
          model = Subscription
          fields = ['id', 'plan', 'start_date', 'end_date', 'price', 'is_active']
  ```

  * Par défaut, les relations sont représentées par leur clé primaire (`plan` → ID du plan).
  * On peut exposer l’objet lié dans sa globalité avec un **Nested Serializer** :

    ```python
    class PlanSerializer(serializers.ModelSerializer):
        class Meta:
            model = Plan
            fields = ['id', 'name', 'price']

    class SubscriptionSerializer(serializers.ModelSerializer):
        plan = PlanSerializer(read_only=True)
        plan_id = serializers.PrimaryKeyRelatedField(
            queryset=Plan.objects.all(), write_only=True, source='plan'
        )

        class Meta:
            model = Subscription
            fields = ['id', 'plan', 'plan_id', 'start_date', 'end_date', 'price']
    ```

    * Ici, `plan` est en lecture seule (affiche nom + prix), et `plan_id` est le champ en écriture pour lier l’ID du plan.

* **ManyToMany**

  ```python
  class GroupSerializer(serializers.ModelSerializer):
      children = serializers.PrimaryKeyRelatedField(
          many=True,
          queryset=Child.objects.all()
      )

      class Meta:
          model = Group
          fields = ['id', 'name', 'classroom', 'children']
  ```

  * Pour ajouter/enlever des enfants à un groupe, on envoie une liste d’IDs dans `children`.
  * On peut également créer un nested serializer si l’on souhaite renvoyer des données enfants complètes.

### 1.4 Validation globale dans le Serializer

```python
class OpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHour
        fields = ['id', 'nursery', 'day', 'open_time', 'close_time', 'is_closed']

    def validate(self, attrs):
        # Exemple : si is_closed == False, on veut que close_time > open_time
        if not attrs.get('is_closed', False):
            if attrs['close_time'] <= attrs['open_time']:
                raise serializers.ValidationError("L'heure de fermeture doit être après l'heure d'ouverture.")
        return attrs
```

* `validate_<fieldname>(self, value)` : appelé pour la validation d’un champ isolé.
* `validate(self, attrs)` : appelé après la validation de chaque champ, on peut vérifier des contraintes « cross-fields ».

---

## 2. **Views : exposer la logique métier via HTTP**

DRF propose plusieurs façons de construire ses vues, selon le niveau de flexibilité vs rapidité de mise en œuvre.

### 2.1 **`APIView` (classe de base)**

* Tous les verbes HTTP (GET, POST, PUT, PATCH, DELETE) se traduisent en méthodes (`def get()`, `def post()`, etc.).
* **Contrôle fin** : idéal pour des besoins sur-mesure.

#### Exemple : CRUD complet sur un modèle `Nursery`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Nursery
from .serializers import NurserySerializer
from rest_framework.permissions import IsAuthenticated

class NurseryListCreateView(APIView):
    permission_classes = [IsAuthenticated]  # tous les utilisateurs authentifiés

    def get(self, request):
        nurseries = Nursery.objects.all()
        serializer = NurserySerializer(nurseries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NurserySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(manager=request.user)  # par exemple, on assigne le manager automatiquement
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NurseryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Nursery.objects.get(pk=pk)
        except Nursery.DoesNotExist:
            return None

    def get(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = NurserySerializer(nursery)
        return Response(serializer.data)

    def put(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        # Exemple : on exige que seul le manager modifie la crèche
        if nursery.manager != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = NurserySerializer(nursery, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        if nursery.manager != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = NurserySerializer(nursery, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'detail': 'Non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        if nursery.manager != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        nursery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### Cas particuliers et traitements :

* **Absence de l’objet (404)** : toujours renvoyer un `Response(..., status=404)`.
* **Permission (403)** : vérifier explicitement avant la modification/suppression.
* **Validation des données** : appeler `serializer.is_valid()`, gérer les erreurs (400).
* **Partial vs strict update** :

  * `data=request.data, partial=True` pour un `PATCH` (mise à jour partielle).
  * Sans `partial=True` pour un `PUT` (nécessité d’envoyer tous les champs requis).

### 2.2 **`GenericAPIView` + Mixins**

* Fournissent des comportements CRUD courants :

  * `ListModelMixin` (GET liste)
  * `CreateModelMixin` (POST)
  * `RetrieveModelMixin` (GET détail)
  * `UpdateModelMixin` (PUT / PATCH)
  * `DestroyModelMixin` (DELETE)

#### Exemple : liste/création de classes

```python
from rest_framework import generics
from .models import Classroom
from .serializers import ClassroomSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class ClassroomListCreateView(generics.ListCreateAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Exemple : on peut vérifier que seul un manager peut créer
        if not self.request.user.type == 'nursery_manager':
            raise PermissionDenied("Seuls les managers peuvent créer une classe.")
        serializer.save()
```

#### Exemple : détail, mise à jour, suppression de groupe

```python
from rest_framework import generics
from .models import Group
from .serializers import GroupSerializer
from rest_framework.permissions import IsAuthenticated

class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        # Exemple : vérification métier
        group = self.get_object()
        if group.classroom.nursery.manager != self.request.user:
            raise PermissionDenied("Non autorisé.")
        serializer.save()
```

### 2.3 **`ViewSet` et `Router`**

* Un **ViewSet** regroupe toutes les actions CRUD d’un même modèle dans une seule classe.
* Le **Router** DRF génère automatiquement les routes (URLs) pour chaque action (list, create, retrieve, update, destroy).

#### Exemple : API complète pour `Child`

```python
from rest_framework import viewsets
from .models import Child
from .serializers import ChildSerializer
from rest_framework.permissions import IsAuthenticated

class ChildViewSet(viewsets.ModelViewSet):
    """
    Fournit : 
    - GET /children/            (liste)
    - POST /children/           (création)
    - GET /children/{pk}/       (détail)
    - PUT /children/{pk}/       (mise à jour complète)
    - PATCH /children/{pk}/     (mise à jour partielle)
    - DELETE /children/{pk}/    (suppression)
    """
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Exemple de filtrage : seuls les parents peuvent voir leurs enfants
        user = self.request.user
        if user.type == 'parent':
            return Child.objects.filter(user_type=user)
        # Les managers/assistants peuvent lister tous les enfants de leur crèche
        if user.type in ['nursery_manager', 'nursery_assistant']:
            return Child.objects.filter(classroom__nursery=user.nursery)
        # Admin (staff) voit tout
        return super().get_queryset()

    def perform_create(self, serializer):
        # Si parent, on assigne automatiquement le parent actuel
        if self.request.user.type == 'parent':
            serializer.save(user_type=self.request.user)
        else:
            raise PermissionDenied("Seuls les parents peuvent créer un enfant.")
```

#### Router et URLs :

```python
from rest_framework.routers import DefaultRouter
from .views import ChildViewSet

router = DefaultRouter()
router.register(r'children', ChildViewSet, basename='children')

urlpatterns = router.urls
```

---

## 3. **URLs : router vs définition manuelle**

### 3.1 Routage manuel (sans ViewSet)

```python
from django.urls import path
from .views import NurseryListCreateView, NurseryDetailView

urlpatterns = [
    path('nurseries/', NurseryListCreateView.as_view(), name='nursery-list'),
    path('nurseries/<int:pk>/', NurseryDetailView.as_view(), name='nursery-detail'),
]
```

* **`<int:pk>`** : capture l’identifiant numérique.
* On peut ajouter des contraintes supplémentaires (UUID, slug, etc.) si besoin.

### 3.2 Routage automatique avec `DefaultRouter`

* Crée automatiquement toutes les routes CRUD pour un `ModelViewSet` ou `ReadOnlyModelViewSet`.
* Exemple pour `Classroom` :

```python
from rest_framework.routers import DefaultRouter
from .views import ClassroomViewSet

router = DefaultRouter()
router.register(r'classrooms', ClassroomViewSet, basename='classroom')

urlpatterns = router.urls
```

* On obtient automatiquement :

  * `GET /classrooms/`
  * `POST /classrooms/`
  * `GET /classrooms/{pk}/`
  * `PUT /classrooms/{pk}/`
  * `PATCH /classrooms/{pk}/`
  * `DELETE /classrooms/{pk}/`

### 3.3 Routes avancées et **nested routers**

Quand on veut imbriquer des routes (par ex. lister les `OpeningHour` d’une `Nursery`), on peut utiliser `drf-nested-routers`.

```python
from rest_framework_nested import routers
from django.urls import path, include
from .views import NurseryViewSet, OpeningHourViewSet

router = routers.SimpleRouter()
router.register(r'nurseries', NurseryViewSet, basename='nursery')

nurseries_router = routers.NestedSimpleRouter(router, r'nurseries', lookup='nursery')
nurseries_router.register(r'opening_hours', OpeningHourViewSet, basename='nursery-opening_hours')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(nurseries_router.urls)),
]
```

* On obtient :

  * `GET /nurseries/{nursery_pk}/opening_hours/`
  * `POST /nurseries/{nursery_pk}/opening_hours/`
  * etc.

---

## 4. **Requêtes HTTP : GET, POST, PUT, PATCH, DELETE**

### 4.1 **GET (Collection / Détail)**

* **GET list** (`ModelViewSet` ou `ListAPIView`)

  * Ex : `GET /activities/`
  * Renvoie une **liste d’objets** sérialisés.
  * On peut ajouter :

    * **Pagination** (`PageNumberPagination`, `LimitOffsetPagination`)
    * **Filtrage** via `?field=value`
    * **Recherche** (`?search=mot`)
    * **Tri** (`?ordering=nom,-date`)

* **GET détail** (`RetrieveAPIView`)

  * Ex : `GET /activities/12/`
  * Renvoie l’**objet unique** identifié par `pk`.
  * Si non trouvé → `404 Not Found`.

### 4.2 **POST (Création)**

* **POST /resources/** crée une nouvelle instance.

  * Ex : `POST /groups/`
  * Payload JSON example :

    ```json
    {
      "name": "Groupe A",
      "classroom": 5,
      "description": "Groupe des 2-3 ans"
    }
    ```
  * Processus :

    1. La vue appelle le `Serializer(data=request.data)`.
    2. `serializer.is_valid()` exécute toutes les validations (champs requis, règles métier).
    3. `serializer.save()` crée l’objet en base (méthode `create()` ou surcharge personnalisée).
    4. Renvoi `Response(serializer.data, status=201)` si succès.
    5. Si `is_valid()` échoue → `Response(serializer.errors, status=400)`.

### 4.3 **PUT (Remplacement complet)**

* **PUT /resources/{pk}/**

  * Nécessite d’envoyer **tous** les champs requis par le serializer (même si inchangés).
  * Exemple :

    ```json
    {
      "name": "Groupe A - MAJ",
      "classroom": 5,
      "description": "Nouvelle desc..."
    }
    ```
  * Si un champ manquant → échec validation (400).
  * Par défaut, appelle `serializer = Serializer(instance, data=request.data)` puis `serializer.save()`.

### 4.4 **PATCH (Mise à jour partielle)**

* **PATCH /resources/{pk}/**

  * Ne nécessite d’envoyer **que** les champs modifiés.
  * Exemple payload minimal :

    ```json
    {
      "description": "Changement description"
    }
    ```
  * On doit utiliser `serializer = Serializer(instance, data=request.data, partial=True)`. DRF gère la différence dans `ListCreateAPIView` ou `ModelViewSet` automatiquement si on l’a configuré.

### 4.5 **DELETE (Suppression)**

* **DELETE /resources/{pk}/**

  * Supprime définitivement la ressource.
  * Par défaut, renvoie un **status 204 No Content** si tout s’est bien passé.
  * Penser à vérifier les permissions avant suppression.

---

## 5. **Filtres : affiner et rechercher dans les données**

### 5.1 **Installation et configuration de `django-filter`**

1. `pip install django-filter`
2. Ajouter dans `settings.py` :

   ```python
   INSTALLED_APPS = [
       # ...
       'django_filters',
   ]

   REST_FRAMEWORK = {
       'DEFAULT_FILTER_BACKENDS': [
           'django_filters.rest_framework.DjangoFilterBackend',
           'rest_framework.filters.SearchFilter',
           'rest_framework.filters.OrderingFilter',
       ],
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 10,
   }
   ```

### 5.2 **`DjangoFilterBackend` (filtrage par champ)**

* Dans la **View** ou le **ViewSet**, on déclare :

  ```python
  from django_filters.rest_framework import DjangoFilterBackend

  class ChildViewSet(viewsets.ModelViewSet):
      queryset = Child.objects.all()
      serializer_class = ChildSerializer
      filter_backends = [DjangoFilterBackend]
      filterset_fields = ['user_type', 'subscription', 'birthday']
  ```
* Exemples d’URL :

  * `/children/?user_type=3` → seuls les enfants du parent ID=3
  * `/children/?birthday=2020-06-01` → enfants nés à cette date

### 5.3 **`SearchFilter` (recherche textuelle)**

* Ajouter dans `filter_backends` avec `search_fields` :

  ```python
  from rest_framework.filters import SearchFilter

  class NurseryViewSet(viewsets.ModelViewSet):
      queryset = Nursery.objects.all()
      serializer_class = NurserySerializer
      filter_backends = [DjangoFilterBackend, SearchFilter]
      filterset_fields = ['manager']
      search_fields = ['name', 'address']
  ```
* Exemple :

  * `/nurseries/?search=Montpellier` → toutes les crèches contenant « Montpellier » dans `name` ou `address`.

### 5.4 **`OrderingFilter` (tri)**

* Ajouter dans `filter_backends` avec `ordering_fields` et éventuellement `ordering` par défaut :

  ```python
  from rest_framework.filters import OrderingFilter

  class ActivityViewSet(viewsets.ModelViewSet):
      queryset = Activity.objects.all()
      serializer_class = ActivitySerializer
      filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
      filterset_fields = ['type', 'date']
      search_fields = ['name', 'description']
      ordering_fields = ['date', 'created_at']
      ordering = ['date']  # tri par défaut
  ```
* Exemple :

  * `/activities/?ordering=-date` → liste des activités triées par date décroissante.

### 5.5 **Filtres avancés personnalisés**

Si l’on doit appliquer une logique métier plus complexe (ex : renvoyer uniquement les `OpeningHour` d’une crèche pour des jours ouvrés, exclure les jours fériés…), on peut :

1. **Surcharger `get_queryset()`** dans la vue ViewSet ou APIView :

   ```python
   class OpeningHourViewSet(viewsets.ModelViewSet):
       queryset = OpeningHour.objects.all()
       serializer_class = OpeningHourSerializer

       def get_queryset(self):
           nursery_id = self.kwargs.get('nursery_pk')
           queryset = super().get_queryset().filter(nursery_id=nursery_id)
           # Exemple : exclure les jours fermés
           return queryset.filter(is_closed=False)
   ```

2. **Créer un `FilterSet` plus fin** avec `django_filters` :

   ```python
   import django_filters

   class OpeningHourFilter(django_filters.FilterSet):
       start_day = django_filters.NumberFilter(field_name='day', lookup_expr='gte')
       end_day = django_filters.NumberFilter(field_name='day', lookup_expr='lte')

       class Meta:
           model = OpeningHour
           fields = ['nursery', 'is_closed']

   class OpeningHourViewSet(viewsets.ModelViewSet):
       queryset = OpeningHour.objects.all()
       serializer_class = OpeningHourSerializer
       filter_backends = [DjangoFilterBackend]
       filterset_class = OpeningHourFilter
   ```

   * On peut alors filtrer par `/opening_hours/?nursery=2&start_day=1&end_day=5`.

---

## 6. **Permissions : contrôler l’accès aux endpoints**

Les **Permissions** déterminent si un utilisateur authentifié ou non peut effectuer une action particulière.

### 6.1 Permissions standards intégrées

* `AllowAny` : aucun contrôle, tout le monde a accès
* `IsAuthenticated` : l’utilisateur doit être connecté
* `IsAdminUser` : l’utilisateur doit être staff (is\_staff=True)
* `IsAuthenticatedOrReadOnly` : méthodes GET/HEAD/OPTIONS accessibles à tous, mais autres méthodes (POST/PUT/DELETE) nécessitent d’être authentifié

#### Exemple dans une ViewSet

```python
from rest_framework.permissions import IsAuthenticated

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
```

### 6.2 Permissions personnalisées

Création d’une classe héritant de `BasePermission` :

```python
from rest_framework.permissions import BasePermission

class IsNurseryManager(BasePermission):
    message = "Vous devez être le manager de cette crèche pour accéder à cette ressource."

    def has_permission(self, request, view):
        # Vérifier que l'utilisateur est authentifié Django
        if not request.user.is_authenticated:
            return False
        return request.user.type == 'nursery_manager'

    def has_object_permission(self, request, view, obj):
        # Par exemple, vérifier que l'utilisateur est bien manager de la crèche liée
        return obj.manager == request.user
```

* `has_permission(self, request, view)` : appelé avant d’accéder à la vue, sur permission globale (list, create).
* `has_object_permission(self, request, view, obj)` : appelé sur actions d’objet (retrieve, update, delete), où `obj` est l’instance de modèle.

#### Application dans une vue

```python
class NurseryViewSet(viewsets.ModelViewSet):
    queryset = Nursery.objects.all()
    serializer_class = NurserySerializer
    permission_classes = [IsNurseryManager]

    def get_permissions(self):
        # Exemple : on veut que tout le monde puisse lister les crèches (même non-authentifiés)
        if self.action == 'list' or self.action == 'retrieve':
            return [AllowAny()]
        return super().get_permissions()
```

* `self.action` : méthode HTTP mappée (`list`, `retrieve`, `create`, `update`, `partial_update`, `destroy`).
* On personnalise les permissions selon l’action.

---

## 7. **Authentication : identifier l’utilisateur**

DRF supporte plusieurs systèmes d’authentification :

### 7.1 SessionAuthentication

* Base Django classique (cookie + session).
* Auth utilisé si on souhaite intégrer une partie Web classique (templates + API).
* Expose automatiquement `request.user` si la session est valide.

### 7.2 TokenAuthentication (simple)

1. Installer `rest_framework.authtoken`.
2. Dans `settings.py` :

   ```python
   INSTALLED_APPS += ['rest_framework.authtoken']
   REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
       'rest_framework.authentication.TokenAuthentication',
   ]
   ```
3. Générer un token pour chaque utilisateur (manuel ou via signal).
4. **Requête** : le client envoie dans l’header HTTP

   ```
   Authorization: Token <clé_du_token>
   ```
5. DRF authentifie l’utilisateur en associant `request.user`.

### 7.3 JWT (JSON Web Token)

* **Avantages** : plus sécurisé, expiration intégrée, possibilité de renvoyer `access` / `refresh` tokens.
* Bibliothèques courantes : `djangorestframework-simplejwt` ou `dj-rest-auth`.

#### Exemple avec `simplejwt`

1. `pip install djangorestframework-simplejwt`
2. Dans `settings.py` :

   ```python
   REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
       'rest_framework_simplejwt.authentication.JWTAuthentication',
   ]
   ```
3. Dans `urls.py` (routage des tokens) :

   ```python
   from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

   urlpatterns = [
       path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
       path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
       # ...
   ]
   ```
4. **Flux type** :

   * Client envoie `POST /api/token/` avec `{ "username": "user", "password": "pass" }`
   * Réponse : `{ "access": "...", "refresh": "..." }`
   * Pour chaque requête protégée, le client met :

     ```
     Authorization: Bearer <access_token>
     ```
   * Quand le token expire, le client fait `POST /api/token/refresh/` avec `{ "refresh": "<refresh_token>" }` → reçoit un nouveau `access`.

---

## 8. **Throttling : limiter le nombre de requêtes**

### 8.1 Classes de throttling standards

* `UserRateThrottle` : limite par utilisateur authentifié
* `AnonRateThrottle` : limite pour les utilisateurs non authentifiés (anonymes)
* `ScopedRateThrottle` : throttle par scope, défini dans la vue (utile pour différencier les endpoints)

### 8.2 Configuration globale dans `settings.py`

```python
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
]
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '10/minute',       # max 10 requêtes par minute pour IP anonyme
    'user': '1000/day',        # max 1000 requêtes par jour pour utilisateur authentifié
}
```

### 8.3 Throttle par scope dans une vue

```python
from rest_framework.throttling import ScopedRateThrottle

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'activities'

# Dans settings.py
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].update({
    'activities': '50/hour',  # 50 requêtes par heure sur cet endpoint
})
```

---

## 9. **Exemples de cas de figure courants et manipulations avancées**

### 9.1 Créer un endpoint read-only (pas de modifications autorisées)

```python
from rest_framework import viewsets

class NurseryReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Nursery.objects.all()
    serializer_class = NurserySerializer
    permission_classes = [AllowAny]  # accessible à tous en lecture
```

* Seuls `list` (GET collection) et `retrieve` (GET détail) sont disponibles.

### 9.2 Ajouter une action custom dans un ViewSet

Parfois, on souhaite exposer une action spécifique, par ex. : `/nurseries/{pk}/stats/`.

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class NurseryViewSet(viewsets.ModelViewSet):
    queryset = Nursery.objects.all()
    serializer_class = NurserySerializer

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request, pk=None):
        nursery = self.get_object()
        # Exemple : calculer le nombre d'enfants et d'activités
        total_children = sum([cls.groups.count() for cls in nursery.classrooms.all()])
        total_activities = nursery.activities.count()
        return Response({
            'nursery_id': nursery.id,
            'total_children': total_children,
            'total_activities': total_activities,
        })
```

* L’URL générée automatiquement par le router sera :

  ```
  GET /nurseries/{pk}/stats/
  ```

### 9.3 Pagination manuelle ou customisée

Dans `settings.py` :

```python
REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = 'rest_framework.pagination.PageNumberPagination'
REST_FRAMEWORK['PAGE_SIZE'] = 10
```

* Par défaut, tout `ListAPIView` ou `ModelViewSet` pagine automatiquement.
* Le client peut spécifier `?page=3` pour la 3ᵉ page.
* On peut définir une pagination plus fine, par ex. `LimitOffsetPagination` :

```python
from rest_framework.pagination import LimitOffsetPagination

class LargeResultsSetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    pagination_class = LargeResultsSetPagination
```

### 9.4 Gérer la mise à jour ou la suppression par lots (bulk)

DRF ne propose pas nativement le bulk update, mais on peut l’implémenter :

```python
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer

    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        """
        Exemple JSON d'entrée pour bulk_update :
        [
          { "id": 1, "first_name": "Alice Modifié" },
          { "id": 2, "last_name": "Dupont Modifié" }
        ]
        """
        updates = request.data
        if not isinstance(updates, list):
            return Response({"detail": "Liste attendue."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ChildSerializer(data=updates, many=True, partial=True)
        serializer.is_valid(raise_exception=True)

        for item in serializer.validated_data:
            child = Child.objects.get(pk=item['id'])
            for attr, value in item.items():
                setattr(child, attr, value)
            child.save()

        return Response({"detail": "Mise à jour par lots réussie."})
```

* La route sera `PATCH /children/bulk_update/`.

---

## 10. **Résumé de tous les cas de figure et manipulations**

| Élément                            | Cas de figure / Manipulation                                                                                                                                                                                                                                                                                                                  |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Serializer**                     | - `ModelSerializer` vs `Serializer`<br>- Champs `read_only`, `write_only`, `default`, `required`<br>- NestedSerializers pour relations complexes<br>- Overrider `validate_<field>` et `validate()`<br>- Overrider `create()` / `update()` pour logique métier                                                                                 |
| **View (APIView)**                 | - `get()`, `post()`, `put()`, `patch()`, `delete()`<br>- Gérer `404 Not Found` et `403 Forbidden`<br>- Vérification des permissions dans chaque méthode<br>- Utiliser `partial=True` pour `PATCH`                                                                                                                                             |
| **View (GenericAPIView + Mixins)** | - `ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`, `ListAPIView`, `CreateAPIView`<br>- Surcharge de `perform_create()` et `perform_update()`<br>- Gestion automatique de la sérialisation/validation                                                                                                                                      |
| **ViewSet**                        | - `ModelViewSet`, `ReadOnlyModelViewSet`, `GenericViewSet` avec `mixins`<br>- Surcharge de `get_queryset()` pour filtrage conditionnel selon l’utilisateur<br>- Actions custom (`@action(detail=True/False)`)                                                                                                                                 |
| **URLs**                           | - Routage manuel (`path`) vs `router.register()`<br>- Nested Routers pour ressources imbriquées (ex : `/nurseries/{pk}/opening_hours/`)                                                                                                                                                                                                       |
| **Requêtes GET**                   | - Liste (pagination, filtres, recherche, tri)<br>- Détail (gestion 404)                                                                                                                                                                                                                                                                       |
| **Requêtes POST**                  | - Création (validation, `serializer.save()`)<br>- Gestion des erreurs (400)                                                                                                                                                                                                                                                                   |
| **Requêtes PUT**                   | - Remplacement complet (nécessite tts les champs)<br>- Risque d’erreur 400 si champ manquant                                                                                                                                                                                                                                                  |
| **Requêtes PATCH**                 | - Mise à jour partielle (uniquement les champs modifiés)<br>- Utiliser `partial=True`                                                                                                                                                                                                                                                         |
| **Requêtes DELETE**                | - Suppression de l’objet (renvoie 204 No Content)<br>- Vérifier permissions avant suppression                                                                                                                                                                                                                                                 |
| **Filtres**                        | - `DjangoFilterBackend` (`filterset_fields` ou `filterset_class`)<br>- `SearchFilter` (`search_fields`)<br>- `OrderingFilter` (`ordering_fields`, `ordering`)<br>- Filtrage avancé dans `get_queryset()` ou `FilterSet` spécifique                                                                                                            |
| **Permissions**                    | - Intégrées : `AllowAny`, `IsAuthenticated`, `IsAdminUser`, `IsAuthenticatedOrReadOnly`<br>- Custom (`BasePermission`, `has_permission()`, `has_object_permission()`)<br>- `self.action` pour adapter selon CRUD                                                                                                                              |
| **Authentication**                 | - `SessionAuthentication` (cookies) ; `TokenAuthentication` (clé) ; `JWTAuthentication` (JSON Web Token)<br>- Endpoints d’obtention/rafraîchissement de token                                                                                                                                                                                 |
| **Throttling**                     | - Classes : `AnonRateThrottle`, `UserRateThrottle`, `ScopedRateThrottle`<br>- Configuration dans `settings.py` (`DEFAULT_THROTTLE_RATES`)<br>- `throttle_classes` et `throttle_scope` en vue pour cas spécifiques                                                                                                                             |
| **Pagination**                     | - `PageNumberPagination` (page=X)<br>- `LimitOffsetPagination` (limit=X\&offset=Y)<br>- Personnalisation via `pagination_class` par vue                                                                                                                                                                                                       |
| **Cas avancés**                    | - Bulk create/ update (custom actions)<br>- Nested serializers et relations profondes (ManyToMany avec création d’objets) ; ex : création simultanée de `Classroom` et `Group` imbriqués ; ex : `PrimaryKeyRelatedField(many=True)`.<br>- Override `perform_create()` pour ajouter automatiquement `request.user` ou d’autres champs calculés |

---

### 👉 **Conclusion**

* **Serializers** gèrent la validation et la transformation des données.
* **Views** (APIView, GenericAPIView, ViewSet) orchestrent la logique métier selon le type de requête.
* **URLs** (manuelles ou via Router) exposent vos endpoints de manière cohérente.
* **Filtrage, Recherche, Tri** se configurent via `filter_backends` et `django-filter`.
* **Permissions** et **Permissions personnalisées** assurent la sécurité et la séparation des droits.
* **Authentication** (Token, JWT) gère l’identité des utilisateurs.
* **Throttling** prévient les abus en limitant le nombre de requêtes.
* Chaque **type de requête HTTP** (GET/POST/PUT/PATCH/DELETE) suit un cycle précis de validation/sérialisation/sauvegarde et de réponse avec codes d’état appropriés.

À partir de ce socle, tu peux construire n’importe quel endpoint pour tes modules (`users`, `nurseries`, `classrooms`, etc.) en appliquant les exemples et patterns décrits. Si tu souhaites un exemple de code complet pour un module particulier (par ex. un `ViewSet` + `Serializer` + `URL` + filtres + permissions + throttling), fais-le moi savoir !
