from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Poll,Choice

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *

@api_view(['GET'])
def get_polls(request):
    print("=========== bIn get_polls")
    polls = Poll.objects.all()
    
    data = PollSerializer(polls, many=True).data
    return Response({
        "results": data
    })
@api_view(['GET'])
def get_choices(request):
    choices = Choice.objects.all()
    data = ChoiceSerializer(choices, many=True).data
    return Response({"results": data})

# def polls_list(request):
#     MAX_OBJECTS = 20
#     polls = Poll.objects.all()[:MAX_OBJECTS]
#     data = {"results": list(polls.values("question", "created_by__username", "pub_date"))}
#     return JsonResponse(data)

# def polls_detail(request, pk):
#     poll = get_object_or_404(Poll, pk=pk)
#     data = {"results": {
#         "question": poll.question,
#         "created_by": poll.created_by.username,
#         "pub_date": poll.pub_date
#     }}
#     return JsonResponse(data)

