from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordChangeForm
from .form import signupForm, loginForm, userdataForm, companyForm

from django.contrib.auth import login as auth_login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.db import connection

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import userdata, companyData, selected



def home(request):
    return render(request, 'home.html', {
        'link':0,
    })

def signup(request):
    if request.method == 'POST':
        form = signupForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = signupForm()
    
    return render(request, 'signup.html', {
        'form': form,
        'link':0,
    })

def login(request):

    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            return redirect('dash')
        else:
            try:
                user = userdata.objects.values().get(pk=request.user.id)
                return redirect('dash')
            except (userdata.DoesNotExist):
                return redirect('profile')
    
    if request.method == "POST":
        uname = request.POST['username']
        upass = request.POST['pass']

        user = authenticate(username=uname, password=upass)

        if user is not None:
            auth_login(request, user)
            if request.user.is_superuser == True:
                return redirect('dash')
            else:
                try:
                    user = userdata.objects.values().get(pk=request.user.id)
                    return redirect('dash')
                except (userdata.DoesNotExist):
                    return redirect('profile')
        
        else:
            messages.warning(request, 'username or password is incorrect !!!!')

    else:
        pass

    return render(request, 'login.html', {
       
    })



def dash(request):
    if request.user.is_authenticated:
        
        if request.user.is_superuser ==True:
            comp = companyData.objects.all()
        else :
            comp = selected.objects.filter(studid=request.user.id)
                    

        return render(request, 'dash.html', {
            'comp': comp,
        })
    else:
        return redirect('login')

def logOut(request):
    logout(request)
    return redirect('home')

#@login_required
def profile(request):
    if request.user.is_authenticated:

        if request.user.is_superuser == True:
            return redirect('admin/addcompany')
        else:
            obj = 0;
            if request.method == "POST":
                form = userdataForm(request.POST, request.FILES)
                form2 = userdataForm(request.FILES)
                #print(form2)
                if form.is_valid():
                    form.save()

                    return HttpResponse('<h1>data saved</h1>')

            else:
                try:
                    user = userdata.objects.values().get(pk=request.user.id) 
                    
                    obj = userdata.objects.get(pk=request.user.id)                     

                   
                    form = userdataForm(initial={
                        'studid':request.user.id,
                        'department':user['department'],
                        'classis' : user['classis'],
                        'roll_no' : user['roll_no'],
                        'add_info' : user['add_info'],
                        'tenth_marks':obj.tenth_marks,
                        'twelth_marks':obj.twelth_marks,
                        'degree_marks':obj.degree_marks,
                        'live_back':obj.live_back,
                        'add_info':obj.add_info,


                    })
                    return render(request, 'portal.html', {
                    'form':form,
                    'obj':obj,
                    'link':1,
                })
                except (userdata.DoesNotExist):
                    form = userdataForm()
                    obj = 0
        return render(request, 'portal.html', {
            'form':form,
            'obj':obj,
            'link':1,
        })
        #return HttpResponse("something wrong")
    else:
        return redirect('login')










def changeProfile(request):
    pass


def changepass(request):

    # setpawordform only accepts the new password

    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()

                # need to update our session 
                update_session_auth_hash(request, form.user)
                return redirect('profile')
        
        else:
            form = PasswordChangeForm(user=request.user)

        return render(request, 'changepass.html', {
                'form':form,
                'link':1,
            })
    else:
        return redirect('login')



#============================================

def makeentry(comp, res):
    for r in res:
        user = User.objects.get(pk=r.studid_id)
        print(user)
        qs = selected(cname=comp, studid=r.studid_id, s_username=user )
        qs.save()

def companydata(request):
    if request.user.is_authenticated:
        if request.user.is_superuser == True:
            
            if request.method == "POST":
                form = companyForm(request.POST)
                if form.is_valid():
                    
                    res = userdata.objects.raw('select studid_id from tnpPortal_userdata where tenth_marks >= %s and twelth_marks >= %s and degree_marks >= %s and live_back <= %s', [
                        form['tenth_marks'].value(),
                        form['twelth_marks'].value(),
                        form['degree_marks'].value(),
                        form['live_back'].value()
                    ])

                    makeentry(form['cname'].value(), res)
                    form.save()
                    #Logindata.objects.filter(pk=id).update(info_stat='y')
                    companyData.objects.filter(cname=form['cname'].value()).update(selected_stud=len(res))
                                        
                    #return HttpResponse('<h1>data saved</h1>')
                    messages.add_message(request, messages.INFO, 'Comapnay data added')
                    return redirect('dash')
                else:
                    
                    error = form['cname'].errors
                    if error.as_text() == '* Company data with this Cname already exists.':
                        cnt = companyData.objects.filter(cname=form['cname'].value()).count()
                        if cnt > 0:
                            
                            res = userdata.objects.raw('select studid_id from tnpPortal_userdata where tenth_marks >= %s and twelth_marks >= %s and degree_marks >= %s and live_back <= %s', [
                                    form['tenth_marks'].value(),
                                    form['twelth_marks'].value(),
                                    form['degree_marks'].value(),
                                    form['live_back'].value()
                                ])


                            companyData.objects.filter(cname=form['cname'].value()).update(
                                tenth_marks=form['tenth_marks'].value(), 
                                twelth_marks=form['twelth_marks'].value(),
                                degree_marks=form['degree_marks'].value(),
                                live_back=form['live_back'].value(),
                                selected_stud=len(res)
                            )

                            selected.objects.filter(cname=form['cname'].value()).delete()
                            makeentry(form['cname'].value(), res)
                        #return HttpResponse('<h1>data Updated</h1>')
                        messages.add_message(request, messages.INFO, 'Comapnay data updated')
                        return redirect('dash')
                            

                return render(request, 'compdata.html', {
                'form': form,
                'link':1,
                })
                    
            else:
                form = companyForm()
            return render(request, 'compdata.html', {
                'form': form,
                'link':1,
            })
    
    else:
        return redirect('login')
    

def comp(request, slug):
    criteria = companyData.objects.get(cname=slug)

    studs = selected.objects.filter(cname=slug)
    print(criteria)
    return render(request, 'dash2.html',{
        'criteria':criteria,
        'studs':studs,
    })