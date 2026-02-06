from django.urls import path
from .views import *
#from .apiviews import PollList, PollDetail,get_polls


urlpatterns = [
    #path("polls/", polls_list, name="polls_list1"),
    #path("polls/<int:pk>/", polls_detail, name="polls_detail1"),

    path("polls/", get_polls, name="polls_list"),
    path("choice/", get_choices, name="get_choices"),

    #path("polls/", PollList.as_view(), name="polls_list"),
    #path("polls/<int:pk>/", PollDetail.as_view(), name="polls_detail")
]