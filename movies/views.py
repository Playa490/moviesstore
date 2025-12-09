from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required

def rating_exceeds_max(movie_rating, max_rating):
    """Check if movie rating exceeds the user's max content rating"""
    rating_order = {'G': 0, 'PG': 1, 'PG-13': 2, 'R': 3}
    # If movie_rating is empty or None, default to showing it (treat as G)
    if not movie_rating:
        movie_rating = 'G'
    return rating_order.get(movie_rating, 0) > rating_order.get(max_rating, 3)

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    # Check user's max content rating preference
    max_rating = 'R'  # Default to R (show all)
    if request.user.is_authenticated:
        try:
            from accounts.models import UserProfile
            profile = UserProfile.objects.get(user=request.user)
            max_rating = profile.max_content_rating
        except:
            pass

    # Create a list of movies with their restriction status
    movies_with_restriction = []
    for movie in movies:
        is_restricted = rating_exceeds_max(movie.rating, max_rating)
        movies_with_restriction.append({
            'movie': movie,
            'is_restricted': is_restricted
        })

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies_with_restriction
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    
    # Check if user can access this movie based on their rating preference
    if request.user.is_authenticated:
        try:
            from accounts.models import UserProfile
            profile = UserProfile.objects.get(user=request.user)
            max_rating = profile.max_content_rating
            if rating_exceeds_max(movie.rating, max_rating):
                # Redirect to movies listing with a message
                from django.contrib import messages
                messages.warning(request, f'This movie ({movie.rating}) exceeds your content rating preference ({max_rating}).')
                return redirect('movies.index')
        except:
            pass
    
    reviews = Review.objects.filter(movie=movie)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

def top_comments(request):
  
    reviews = Review.objects.order_by("-likes")[:20]
    template_data = {}
    template_data['reviews'] = reviews
    return render(request, "movies/top_comments.html", {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

