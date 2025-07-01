from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from .views import NurseryViewSet, NurseryAssistantViewSet, NurseryGetViewSet
from apps.classrooms.views import ClassroomViewSet, GroupViewSet
from apps.activities.views import ActivityViewSet, ClassroomActivityViewSet
from apps.subscriptions.views import PlanViewSet, SubscriptionViewSet, MySubscriptionViewSet, GetPlanViewSet

router = DefaultRouter()
router.register(r'nursery', NurseryViewSet, basename='nursery')
router.register(r'mynursery', NurseryGetViewSet, basename='mynursery')

nursery_router = NestedDefaultRouter(router, r'nursery', lookup='nursery')
nursery_router.register(r'assistants', NurseryAssistantViewSet, basename='nursery-assistant')
nursery_router.register(r'plans', PlanViewSet, basename='nursery-plan')
nursery_router.register(r'classrooms', ClassroomViewSet, basename='nursery-classroom')
nursery_router.register(r'activities', ActivityViewSet, basename='nursery-activity')

mynursery_router = NestedDefaultRouter(router, r'mynursery', lookup='mynursery')
mynursery_router.register(r'myplans', GetPlanViewSet, basename='mynursery-plan')

classroom_router = NestedDefaultRouter(nursery_router, r'classrooms', lookup='classroom')
classroom_router.register(r'groups', GroupViewSet, basename='classroom-group')
classroom_router.register(r'activities', ClassroomActivityViewSet, basename='classroom-activity')

plan_router = NestedDefaultRouter(nursery_router, r'plans', lookup='plans')
plan_router.register(r'subscriptions', SubscriptionViewSet, basename='plans-subscription')

router.register(r'mysubscriptions', MySubscriptionViewSet, basename='plans-subscription-get')

urlpatterns = (
    router.urls +
    nursery_router.urls +
    classroom_router.urls +
    plan_router.urls +
    mynursery_router.urls
)
