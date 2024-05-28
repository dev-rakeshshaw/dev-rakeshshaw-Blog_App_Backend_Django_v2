from django.shortcuts import render,get_object_or_404
from django.http import Http404,JsonResponse
from .models import Post,Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.views.generic import ListView
from .forms import EmailPostForm,CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag,TaggedItem
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity


## Function to the all the post as a lists.
def post_list(request, tag_slug=None):
    posts_list = Post.objects.filter(status=Post.Status.PUBLISHED)

    tag = None
    if tag_slug:
        # tag = Tag.objects.get(slug=tag_slug)
        tag = get_object_or_404(Tag, slug=tag_slug)
        # print("This is the tag: ",tag)
        posts_list = posts_list.filter(tags__in=[tag])
        # print("This is related posts_list: ",posts_list )

    ##PAGINATION WITH 3 POSTS PER PAGE.

    #we will display 3 posts/page
    paginator = Paginator(posts_list,3) 

    #we retrive the page no. using GET method and if 
    #page parameter is not in the GET parameter of the 
    #request then we use the default value 1 to load the first page of results.
    page_number = request.GET.get("page",1)

    try:

        #we obtain the objects of the desired page by calling page() method.
        posts = paginator.page(page_number)

    # print("Previous Page num: ",posts.previous_page_number)
    # print("Current Page num: ",posts.number)
    # print("Total Page num: ",posts.paginator.num_pages)
    # print("Next Page num: ",posts.next_page_number)
    # print("Object List: ",posts.object_list)
    # print("*****************************************************************************************************************")

    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    posts_dict = {
            "posts":posts,
            'tag':tag,
            "posts_list":posts_list,
        }

    return render(request,"blog/post/list.html",context = posts_dict)


# Function to handle the details of a particular post.
def post_detail(request,year,month,day,slug):
    
    try:
        
        # print(f"{year} {month} {day} {slug}")
        post = Post.objects.get(publish__year=year, publish__month=month, publish__day=day, slug=slug, status=Post.Status.PUBLISHED)
        # post = Post.objects.get(publish__date="2023-9-6", slug=slug, status=Post.Status.PUBLISHED)        
        
        # post = post[0]
        # print(post)

        # List of active comments for this post
        comments = post.comments.filter(active=True)
        # Form for users to comment
        form = CommentForm()
 
        #Retrieving the list of ids of the tags related with this post.
        tag_id_list = post.tags.values_list("id",flat=True)
        print(tag_id_list)

        similar_posts = Post.objects.filter(tags__in=tag_id_list,status=Post.Status.PUBLISHED).exclude(id=post.id)
        print(similar_posts)

        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
        print(similar_posts)

        post_dict = {
            "post":post,
            "comments": comments,
            "form": form,
            'similar_posts': similar_posts,
         }

    except Post.DoesNotExist:
        raise Http404("No Post found.")
    return render(request,"blog/post/detail.html",context = post_dict)


# Function to handle sharing of a post via email.
def post_share(request, post_id):

    sent = False
    #Retrive post by id
    try:
        #Retrive post by id
        post = Post.objects.get(id=post_id, status=Post.Status.PUBLISHED)
        
        
    #     post_dict = {
    #     "post":post,
    # }
        if request.method == "POST":  
            """ If the request method is POST 
            that means Form was submitted and now 
            we have to process the data from the Form"""

            form = EmailPostForm(data=request.POST)
            # print("form:  ",form)

            if form.is_valid():
                #FORM fields passed validation
                cd = form.cleaned_data
                # print("cd:  ",cd)
                #...send email
            post_url = request.build_absolute_uri(post.get_absolute_url_for_urls_post_details())

            subject = f"{cd['name']} recommends you read {post.title}"
                     
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}" 
                      
            send_mail(subject, message, cd['email'],
                      [cd['to']])
            sent = True

        elif request.method == "GET":
            """ If the request method is GET 
            that means an empty form has to be displayed 
             to the user. """
            form = EmailPostForm()
        
        comfirm_dict = {'post': post, 'form': form, 'sent': sent}

    except Post.DoesNotExist:
        raise Http404("No Post found.")
    
    return render(request,'blog/post/share.html', context=comfirm_dict)



## Function to handle comments on the posts.
@require_POST
def post_comment(request,post_id):

    try:
        # print("Inside post_comment")
        #Retrive post by id
        post = Post.objects.get(id=post_id, status=Post.Status.PUBLISHED)
        # print(post)
        comment = None
                
        if request.method == "POST":
            """ If the request method is POST 
            that means Form was submitted and now 
            we have to process the data from the Form"""
            
            # A comment was posted
            form = CommentForm(data=request.POST)

            if form.is_valid():
                # Create a Comment object without saving it to the database
                comment = form.save(commit=False)
                # print(comment)
                # Assign the post to the comment
                comment.post = post
                # Save the comment to the database
                comment.save()

                

        confirm_dict = {'post': post, 'form': form, 'comment': comment}
        # print("Inside post_comment_8965")
    
    except Post.DoesNotExist:
        raise Http404("No Post found.")
    
    return render(request,"blog/post/comment.html",context=confirm_dict)


#To handle text-based search using postgresql
def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.filter(status=Post.Status.PUBLISHED).annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})



# To get all the comments related to a post.
def get_comments_for_post(request, post_id):
    comments = Comment.objects.filter(post_id=post_id)
    comments_data = [{'id': comment.id, 'body': comment.body} for comment in comments]
    return JsonResponse(comments_data, safe=False)

