from .models import Ratings, Article
from django.db.models import Avg


class Averages:
    def check_if_user_exists(self, user_id, article_id):
        user = Ratings.objects.filter(user_id=user_id, article=article_id)
        return user
    
    def query_ratings_table(self, article_id):
       rating = Ratings.objects.filter(article=article_id).aggregate(avg_rating=Avg('rating')) 
       return rating

    def update_avg_articles_table(self, article_id, rating):
        avg_rating = Article.objects.filter(id=article_id)[0]
        avg_rating.avg_rating = rating
        avg_rating.save()
        return rating


    def re_rate_articles(self, article_id, rating):
        re_rate = Ratings.objects.filter(article=article_id)[0]
        re_rate.rating = rating
        re_rate.save()
        return re_rate       

