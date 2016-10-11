from django.shortcuts import render
import urllib.request
import urllib.parse
import json
from .forms import LoginForm
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
	return render(request, 'marketplace/index.html')

def login(request):
	if request.method == 'GET':
		form = LoginForm()
		return render(request, 'marketplace/login.html', {'form': form})
	form = LoginForm(request.POST)
	# check whether it's valid:
	if not form.is_valid():
		return render(request, 'marketplace/login.html', {'form': form})
	email = form.cleaned_data['email']
	password = form.cleaned_data['password']
	post_data = {'email': email, 'password': password}
	post_encoded = urllib.parse.urlencode(post_data).encode('utf-8')
	req = urllib.request.Request('http://exp-api:8000/login/', data=post_encoded, method='POST')
	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	resp = json.loads(resp_json)
	if not resp or not resp['ok']:
		# couldn't log them in, send them back to login page with error
		return render(request, 'marketplace/login.html', {'form': form})
	# logged them in. set their login cookie and redirect to back to wherever they came from
	authenticator = resp['resp']['authenticator']
	response = HttpResponseRedirect(next)
	response.set_cookie("auth", authenticator)
	return HttpResponseRedirect('/market/index/')


def job_entry(request, id):
	# make a GET request and parse the returned JSON                                                                                                                                                           # note, no timeouts, error handling or all the other things needed to do this for real
	#req = urllib.request.Request('http://www.mocky.io/v2/57f001943d0000dc1e0dd7ca')
	req = urllib.request.Request('http://exp-api:8000/jobs/' + id + '/')
	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	resp_dict = json.loads(resp_json)
	context = {"job": resp_dict['result']}
	return render(request, 'marketplace/job_detail.html', context=context)

def allJobs(request):
	#Experience service call to get all jobs
	req = urllib.request.Request('http://exp-api:8000/jobs/')

	#mock response data for testing:
	#req = urllib.request.Request('http://www.mocky.io/v2/57efed1a3d0000371e0dd7c4')

	resp_json = urllib.request.urlopen(req).read().decode('utf-8')
	resp = json.loads(resp_json)
	context = {'job_list' : resp['result']}
	return render(request, 'marketplace/jobslist.html', context)



