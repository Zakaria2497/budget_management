from django.shortcuts import render

from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required

from transaction_management.models import *
from decimal import Decimal
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.contrib import messages

@login_required
def dashboard(request): 

    all_accounts = Account.objects.all().order_by("-id")[:5]
    all_transfers = Transfer.objects.all().order_by("-id")[:5]
    context = {
     
        "all_accounts": all_accounts,
        "all_transfers": all_transfers,
       
    }
    return render(request, "dashboard.html", context)

################
### ACCOUNTS ###
################
def all_account(request): 
   
    all_accounts = Account.objects.all()    

    if request.method == "POST":
        data = request.POST
        if not data["search"] :
            return redirect('/transaction/accounts')
        else:
            content=all_accounts.filter(name__icontains=data["search"])

            context = {
                "content":content,
            }
            return render(request, "acc_search.html", context)
     
    context = {
        "all_accounts": all_accounts,
    }
    return render(request, "all_account.html", context)

def add_account(request): #complete, not tested
    
    return render(request, "add_new_acc.html")

def add_account_processing(request): #complete, not tested
    if request.method != "POST":
        return redirect("/transaction/accounts")
    form = request.POST
   
    Account.objects.create(name=form["name"], alloted=form["alloted"], actual_recieved=form['actual_recieved'], acc_balance=form["actual_recieved"])
    
    return redirect("/transaction/accounts")

   


def edit_account(request, pk): ### DO NOT USE ###
   
    acc_to_edit = Account.objects.get(id=pk)
    history = History.objects.filter(account__id=pk)
   
    context = {
        "acc_to_edit": acc_to_edit,
        "all_history":history,
    }
    return render(request, "edit_account.html", context)

def edit_account_processing(request,pk): #complete, not tested
    if request.method != "POST":
        return redirect("/transaction/accounts")    

    acc_update = Account.objects.get(id=pk)    
    form = request.POST
    
    if form["alloted"]:
        alloted = Decimal(form["alloted"])
    else:
        alloted = acc_update.alloted
    if form["actual_recieved"]:
        actual= Decimal(form["actual_recieved"])
    else:
        actual = acc_update.actual_recieved            
    History.objects.create(account=acc_update,update_name=form["name"], alloted=alloted,actual_recieved=actual)
    
    if form["name"]:
        acc_update.name = form["name"]
    else:
        acc_update.name = acc_update.name    


    if form["alloted"]:
        if Decimal(form["alloted"]) > acc_update.actual_recieved:
            req_alloted = request.POST["alloted"]
            edit_alloted = Decimal(req_alloted) - acc_update.alloted
            # acc_update.alloted = form["alloted"]
            acc_update.alloted = acc_update.alloted + edit_alloted
    else:
        acc_update.alloted = acc_update.alloted

    if form["actual_recieved"]:
        req_actual_amount = request.POST["actual_recieved"]
        edit_actual_amount = Decimal(req_actual_amount) - acc_update.actual_recieved
        
        acc_update.actual_recieved = acc_update.actual_recieved + edit_actual_amount 
        acc_update.acc_balance = acc_update.acc_balance + edit_actual_amount
        acc_update.total_after_adjustment = acc_update.acc_balance
        # acc_update.adjusted = acc_update.adjusted + edit_actual_amount


    else:
        acc_update.actual_recieved = acc_update.actual_recieved        

    acc_update.save()
    return redirect("/transaction/accounts")     


## Detail View of an account Zakaria
        
def view_an_acount(request,pk):
    
    all_trans_debit = Transfer.objects.filter(debit_acc__pk=pk)
    all_trans_credit = Transfer.objects.filter(credit_acc__pk=pk)

    context = {
        "all_trans_debit" : all_trans_debit ,
        "all_trans_credit" : all_trans_credit,
    }

    return render(request, "acc_detail.html", context)

def delete_an_account(request,pk):
    obj =  get_object_or_404(Account, id =pk)
    if request.method == "POST":
        print("I am deleteing")
        obj.delete()
        return redirect("/transaction/accounts")
    context = {
        "object" : obj,
    }      
    return render(request, "delete_acc.html", context)  
   
################
### TRANSFER ###
################

def all_transfer(request): 
    all_transfers = Transfer.objects.all().order_by("-id")

    if request.method == "POST":
        data = request.POST
        if not data["search"] :
            return redirect('/transaction/transfers')
        else:
            content=all_transfers.filter(debit_acc__name__icontains=data["search"])

            context = {
                "content":content,
            }
            return render(request, "trans_search.html", context)
    context = {
        "all_transfers": all_transfers,
    }
    return render(request, "all_trans.html", context)



def new_transfer(request): #complete, not tested
    all_accounts = Account.objects.all()

    context = {
        "all_accounts": all_accounts,
    }
    return render(request, "add_transfer.html",context)

def new_transfer_processing(request): #complete, not tested
    if request.method != "POST":
        return redirect("/transaction/transfers")
    else:
        acc_to_debit = Account.objects.filter(name=request.POST["debit_acc"]).first()
        acc_to_credit = Account.objects.filter(name=request.POST["credit_acc"]).first()  
        if acc_to_credit.id != acc_to_debit.id:
            if acc_to_debit.alloted == acc_to_debit.acc_balance:

                req_amount = Decimal(request.POST["amount"])


                if req_amount > acc_to_debit.alloted:  
                    # messages.error(request,"Oops___something bad happend")
                    messages.error(request,"f'{req_amount} exceeds transaction of RDPP {acc_to_debit.name} (DBT {acc_to_debit.alloted})'")
                    # raise ValidationError(f'{trans_debit.amount} in addition with previous total {total_debit["amount__sum"]} exceeds transaction of RDPP {trans_debit.debit_acc} (DBT {trans_debit.debit_acc.alloted})')
                    return redirect("/transaction/transfers/new")

                
                elif req_amount + acc_to_credit.acc_balance > acc_to_credit.alloted:
                    messages.error(request,"f'{req_amount} in addition with previous total exceeds total allotment of RDPP {acc_to_credit.name} (DBT {acc_to_credit.alloted})'")
                    return redirect("/transaction/transfers/new")
                    # raise ValidationError(f'{transfer.amount}  Money Receive====== n addition with previous total {total["amount__sum"]} exceeds transaction of RDPP {transfer.credit_acc} (DBT {transfer.credit_acc.alloted})')
                
                else:
                    Transfer.objects.create(vendor=acc_to_debit.name, description=request.POST["description"],\
                    amount=request.POST["amount"], debit_acc=acc_to_debit, credit_acc=acc_to_credit)
                
                
                    acc_to_debit.acc_balance = (acc_to_debit.acc_balance - Decimal(request.POST["amount"]))
                    acc_to_debit.total_after_adjustment = acc_to_debit.acc_balance
                    acc_to_debit.adjusted = (Decimal(acc_to_debit.adjusted) - Decimal(request.POST["amount"]))
                    acc_to_debit.amount = (Decimal(request.POST["amount"]))
                    acc_to_debit.save()
                
                    ### apply credit to credit acc ###
                    acc_to_credit.acc_balance = (acc_to_credit.acc_balance + Decimal(request.POST["amount"]))
                    acc_to_credit.total_after_adjustment = acc_to_credit.acc_balance
                    acc_to_credit.adjusted = (Decimal(acc_to_credit.adjusted) + Decimal(request.POST["amount"]))
                    acc_to_credit.amount = (Decimal(request.POST["amount"]))
                    acc_to_credit.save() 

                    print("Second block working")
                
                    return redirect("/transaction/transfers")
                   

            
            else:
                req_amount = Decimal(request.POST["amount"])
                if req_amount > acc_to_debit.acc_balance:

                    messages.error(request,f'{req_amount} exceeds transaction of RDPP {acc_to_debit.name} (DBT {acc_to_debit.acc_balance})')
                    # raise ValidationError(f'{trans_debit.amount} in addition with previous total {total_debit["amount__sum"]} exceeds transaction of RDPP {trans_debit.debit_acc} (DBT {trans_debit.debit_acc.acc_balance})')
                    return redirect("/transaction/transfers/new")
                
                elif req_amount + acc_to_debit.acc_balance > acc_to_debit.alloted:  
                    messages.error(request,f'{req_amount}  in addition with previous total exceeds total allotment of RDPP {acc_to_debit.name} (DBT {acc_to_debit.alloted})')
                    # raise ValidationError(f'{trans_debit.amount} in addition with previous total {total_debit["amount__sum"]} exceeds transaction of RDPP {trans_debit.debit_acc} (DBT {trans_debit.debit_acc.alloted})')
                    return redirect("/transaction/transfers/new")

                elif req_amount + acc_to_credit.acc_balance > acc_to_credit.alloted:
                    messages.error(request,f'{req_amount}  in addition with previous total exceeds total allotment of RDPP {acc_to_credit.name} (DBT {acc_to_credit.alloted})')
                    return redirect("/transaction/transfers/new")
                    # raise ValidationError(f'{transfer.amount}  Money Receive====== n addition with previous total {total["amount__sum"]} exceeds transaction of RDPP {transfer.credit_acc} (DBT {transfer.credit_acc.alloted})')
                
                else:
                    Transfer.objects.create(vendor=acc_to_debit.name, description=request.POST["description"],\
                    amount=request.POST["amount"], debit_acc=acc_to_debit, credit_acc=acc_to_credit)
                
                
                    acc_to_debit.acc_balance = (acc_to_debit.acc_balance - Decimal(request.POST["amount"]))
                    acc_to_debit.total_after_adjustment = acc_to_debit.acc_balance
                    acc_to_debit.adjusted = (Decimal(acc_to_debit.adjusted) - Decimal(request.POST["amount"]))
                    acc_to_debit.amount = (Decimal(request.POST["amount"]))
                    acc_to_debit.save()
                
                    ### apply credit to credit acc ###
                    acc_to_credit.acc_balance = (acc_to_credit.acc_balance + Decimal(request.POST["amount"]))
                    acc_to_credit.total_after_adjustment = acc_to_credit.acc_balance
                    acc_to_credit.adjusted = (Decimal(acc_to_credit.adjusted) + Decimal(request.POST["amount"]))
                    acc_to_credit.amount = (Decimal(request.POST["amount"]))
                    acc_to_credit.save()

                    return redirect("/transaction/transfers")
        else:            
            messages.error(request,"You are trying to send money to same RDPP Head")
            return redirect("/transaction/transfers/new")



def edit_transfer(request, pk):
    transfer=Transfer.objects.get(id=pk)
    
    acc_to_debit = Account.objects.get(name=transfer.debit_acc)
    acc_to_credit = Account.objects.get(name=transfer.credit_acc) 

    if request.method == "POST":
        form = request.POST
        req_amount = Decimal(request.POST["amount"])
        # edit_amount = 0
        edit_amount = req_amount - transfer.amount 
        # if req_amount > transfer.amount:
        #     edit_amount = req_amount - transfer.amount 
        # else:
        #     edit_amount = - req_amount    

        if req_amount > acc_to_debit.acc_balance:

            messages.error(request,"Edit amount exceeds Budget")
            # raise ValidationError(f'{trans_debit.amount} in addition with previous total {total_debit["amount__sum"]} exceeds transaction of RDPP {trans_debit.debit_acc} (DBT {trans_debit.debit_acc.acc_balance})')
            return redirect(f"/transaction/transfer/edit/{transfer.id}")
        
        elif req_amount + acc_to_debit.acc_balance > acc_to_debit.alloted:  
            messages.error(request,"Edit amount exceeds Budget")
            # raise ValidationError(f'{trans_debit.amount} in addition with previous total {total_debit["amount__sum"]} exceeds transaction of RDPP {trans_debit.debit_acc} (DBT {trans_debit.debit_acc.alloted})')
            return redirect(f"/transaction/transfer/edit/{transfer.id}")

        elif req_amount + acc_to_credit.acc_balance > acc_to_credit.alloted:
            messages.error(request,"Edit amount exceeds Budget")
            return redirect(f"/transaction/transfer/edit/{transfer.id}")
            # raise ValidationError(f'{transfer.amount}  Money Receive====== n addition with previous total {total["amount__sum"]} exceeds transaction of RDPP {transfer.credit_acc} (DBT {transfer.credit_acc.alloted})')
        
        else:
            acc_to_debit.acc_balance = (acc_to_debit.acc_balance - edit_amount)
            acc_to_debit.total_after_adjustment = acc_to_debit.acc_balance
            acc_to_debit.adjusted = acc_to_debit.adjusted - edit_amount
            acc_to_debit.amount = req_amount
            acc_to_debit.save()
        
            ### apply credit to credit acc ###
            acc_to_credit.acc_balance = (acc_to_credit.acc_balance + edit_amount)
            acc_to_credit.total_after_adjustment = acc_to_credit.acc_balance
            acc_to_credit.adjusted = acc_to_credit.adjusted + edit_amount
            acc_to_credit.amount = req_amount
            acc_to_credit.save()

            transfer.amount = form["amount"]
            transfer.save()

        return redirect("/transaction/transfers")

    context = {
        "transfer": transfer,
    }
    
    return render(request, 'edit_transfer.html',context)


def delete_transfer(request, pk):
    obj = get_object_or_404(Transfer, id=pk)

    acc_to_debit = Account.objects.get(name=obj.debit_acc)
    acc_to_credit = Account.objects.get(name=obj.credit_acc)  
    
    if request.method == "POST":



        acc_to_credit.acc_balance = acc_to_credit.acc_balance - obj.amount
        # acc_to_credit.total_after_adjustment = acc_to_credit.acc_balance
        acc_to_credit.total_after_adjustment = acc_to_credit.total_after_adjustment - obj.amount
        acc_to_credit.adjusted = acc_to_credit.adjusted - obj.amount
        # acc_to_credit.amount = acc_to_credit.amount - obj.amount
        acc_to_credit.save()

        ### apply credit to credit acc ###
        acc_to_debit.acc_balance = acc_to_debit.acc_balance + obj.amount
        # acc_to_debit.total_after_adjustment = acc_to_debit.acc_balance
        acc_to_debit.total_after_adjustment = acc_to_debit.total_after_adjustment + obj.amount
        acc_to_debit.adjusted = acc_to_debit.adjusted + obj.amount
        # acc_to_debit.amount = 
        acc_to_debit.save() 
        obj.delete()
        return redirect("/transaction/transfers")
    context = {
        "object":obj,
    }        

    return render(request, 'delete_transfer.html', context)

