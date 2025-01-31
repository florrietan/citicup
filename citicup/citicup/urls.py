from django.urls import include, path
from rest_framework import routers

from thm.views import RegisterAPIView, SearchFootprintAPIView,\
    SearchExchangeAPIView, LikeAPIView, Achievements,\
    WebPlogType, WebGoodType, WebLogin, WebRegister,\
    WebGood, ProcessReport, WebGetReport, Garbage,\
    CreditsModel, Calculate, CreditHouse, VoiceInteraction, ImageSearch
from zlh.views import UploadStepsAPIView, PostPlogAPIView,\
    ExchangeGoodAPIView, CommentMessageAPIView,\
    LikeMessageAPIView, ReportMessageAPIView
from mxy.views import LoginAPIView, GetAllGoodsAPIView, GoodTypeAPIView,\
    CategorizedGoodAPIView, GetAllPlogAPIView,\
    PlogTypeAPIView, CategorizedPlogAPIView,\
    GetPlogDetailsAPIView,SearchForPlogAPIView,SearchForGoodAPIView
from lj.views import GoodAPIView, UserPageAPIView, ReportAPIView,\
    CommentAPIView, UserPlogAPIView

router = routers.DefaultRouter()


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    # thm's part，记得打逗号！
    path('register/', RegisterAPIView.as_view()),  # 用户注册
    path('search_footprint/', SearchFootprintAPIView.as_view()),  # 查询某天碳足迹
    path('search_exchanges/', SearchExchangeAPIView.as_view()),  # 查询某天兑换记录
    path('like/', LikeAPIView.as_view()),  # 点赞plog
    path('achievements/', Achievements.as_view()),  # 查看成就，已完成步行者（金银铜）
    path('web/plog_type/', WebPlogType.as_view()),  # web端管理plogtype
    path('web/good_type/', WebGoodType.as_view()),  # web端管理goodtype
    path('web/login/', WebLogin.as_view()),  # web端的管理员账户登录
    path('web/register/', WebRegister.as_view()),  # web端的管理员账户注册
    path('web/good/', WebGood.as_view()),  # web端管理商品
    path('web/reports/', ProcessReport.as_view()),  # 处理举报消息
    path('web/get_report/', WebGetReport.as_view()),  # 获得所有未处理的举报
    path('garbage_classification/', Garbage.as_view()),  # 垃圾分类
    path('credits/', CreditsModel.as_view()),  # 获取用户的碳信用相关信息
    path('calculate/', Calculate.as_view()),  # 进行一次评估
    path('credit_house/', CreditHouse.as_view()),  # 获取信用等级
    path('voice/',VoiceInteraction.as_view()), #语音交互
    path('image_search/',ImageSearch.as_view()), #图片搜索
    # zlh's part,记得打逗号！
    path('wxsteps_upload/', UploadStepsAPIView.as_view()),  # 微信步数兑换
    path('good_exchange/', ExchangeGoodAPIView.as_view()),  # 商品兑换
    path('plog_post/', PostPlogAPIView.as_view()),  # 发布Plog
    path('message_comment/', CommentMessageAPIView.as_view()),  # 消息列表comment
    path('message_likes/', LikeMessageAPIView.as_view()),  # 消息列表likes
    path('message_report/', ReportMessageAPIView.as_view()),  # 消息列表report

    # mxy's part,记得打逗号！
    path('login/', LoginAPIView.as_view()),  # 用户登录
    path('store/', GetAllGoodsAPIView.as_view()),  # 商城页面获取全部商品
    path('good_type/', GoodTypeAPIView.as_view()),  # 获取商城中的商品分类
    path('categorized_good/', CategorizedGoodAPIView.as_view()),  # 获取某个分类的所有商品
    path('get_plog/', GetAllPlogAPIView.as_view()),  # 首页获取全部帖子
    path('plog_type/', PlogTypeAPIView.as_view()),  # 首页获取帖子分类
    path('categorized_plog/', CategorizedPlogAPIView.as_view()), # 首页获取某个分类的所有商品
    path('plog_details/', GetPlogDetailsAPIView.as_view()),  # 查看某条帖子详情页
    path('search_plog/', SearchForPlogAPIView.as_view()),  # 搜索帖子
    path('search_good/', SearchForGoodAPIView.as_view()),  # 搜索商品

    # lj's part,记得打逗号！
    path('good/', GoodAPIView.as_view()),  # 商品详情页
    path('user_page/', UserPageAPIView.as_view()),  # 用户个人页面
    path('report/', ReportAPIView.as_view()),  # 举报
    path('comment/', CommentAPIView.as_view()),  # 评论
    path('user_plogs/', UserPlogAPIView.as_view()),  # 用户发过的所有帖子
]
