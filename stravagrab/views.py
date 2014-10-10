from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import facebook


def index(request):
    return render(request, 'index.html')

@login_required
def profile(request):
    user_social_auth = request.user.social_auth.filter(provider='facebook').first()
    graph = facebook.GraphAPI(user_social_auth.extra_data['access_token'])
    profile_data = graph.get_object("me")
    picture_data = graph.get_object("me/picture", width=200, limit=100)
    return render(request, 'profile.html', {'profile':profile_data, 'picture_url':picture_data})