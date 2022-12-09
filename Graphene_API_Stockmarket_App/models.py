from django.db import models
from django.core.validators import MinValueValidator

##########################################
# Stock market user

TYPE_ACCOUNT_CHOICE = (
    ("1","comodity"),
    ("2","index"),
)

class User(models.Model):
    user_Name = models.CharField(max_length=12)
    user_Last_Name = models.CharField(max_length=12)
    user_Email = models.EmailField(null=False)
    user_VerificationID = models.IntegerField()
    user_Type_account = models.CharField(choices=TYPE_ACCOUNT_CHOICE,max_length=12)
    user_Documentation = models.ImageField(upload_to="Images/")

    def __str__(self):
        return self.user_Name

    class Meta:
        ordering = ('-user_Name',)        
        verbose_name = 'user'
        verbose_name_plural = "User"
    

##########################################
# Total stocks

TYPE_OF_STOCKS = [
    ("1" , "Private_Bank"),
    ("2" , "Psu_Bank"),
    ("3" , "Consumers"),
    ("4" , "Industrys"),
    ("5" , "IT_sector"),
    ("6" , "oil_and_natural_gas"),
]

class Total_stocks(models.Model):
    stock_Name = models.CharField(max_length=12)
    stock_Price = models.IntegerField(validators=[MinValueValidator(1,'Minimum value is 1')])
    stock_Type = models.CharField(choices=TYPE_OF_STOCKS , max_length=12)

    def __str__(self):
        return self.stock_Name

    class Meta:
        ordering = ('stock_Type',)
        verbose_name = 'stock_Name'
        verbose_name_plural = 'stock_Price'

########################################
# User buy stocks and stock sell

class User_Buy (models.Model):
    user_ID = models.ForeignKey (User  ,on_delete=models.CASCADE, blank=True, null=True)
    sto_Name = models.ForeignKey(Total_stocks , on_delete=models.CASCADE )
    user_Stock_Qty = models.IntegerField()

    def __str__(self):
        return self.sto_Name.stock_Name

    class Meta:
        ordering = ('sto_Name',)
        verbose_name = 'User_stock_buy_or_sell'

#######################################
# Wallet

MAXIMUM_LIMIT = [
    ("1" , "50000"),
    ("2" , "100000")
]

class User_wallet (models.Model):
    user_Wallet = models.OneToOneField(User ,on_delete=models.CASCADE)
    user_Balance = models.IntegerField(validators=[MinValueValidator(0,'The field must contain at leaset 0 character')])
    user_Maxlimit = models.CharField(choices=MAXIMUM_LIMIT,max_length=12)
        

    def __str__(self):
        return self.user_Wallet.user_Name

    class Meta:
        ordering = ('user_Wallet' ,)
        verbose_name = 'user_Wallet'

#######################################
# Token store 

class User_Token (models.Model):    
    user = models.OneToOneField(User , on_delete=models.CASCADE )
    user_Token = models.CharField(max_length=300)

    def __str__(self):
        return self.user.user_Name