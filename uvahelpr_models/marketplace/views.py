from django.views.generic import View
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from json import dumps
from django.forms.models import model_to_dict
from .forms import  JobForm, MessageForm, HelprUserForm
from .models import HelprUser, Job, Message, Authenticator

from django.contrib.auth import hashers
import os
import hmac
from django.conf import settings


############ VIEWS ####################

######### Function-based #############
@require_http_methods(["POST"])
def checkPassword(request):
	emailaddress = request.POST.get('email')
	password = request.POST.get('password')
	userfound = True
	try:
		user = HelprUser.objects.get(email=emailaddress)
	except ObjectDoesNotExist:
		userfound = False
	resp = {}
	if (userfound and hashers.check_password(password, user.password)):
		resp['ok'] = True
		resp['result'] = model_to_dict(user)
	else:
		resp['ok'] = False
		resp['result'] = "Invalid email or password"
	return JsonResponse(resp)

def createAuthenticator(request):
	user_id = request.POST.get('user_id')
	user = HelprUser.objects.get(pk=user_id)
	resp = {}
	authenticator_hash = hmac.new(key=settings.SECRET_KEY.encode('utf-8'), msg=os.urandom(32), digestmod='sha256').hexdigest()
	authenticator = Authenticator.objects.create(auth_user=user, authenticator=authenticator_hash)
	try:
		authenticator.save()
		resp['ok'] = True
		resp["result"] = {"authenticator": model_to_dict(authenticator)}
	except:
		resp['ok'] = False
		resp['result'] = "Failed to create authenticator"
	return JsonResponse(resp)

def delete_authenticator(request):
	authkey = request.POST.get('auth')
	resp = {}
	userfound = True
	try:
		authenticator = Authenticator.objects.get(authenticator=authkey)
		authenticator.delete()
	except ObjectDoesNotExist:
		userfound = False
	if userfound:
		resp["ok"] = True
	else:
		resp["ok"] = False
	return JsonResponse(resp)

def get_auth_user(request):
	authkey = request.POST.get('auth')
	resp = {}
	userfound = True
	try:
		authenticator = Authenticator.objects.get(authenticator=authkey)
	except ObjectDoesNotExist:
		userfound = False

	if userfound:
		resp["ok"] = True
		authdict = model_to_dict(authenticator)
		authdict['time_created'] = authenticator.time_created
		resp["result"] = {"user": model_to_dict(authenticator.auth_user), "auth": authdict}
	else:
		resp["ok"] = False
		resp["result"] = "Invalid authenticator"
	return JsonResponse(resp)

# Creating a user
@require_http_methods(["POST"])
def create_user(request):
	result = {}
	result_msg = None
	try:
		req_input = {
		'username': request.POST['username'],
		'email':request.POST['email'],
		'password':hashers.make_password(request.POST['password']),
		'first_name':request.POST['first_name'],
		'last_name':request.POST['last_name'],
		'phone_number':request.POST['phone_number'],
		'skills': request.POST['skills']
		}
	except KeyError:
		req_input = {}
		result_msg = "Input did not contain all the required fields."
	user_form = HelprUserForm(req_input)
	if user_form.is_valid():
		user = user_form.save()
		result["ok"] = True
		result["result"] = {"id": user.id}
	else:
		result_msg = "Invalid form data." if result_msg is None else result_msg
		result["ok"] = False
		result["result"] = result_msg
		result["submitted_data"] = dumps(request.POST)
	return JsonResponse(result)

#Deleting a user
@require_http_methods(["POST"])
def delete_user(request):
	result = {}
	try:
		user = HelprUser.objects.get(pk=request.POST["id"])
		user.delete()
		result["ok"] = True
		result["result"] = "User successfully deleted."
	except ObjectDoesNotExist:
		result["ok"] = False
		result["result"] = "User does not exist."
	return JsonResponse(result)

#getting all jobs
@require_http_methods(["GET"])
def get_all_jobs(request):
	result = {}
	try:
		result["ok"] = True
		result["result"] = [model_to_dict(job) for job in Job.objects.all()]
	except Exception:
		result["ok"] = False
		result["result"] = []
	return JsonResponse(result)

#Creating a job
@require_http_methods(["POST"])
def create_job(request):
	result = {}
	job_form = JobForm(request.POST)
	if job_form.is_valid():
		job = job_form.save()
		job.save()
		result["ok"] = True
		result["result"] = {"id": job.id}
	else:
		result["ok"] = False
		result["result"] = "Invalid form data."
		result["submitted_data"] = request.POST
		result["errors"] = job_form.errors
	return JsonResponse(result)

#Deleting a job
@require_http_methods(["POST"])
def delete_job(request):
	result = {}
	try:
		job = Job.objects.get(pk=request.POST["id"])
		job.delete()
		result["ok"] = True
		result["result"] = "Job succesfully deleted."
	except ObjectDoesNotExist:
		result["ok"] = False
		result["result"] = "Job does not exist."
	return JsonResponse(result)

#Creating a message
@require_http_methods(["POST"])
def create_message(request):
	result = {}
	message_form = MessageForm(request.POST)
	if message_form.is_valid():
		message = message_form.save()
		message.save()
		result["ok"] = True
		result["result"] = {"id": message.id}
	else:
		result["ok"] = False
		result["result"] = "Invalid form data."
		result["submitted_data"] = dumps(request.POST)
	return JsonResponse(result)

#Deleting a message
@require_http_methods(["POST"])
def delete_message(request):
	result = {}
	try:
		message = Message.objects.get(pk=request.POST["id"])
		message.delete()
		result["ok"] = True
		result["result"] = "Message succesfully deleted."
	except ObjectDoesNotExist:
		result["ok"] = False
		result["result"] = "Message does not exist."
	return JsonResponse(result)

########## Class-based #######################

# Retrieving/updating a user instance
class UserRU(View):

	def get(self, request, id):
		result = {}
		try:
			user = HelprUser.objects.get(pk=id)
			result["ok"] = True
			result["result"] = model_to_dict(user)
		except ObjectDoesNotExist:
			result["ok"] = False
			result["result"] = "User does not exist."
		return JsonResponse(result)

	def post(self, request, id):
		result = {}
		try:
			user = HelprUser.objects.get(pk=id)
			user_fields = [f.name for f in HelprUser._meta.get_fields()]
			for field in user_fields:
				if field in request.POST:
					setattr(user, field, request.POST[field])
			user.save()
			result["ok"] = True
			result["result"] = "User updated succesfully."
		except ObjectDoesNotExist:
			result["ok"] = False
			result["result"] = "User does not exist."
		return JsonResponse(result)

class JobRU(View):
	def get(self, request, id):
		result = {}
		try:
			job = Job.objects.get(pk=id)
			result["ok"] = True
			result["result"] = model_to_dict(job)
		except ObjectDoesNotExist:
			result["ok"] = False
			result["result"] = "Job does not exist."
		return JsonResponse(result)

	def post(self, request, id):
		result = {}
		try:
			job = Job.objects.get(pk=id)
			job_fields = [f.name for f in Job._meta.get_fields()]
			for field in job_fields:
				if field in request.POST:
					setattr(job, field, request.POST[field])
			job.save()
			result["ok"] = True
			result["result"] = "Job updated succesfully."
		except ObjectDoesNotExist:
			result["ok"] = False
			result["result"] = "Job does not exist."
		return JsonResponse(result)

class MessageRU(View):
	def get(self, request, id):
		result = {}
		try:
			message = Message.objects.get(pk=id)
			result["ok"] = True
			result["result"] = model_to_dict(message);
		except ObjectDoesNotExist:
			result["ok"] = False
			result["result"] = "Message does not exist."
		return JsonResponse(result)

	def post(self, request, id):
		result = {}
		try:
			message = Message.objects.get(pk=id)
			message_fields = [f.name for f in Message._meta.get_fields()]
			for field in message_fields:
				if field in request.POST:
					setattr(message, field, request.POST[field])
			message.save()
			result["ok"] = True
			result["result"] = "Message updated succesfully."
		except ObjectDoesNotExist:
			result["ok"] = False
			result["result"] = "Message does not exist."
		return JsonResponse(result)