import graphene
from graphene_django import DjangoObjectType
from .models import *
import random
from django.db.models import Q
import jwt
from functools import wraps
import datetime
from Graphene_API_Stockmarket_Project.settings import SECRET_KEY
from graphene_file_upload.scalars import Upload

#######################################
# PYjwt Token
def token_required(f):
    @wraps(f)
    def decorator(self, request, **kwargs):
       auth_Header = request.context.headers['Authentication']
       if auth_Header is None:
        raise Exception ("Auth token not provide !!")
       else:
        user_token = User_Token.objects.get (user_Token  = auth_Header)
        if user_token:
            return f(self,request,**kwargs)
        raise Exception("Please login Again you'r logged out!!!!")
    return decorator

#######################################
# DjangoObjectType

class User_Schema (DjangoObjectType):
    class Meta:
        fileds = "__all__"
        model = User

class Total_stocks_Schema (DjangoObjectType):
    class Meta:
        fileds = "__all__"
        model = Total_stocks


class User_wallet_Schema (DjangoObjectType):
    class Meta:
        fileds = "__all__"
        model = User_wallet

class User_buy (DjangoObjectType):
    class Meta:
        fields = "__all__"
        model = User_Buy

#######################################
# InputeobjectType

# userregistraton
class Userregistration (graphene.InputObjectType):
    user_Name = graphene.ID()
    user_Last_Name = graphene.String()
    user_Email = graphene.String()
    user_VerificationID = graphene.Int()
    user_Type_account = graphene.String()
    # user_Documentation = Upload()

# totalstockeentry
class Totalstockeentry (graphene.InputObjectType):
    stock_Name = graphene.String()
    stock_Price = graphene.Int()
    stock_Type = graphene.String()

# userbuyorsell
class Userbuy (graphene.InputObjectType):
    stock_Name = graphene.String()
    stock_Qty = graphene.Int()

#######################################
# Mutation 

#registration mutaion
class User_registration_mutation (graphene.Mutation):
    user_Schema = graphene.Field (User_Schema)

    class Arguments:
        userRegistration = Userregistration (required = True)
    
    msg = graphene.String()
    status = graphene.String()
    verificationID = graphene.String()

    def mutate (self,request,**kwargs):
        try:
            if User.objects.filter (user_Name = kwargs ['userRegistration'] ['user_Name']).exists():    
                msg = "User already registered! :("
                status = 409
                return User_registration_mutation (msg = msg , status = status)
            else:
                register = User(
                    user_Name = kwargs ['userRegistration'] ['user_Name'],
                    user_Last_Name = kwargs ['userRegistration'] ['user_Last_Name'],
                    user_Email = kwargs ['userRegistration'] ['user_Email'],
                    user_VerificationID = random.randrange(1000,5000),
                    user_Type_account = kwargs ['userRegistration'] ['user_Type_account'],
                    # user_Documentation = kwargs ['userRegistration'] ['user_Documentation'],
                )
                register.save()
                msg = "User register succesfully! :)"
                status = 200
                verificationID = register.user_VerificationID
                return User_registration_mutation (msg = msg , status = status, verificationID = verificationID)
        except Exception as e:
            print("User_registation_mutaion exception ",e)
            msg = "Please enter all required field! :("
            status = 400
            return User_registration_mutation (msg = msg , status = status)

# Total_stocks_entry
class Total_stocks_entry (graphene.Mutation):
    total_Stocks = graphene.Field (Total_stocks_Schema)

    class Arguments:
        tStocks = Totalstockeentry (required = True)
    
    msg = graphene.String()
    status = graphene.String()

    def mutate (self,request,**kwargs):
        try:
            if Total_stocks.objects.filter (stock_Name = kwargs ['tStocks'] ['stock_Name']).exists():
                msg = "Stock already registered! :("
                status = 409
                return Total_stocks_entry (msg = msg , status = status)
            else:
                stockRegistrate = Total_stocks(
                    stock_Name = kwargs ['tStocks'] ['stock_Name'],
                    stock_Price = kwargs ['tStocks'] ['stock_Price'],
                    stock_Type  = kwargs ['tStocks'] ['stock_Type'],
                )
                stockRegistrate.save()
                msg = "Stock register successfully! :)"
                status = 200
                return Total_stocks_entry (msg = msg , status = status)
        except Exception as e:
            print("Total_stocks_entry exception ",e)
            msg = "Please enter all register filed! :("
            status = 400
            return Total_stocks_entry (msg = msg, status = status)


# user login mutation
class User_login_mutation (graphene.Mutation):
    user_Schema = graphene.Field(User_Schema)

    class Arguments:
        username = graphene.String(required = True)
        verifyID = graphene.Int()

    msg = graphene.String()
    token = graphene.String()
    
    def mutate (self,request,**kwargs):
        user_check_list = User.objects.filter(user_Name = kwargs['username'],user_VerificationID = kwargs['verifyID'])
        if user_check_list:
            token = jwt.encode({'user_id':user_check_list[0].id,'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=5)},SECRET_KEY,'HS256')

            user  = User_Token.objects.filter (user  = User.objects.get (user_Name =  kwargs ['username'])).first()

            if user:
                user.user_Token = token
                user.save()
                msg = "Please provide this token all place"
                return User_login_mutation (msg = msg , token = token)
           
            else:            
                User_Token.objects.create (user = User.objects.get (user_Name = kwargs ['username']) , user_Token = token)
                print("first parameter::")

                # create wallet
                value = random.randrange(1,3,1)
                User_wallet.objects.create(user_Wallet = user_check_list.first(),user_Balance = 0,user_Maxlimit = str(value))
                
                msg = "Please provide this token all place"
                return User_login_mutation (msg = msg , token = token)

        msg = "Sorry, user or token not allow!!"
        return User_login_mutation (msg = msg )

# user stock buy or sell
class User_buy_stock (graphene.Mutation):
    user_buy = graphene.Field (User_buy)

    class Arguments:
        buy = Userbuy (required = True)

    msg = graphene.String()
    status = graphene.String()

    @token_required
    def mutate (self, request, **kwargs):
        try:
            if Total_stocks.objects.filter (stock_Name = kwargs ['buy'] ['stock_Name']).exists():
                stock_Name = kwargs ['buy'] ['stock_Name']
                stock_Qty = kwargs ['buy'] ['stock_Qty']

                wallet = User_wallet.objects.filter(user_Wallet = User.objects.get (id = jwt.decode(request.context.headers['Authentication'],SECRET_KEY,algorithms=['HS256'])['user_id'])).first()
                stock_price = Total_stocks.objects.filter (stock_Name = stock_Name).first() 
                if wallet.user_Balance <= stock_price.stock_Price * stock_Qty:
                    msg = "insufficiant balance! :(-"
                    return User_buy_stock (msg = msg, status = 409)

                # if User_Buy.objects.filter (sto_Name = Total_stocks.objects.filter (stock_Name = stock_Name).first() , ):
                    
                #     msg = "Stock already in! :)-"
                #     status = 405
                #     return User_buy_stock (msg = msg , status = status)
                user = User_Buy.objects.filter (sto_Name = Total_stocks.objects.get ( stock_Name = stock_Name),\
                user_ID  = User.objects.get (id = jwt.decode(request.context.headers['Authentication'],SECRET_KEY,algorithms=['HS256'])['user_id'])).first()
                
                if user:
                    
                    user.user_Stock_Qty = stock_Qty + user.user_Stock_Qty
                    user.save()
                    wallet.user_Balance =wallet.user_Balance -  (stock_Qty * stock_price.stock_Price)
                    wallet.save()
                    msg = "Stock add suucccccccessssssffffullly! :)-"
                    status = 200
                    return User_buy_stock (msg = msg, status = status)

                else:
                    User_Buy.objects.create(
                        user_ID = User.objects.get (id = jwt.decode(request.context.headers['Authentication'],SECRET_KEY,algorithms=['HS256'])['user_id']),
                        sto_Name = Total_stocks.objects.get (stock_Name = stock_Name),
                        user_Stock_Qty = stock_Qty,
                    )
                    wallet.user_Balance = wallet.user_Balance -  (stock_Qty * stock_price.stock_Price)
                    wallet.save()
                    msg = "Stock add suucccccccessssssffffullly! :)-"
                    status = 200
                    return User_buy_stock (msg = msg, status = status)
                
            else:
                msg = "sorrry,Your stock not listed!!! :(--"
                status = 404
                return User_buy_stock  (msg = msg , status = status)
        except Exception as e:
            print("User_buy_or_sell",e)
            msg = "Something went's wrong!!"
            status = 500, 400
            return User_buy_stock  (msg = msg , status = status)

# update stock api
class Sell_stock (graphene.Mutation):
    user_update = graphene.Field (User_buy)

    class Arguments:
        user_stock_name = graphene.String()
        user_stock_qty = graphene.Int()

    msg = graphene.String()
    status = graphene.String()

    @token_required
    def mutate (self,request,**kwargs):
        try:

            user_Portfolio = User_Buy.objects.filter (user_ID = User.objects.get (id =  jwt.decode(request.context.headers['Authentication'],SECRET_KEY,algorithms=['HS256'])['user_id']) ,\
                 sto_Name = Total_stocks.objects.get (stock_Name = kwargs['user_stock_name'])).first()

            user_Wallet  = User_wallet.objects.filter (user_Wallet = User.objects.get (id =  jwt.decode(request.context.headers['Authentication'],SECRET_KEY,algorithms=['HS256'])['user_id'])).first()
            
            if user_Portfolio:
               
                if user_Portfolio.user_Stock_Qty >= kwargs ['user_stock_qty'] :
                    
                    if user_Portfolio.user_Stock_Qty == kwargs ['user_stock_qty']:
                        user = User_Buy.objects.get(sto_Name = Total_stocks.objects.get (stock_Name = kwargs['user_stock_name']))
                        user.delete()
                        user_Wallet.user_Balance =user_Wallet.user_Balance +  (kwargs ['user_stock_qty'] * user_Portfolio.sto_Name.stock_Price)
                        print(user_Wallet.user_Balance +  (kwargs ['user_stock_qty'] * user_Portfolio.sto_Name.stock_Price))
                        user_Wallet.save()
                        msg = "Stock sell successfully! :(-"
                        status = 200
                        return Sell_stock (msg = msg, status = status)
                    else:
                        user_Portfolio.user_Stock_Qty = user_Portfolio.user_Stock_Qty+kwargs ['user_stock_qty'] 
                        user_Portfolio.save()
                        user_Wallet.user_Balance =user_Wallet.user_Balance -  (kwargs ['user_stock_qty'] * user_Portfolio.sto_Name.stock_Price)
                        user_Wallet.save()
                        print(user_Wallet.user_Balance +  (kwargs ['user_stock_qty'] * user_Portfolio.sto_Name.stock_Price))
                        msg = "Stock buy successfully! :(-"
                        status = 200
                        return Sell_stock (msg = msg, status = status) 
                
                else:
                    msg = "Unsufficiant quantity plese add valid number !!"
                    status = 409
                    return Sell_stock (msg = msg, status = status)
            else:
                msg = "No portfolio available for your name or No stock available!!"
                status = 400
                return Sell_stock (msg = msg, status = status)
        except Exception as e:
            print("Update user stock",e)
            msg = ("Something wents wrong!!",{}).formate(e)
            status = 400
            return Sell_stock (msg = msg , status = status)            

# add wallet balance
class Update_wallet_balance (graphene.Mutation):
    update_Wallet = graphene.Field (User_wallet_Schema)

    class Arguments:
        credit_debit = graphene.String()
        amount = graphene.Int()
    
    msg = graphene.String()
    status = graphene.String()

    @token_required
    def mutate (self, request ,**kwargs):
        try:
            user_Data = User_wallet.objects.get (user_Wallet = User.objects.get(id = jwt.decode(request.context.headers['Authentication'],SECRET_KEY,algorithms=['HS256'])['user_id']))
            if user_Data:
                credit_debit = kwargs ['credit_debit']
                amount = kwargs ['amount']

                if credit_debit == 'credit':
                    user_Data.user_Balance = amount + user_Data.user_Balance
                    user_Data.save()
                    msg = "amount Credit !! :)--"
                    status = 200
                    return Update_wallet_balance (msg = msg , status = status)
                else:
                    user_Data.user_Balance = amount - user_Data.user_Balance
                    user_Data.save()
                    msg = "amount Debit !! :)--"
                    status = 200
                    return Update_wallet_balance (msg = msg , status = status)              
                
            else:
                msg = "sorry user not available !! :)--"
                status = 200
                return Update_wallet_balance (msg = msg , status = status)    
        except Exception as e:
            print("Update_wallet_balance",e)
            msg = "something went's wrong {}".format(e)
            status = 200
            return Update_wallet_balance (msg = msg , status = status)  
                    

#######################################
# Schema defined

class Query (graphene.ObjectType):
    users = graphene.List (User_Schema)
    total_stocks = graphene.List (Total_stocks_Schema)
    wallet = graphene.List (User_wallet_Schema) 

    @token_required
    def resolve_users (self, request):
        return User.objects.all()
    
    def resolve_total_stocks (self, request):
        return Total_stocks.objects.all()
    
    @token_required
    def resolve_wallet (self, request):
        return User_wallet.objects.all()

class Mutation(graphene.ObjectType):
    user_registre = User_registration_mutation.Field()
    total_stocks = Total_stocks_entry.Field()
    user_login = User_login_mutation.Field()
    user_buy = User_buy_stock.Field()
    sell_stock = Sell_stock.Field()
    user_wallet_update = Update_wallet_balance.Field()

schema = graphene.Schema(query=Query, mutation = Mutation)