from django import forms

class BagInfoForm(forms.Form):
    Source_Organization =       forms.CharField(max_length=100)
    External_Identifier =       forms.CharField(max_length=100)
    Internal_Sender_Description = forms.CharField(max_length=100)
    Title =                     forms.CharField(max_length=100)
    Date_Start =                     forms.CharField(max_length=100)
    Date_End =                     forms.CharField(max_length=100, required=False)
    Record_Creators =           forms.CharField(max_length=100)
    Record_Type =           forms.CharField(max_length=100)
    Language =             forms.URLField(max_length=200)
    Bagging_Date =          forms.CharField(max_length=100)
    Bag_Count =             forms.CharField(max_length=100,required=False)
    Bag_Group_Identifier=   forms.CharField(max_length=100,required=False)
    Payload_Oxum =              forms.CharField(max_length=100)
    BagIt_Profile_Identifier =  forms.URLField(max_length=200)
