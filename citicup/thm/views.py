from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from thm.achievements import walker, master_walker, rider, master_rider,\
    cutleryGuardian, traveler, master_traveler,\
    chop_collector, clothes, clothes_lover
import thm.GarbageClassification as GC
import hashlib
import time
import thm.credits as cmodel
import os

from bert_serving.client import BertClient
import speech_recognition as sr
import numpy as np

from werkzeug.utils import secure_filename
import shutil 
from thm.search import recommend
import tarfile
from datetime import datetime
from scipy import ndimage

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
from tensorflow.python.platform import gfile


class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data
        id = data['id']
        userName = data['userName']
        password = data['password']
        phoneNumber = data['phoneNumber']
        try:
            avatarPath = data['avatarPath']
        except ValueError:
            avatarPath = ""
        carbonCurrency = 0
        carbonCredit = 0
        cursor = connection.cursor()
        print(data)
        cursor.execute("insert into user(id,userName,password,phoneNumber,\
                       avatarPath,carbonCurrency,carbonCredit)\
                       values(%s,%s,%s,%s,%s,%s,%s)", [
                       id, userName, password, phoneNumber, avatarPath,
                       carbonCurrency, carbonCredit])
        print(JsonResponse.status_code)
        response = JsonResponse(data)
        res = JsonResponse.status_code
        response['Access-Control-Allow-Origin'] = '*'
        print(type(res))
        response = JsonResponse({"status_code": res})
        return response


class SearchFootprintAPIView(APIView):
    def get(self, request):
        data = request.query_params
        user_id = data['user_id']
        time = data['time']
        print(user_id, time)

        cursor = connection.cursor()
        cursor.execute("select * from PlogType")
        results = cursor.fetchall()
        plogType = {}
        for each in results:
            id = str(each[0])
            name = each[1]
            plogType[id] = name

        cursor.execute("select * from footprint\
                       where userid=%s and foottime>=%s and foottime<=%s",
                       [user_id, time+" 00:00:00", time+" 23:59:59"])
        results = cursor.fetchall()
        cnt = len(results)  # 记录个数
        print(cnt)
        list = []
        for each in results:
            dict = {}
            name = plogType[str(each[2])]
            dict["footprint_type_name"] = name
            dict["carbon_currency"] = each[3]
            dict["time"] = each[4]
            list.append(dict)

        response = JsonResponse(list, safe=False)
        return response


class SearchExchangeAPIView(APIView):
    def get(self, request):
        data = request.query_params
        user_id = data['user_id']
        time = data['time']

        cursor = connection.cursor()
        cursor.execute("select goodid from Exchanges\
                       where userid=%s and exchangetime>=%s\
                           and exchangetime<=%s", [
                       user_id, time+" 00:00:00", time+" 23:59:59"])
        results = cursor.fetchall()
        # 没有记录
        if len(results) == 0:
            return JsonResponse({})
        # 有记录
        list = []
        for each in results:
            good_id = each[0]
            cursor.execute("select * from good where id=%s", [good_id])
            results = cursor.fetchall()
            good_name = results[0][1]
            good_price = results[0][-3]
            dict = {"good_name": good_name, "good_price": good_price}
            list.append(dict)

        response = JsonResponse(list, safe=False)
        return response


class LikeAPIView(APIView):
    def post(self, request):
        data = request.data
        user_id = data['user_id']
        plog_id = data['plog_id']

        cursor = connection.cursor()
        cursor.execute("insert into likes (userid,plogid) values(%s,%s)", [
                       user_id, plog_id])

        response = JsonResponse(data)
        res = JsonResponse.status_code
        response['Access-Control-Allow-Origin'] = '*'
        response = JsonResponse({"status_code": res})
        return response


class Achievements(APIView):
    def get(self, request):
        data = request.query_params
        user_id = data['user_id']

        # thm的两类成就,函数记得要import
        num_walker = walker(user_id)  # 1.步行者
        num_master_walker = master_walker(user_id)  # 6.步行达人
        # lj's
        num_rider = rider(user_id)  # 2.骑行者，金银铜
        num_master_rider = master_rider(user_id)  # 7.骑行达人，金银铜
        # mxy's
        num_cg = cutleryGuardian(user_id)  # 3.餐具卫士，金银铜
        num_traveler = traveler(user_id)  # 4.未来旅客，金银铜
        num_master_traveler = master_traveler(user_id)  # 9.步未来旅行家，金银铜
        # zlh's
        num_chop = chop_collector(user_id)  # 8.餐具收藏家 #####
        num_clothes = clothes(user_id)  # 5.爱心使者 #####
        num_master_clothes = clothes_lover(user_id)  # 10.爱心大使 #####

        return JsonResponse([num_walker, num_rider, num_cg, num_traveler,
                            num_clothes, num_master_walker, num_master_rider,
                            num_chop, num_master_traveler, num_master_clothes],
                            safe=False)


class WebPlogType(APIView):
    def get(self, request):
        data = request.query_params
        id = data.get('id', None)
        cursor = connection.cursor()
        sql = "select id,typeName,typeCarbonCurrency from plogType\
            where id =%s"
        cursor.execute(sql, [id])
        connection.commit()
        results = cursor.fetchall()
        try:
            result = results[0]
        except ValueError:
            return JsonResponse({"status_code": JsonResponse.status_code})

        response = []
        response.append(
            {'id': result[0], 'typeName': result[1],
             'typeCarbonCurrency': result[2]})
        cursor.close()
        return JsonResponse(response, safe=False)

    def post(self, request):
        data = request.data
        type_name = data['type_name']
        type_coin = data['type_coin']
        if type_coin is None:
            return JsonResponse({"error_tip": "汇率应为数字"})

        cursor = connection.cursor()
        cursor.execute("insert into plogtype (typename,typecarboncurrency)\
            values(%s,%s)", [type_name, type_coin])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response

    def put(self, request):
        data = request.data
        type_name = data['type_name']
        type_coin = data['type_coin']
        if type_coin is None:
            return JsonResponse({"error_tip": "汇率应为数字"})

        id = data['id']
        cursor = connection.cursor()

        if type_name != "":
            cursor.execute(
                "update plogtype set typename=%s where id=%s", [type_name, id])
        if type_coin != "":
            cursor.execute(
                "update plogtype set typeCarbonCurrency=%s where id=%s",
                [type_coin, id])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response

    def delete(self, request):
        data = request.query_params
        id = data.get('id')
        cursor = connection.cursor()
        cursor.execute("delete from plogtype where id=%s", [id])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response


class WebGoodType(APIView):
    def get(self, request):
        data = request.query_params
        id = data.get('id')
        cursor = connection.cursor()
        sql = "select id,goodtypename from goodtype where id =%s"
        cursor.execute(sql, [id])
        connection.commit()
        results = cursor.fetchall()
        try:
            result = results[0]
        except ValueError:
            return JsonResponse({"status_code": JsonResponse.status_code})

        response = []
        response.append({'id': result[0], 'typeName': result[1]})
        cursor.close()
        return JsonResponse(response, safe=False)

    def post(self, request):
        data = request.data
        type_name = data['type_name']
        cursor = connection.cursor()
        cursor.execute(
            "insert into goodtype (goodtypename) values(%s)", [type_name])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response

    def put(self, request):
        data = request.data
        type_name = data['type_name']
        id = data['id']
        cursor = connection.cursor()

        if type_name != "":
            cursor.execute(
                "update goodtype set goodtypename=%s where id=%s",
                [type_name, id])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response

    def delete(self, request):
        data = request.query_params
        id = data.get('id')
        cursor = connection.cursor()
        cursor.execute("delete from goodtype where id=%s", [id])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response


class WebRegister(APIView):
    def post(self, request):
        data = request.data
        id = data['id']
        userName = data['user_name']
        password = data['password']

        cursor = connection.cursor()

        cursor.execute("select id from adminuser where id=%s", [id])
        results = cursor.rowcount
        if results == 1:
            return JsonResponse({"error_tip": "改用户id已被注册"})

        cursor.execute("insert into adminuser(id,adminuserName,password)\
            values(%s,%s,%s)", [id, userName, password])

        response = JsonResponse(data)
        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response

# 给 token 进行加密处理


def token_md5(user):
    ctime = str(time.time())  # 当前时间
    m = hashlib.md5(bytes(user, encoding="utf-8"))
    m.update(bytes(ctime, encoding="utf-8"))  # 加上时间戳
    return m.hexdigest()


class WebLogin(APIView):
    def post(self, request):
        data = request.data
        print(data)
        id = data['id']
        password = data['password']
        cursor = connection.cursor()
        cursor.execute(
            "select id,password from adminuser where id=%s and password=%s",
            [id, password])
        results = cursor.rowcount
        if results == 1:
            token = token_md5(id)
            return JsonResponse({"ifSuccess": True, "token": token})
        else:
            return JsonResponse({"ifSuccess": False})


class WebGood(APIView):
    def post(self, request):
        data = request.data
        print(data)
        good_name = data["good_name"]
        print(good_name)
        good_type = data['good_type']
        good_description = data['good_description']
        good_carboncurrency = data['good_carboncurrency']
        good_left = data['good_left']
        image_path = data['image_path']

        cursor = connection.cursor()
        cursor.execute("insert into good (goodname,goodtype,gooddescription,\
                        goodcarboncurrency,goodleft,imagepath)\
                        values(%s,%s,%s,%s,%s,%s)", [good_name, good_type,
                                                     good_description,
                                                     good_carboncurrency,
                                                     good_left, image_path])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response

    def put(self, request):
        data = request.data
        good_name = data['good_name']
        good_type = data['good_type']
        good_description = data['good_description']
        good_carboncurrency = data['good_carboncurrency']
        good_left = data['good_left']
        image_path = data['image_path']
        id = data['id']

        cursor = connection.cursor()
        cursor.execute("update good set goodname=%s,goodtype=%s,\
            gooddescription=%s,goodcarboncurrency=%s,goodleft=%s,imagepath=%s\
                where id=%s", [
                       good_name, good_type, good_description,
                       good_carboncurrency, good_left, image_path, id])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response

    def delete(self, request):
        data = request.query_params
        id = data.get('id')

        cursor = connection.cursor()
        cursor.execute("delete from good where id=%s", [id])

        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response


class ProcessReport(APIView):
    def post(self, request):
        data = request.data
        report_id = data['report_id']
        admin_user = data['admin_user']
        result = data['result']
        result_detail = data['result_detail']

        cursor = connection.cursor()
        cursor.execute("insert into reportprocess \
            (reportid,adminuser,result,resultdetail) values(%s,%s,%s,%s)", [
                       report_id, admin_user, result, result_detail])

        cursor.execute("select plogid from reports where id=%s", [report_id])
        results = cursor.fetchall()
        plog_id = results[0][0]  # int

        if int(result) == 1:
            cursor.execute(
                "select userid,plogname from plog where id=%s", [plog_id])
            results = cursor.fetchall()
            user_id = results[0][0]  # string
            plog_name = results[0][1]
            print(plog_name)

            cursor.execute("update plog set plogname=%s,plogcontent=%s,\
                imagepath=%s where id=%s", [
                           "这条帖子不见了噢", "这条帖子不见了噢", "", plog_id])
            cursor.execute(
                "update user set carboncurrency=carboncurrency-100\
                    where id=%s", [user_id])
            cursor.execute(
                "insert into footprint (userid,plogtypeid,carboncurrency)\
                    values(%s,10,%s)", [user_id, -100])

        cursor.execute(
            "update reports set status=1 where plogid=%s", [plog_id])
        res = JsonResponse.status_code
        response = JsonResponse({"status_code": res})
        return response


class WebGetReport(APIView):
    def get(self, request):
        cursor = connection.cursor()
        cursor.execute("select * from reports where status=0")
        results = cursor.fetchall()
        list = []
        for each in results:
            dict = {}
            dict['report_id'] = each[0]
            dict['reporter'] = each[1]
            dict['report_content'] = each[4]
            dict['plog_id'] = each[2]
            cursor.execute("select * from plog where id=%s", [dict['plog_id']])
            plog = cursor.fetchall()[0]
            dict['plog_name'] = plog[5]
            dict['plog_content'] = plog[6]
            dict['poster'] = plog[1]
            list.append(dict)

        print(list)

        res = JsonResponse.status_code
        print(res)
        response = JsonResponse(list, safe=False)
        return response

# 垃圾分类
# 发布Plog


class Garbage(APIView):
    def post(self, request):
        data = request.data
        print(data)
        file = request.FILES.get('file')
        # file_dir = os.path.join(os.getcwd(), 'upload_images')
        # file_path = os.path.join(file_dir, image_name)

        pred = GC.predict_img(file)
        print(pred)
        # print(img) # raw数据存入upload_files文件夹中
        return JsonResponse({'result': pred})


class CreditsModel(APIView):
    def get(self, request):
        data = request.query_params
        user_id = data["user_id"]

        cursor = connection.cursor()
        dict = {"old": [], "new": []}

        # order by time    desc
        cursor.execute(
            "select * from carboncredits where userid=%s order by date desc",
            [user_id])
        res = cursor.fetchall()
        if len(res) == 1:
            dict['old'] = ["-", "0", "0%", "0%", "0%", "0%", "0%"]
        else:
            old = res[1]
            print(old)
            dict['old'].append(str(old[1]))
            dict['old'].append(str(old[2]))
            for i in range(3, 8):
                s = round(old[i]*100, 2)
                s = str(s)+"%"
                dict['old'].append(s)

        new = res[0]
        dict['new'].append(str(new[1]))
        dict['new'].append(str(new[2]))
        for i in range(3, 8):
            s = round(new[i]*100, 2)
            s = str(s)+"%"
            dict['new'].append(s)

        print(dict)
        return JsonResponse(dict)


class CreditHouse(APIView):
    def get(self, request):
        data = request.query_params
        user_id = data["user_id"]

        cursor = connection.cursor()
        cursor.execute("select carboncredit from user where id=%s", [user_id])
        cre = cursor.fetchone()[0]
        if cre >= 90:
            level = 3
        elif cre >= 60:
            level = 2
        else:
            level = 1

        return JsonResponse({'level': level})


class Calculate(APIView):
    def get(self, request):
        cmodel.evaluate()
        return JsonResponse({'result': "本次碳信用评估已完成"})

class VoiceInteraction(APIView):
    def get(self,request):
        r = sr.Recognizer()
        bc = BertClient(ip='139.224.100.23')# ip中是部署了bert模型的服务器地址
        stc = [
            "为我解读一下我这个月的碳信用",
            "我现在有多少碳币",
            "我的碳信用分数是多少",
        ]
        vec = []
        input_vec = []
        print(os.getcwd())
        vec = np.load('./thm/bert_vec.npy')

        # 录音、识别
        print("您可以向我查询碳币、碳信用等等..."+'\n'+'请说话：')
        microphone = sr.Microphone()
        with microphone as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            print('录音结束')
            # sentence = r.recognize_sphinx(audio)
            input_sentence = r.recognize_google(audio,language="cmn-Hans-CN") #简体中文
            print('识别结束')
            # 计算用户说的句子的bert向量
            input_vec = bc.encode([input_sentence])
            print(input_sentence)
        except:
            print("无法识别出句子，请重试。")
            return JsonResponse({'index': 1})

        
        # 将输入句子的向量与预设句子的向量一一求出余弦值，与余弦值最大的匹配成功
        cos_input = []
        for each in vec:
            each = each.reshape(768,1)
            res = input_vec.dot(each) / (np.linalg.norm(input_vec) * np.linalg.norm(each))
            res = (res[0][0])
            cos_input.append(res)
        print(cos_input)
        index = cos_input.index(max(cos_input))
        print('检测到输入应为预设库中的第'+str(index+1)+'条，“',stc[index]+'”')
        #cos_input = a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b))
        print(index)
        return JsonResponse({'index': index})

class ImageSearch(APIView):
    def get(self,request):
        file = request.FILES.get('file')
        result = 'static/result'
        if not gfile.Exists(result):
            os.mkdir(result)
        shutil.rmtree(result)

        extracted_features=np.zeros((10000,2048),dtype=np.float32)
        with open('saved_features_recom.txt') as f:
                    for i,line in enumerate(f):
                        extracted_features[i,:]=line.split()
        print("loaded extracted_features") 

        if file:# and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            inputloc = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            recommend(inputloc, extracted_features)
            os.remove(inputloc)
            image_path = "/result"
            image_list =[os.path.join(image_path, file) for file in os.listdir(result)
                              if not file.startswith('.')]
            images = {
                'image0':image_list[0],
                'image1':image_list[1]
		    }				

        
        cursor = connection.cursor()
        sql = "select id,goodName,goodType,goodCarbonCurrency,imagePath\
              from good"
        cursor.execute(sql)
        connection.commit()
        results = cursor.fetchall()
        good_list = []
        for good in results:
            good_item = {}
            good_item["id"] = good[0]
            good_item["goodName"] = good[1]
            good_item["goodType"] = good[2]
            good_item["goodCarbonCurrency"] = good[3]
            good_item["imagePath"] = good[4]
            good_list.append(good_item)
        cursor.close()
        res = JsonResponse.status_code
        if res == 200:
            response = JsonResponse(good_list, safe=False)
            return response
        else:
            return JsonResponse({"status_code": res}) 