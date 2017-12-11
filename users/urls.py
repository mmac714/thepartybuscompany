""" Defines URL patterns for users """
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import reverse, reverse_lazy


# https://docs.djangoproject.com/en/1.11/topics/auth/default/
suc_url=reverse_lazy('password_reset_complete',current_app='users')

urlpatterns = [

	# log in/put urls
	url(r'^login/$', 
		auth_views.LoginView.as_view(
			template_name='users/login.html', 
			redirect_authenticated_user=False,
			# ^^ will update depending on whether I decide to make logins
			# for users. Right now the answer is no. 
			redirect_field_name="move",
			),
		name='login'),

	url(r'^logout/$', 
		auth_views.LogoutView.as_view(
			next_page='users:login'), 
		name='logout'),

	# Password change urls

	url(r'^password_reset/$',
		auth_views.PasswordResetView.as_view(
			template_name='users/password_reset.html',
			email_template_name='users/password_reset_email.html',
			subject_template_name='users/password_reset_subject.txt',
			success_url='password_reset_done'),
		name='password_reset'),

	url(r'^password_reset/password_reset_done/$', 
		auth_views.PasswordResetDoneView.as_view(
			template_name='users/password_reset_done.html'),
		name='password_reset_done'),

	url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
		auth_views.PasswordResetConfirmView.as_view(
			template_name='users/password_reset_confirm.html',
			success_url=suc_url),
		name='password_reset_confirm'),

	url(r'^password_reset_complete/$', 
		auth_views.PasswordResetCompleteView.as_view(
			template_name='users/password_reset_complete.html'),
		name='password_reset_complete'),
	
	]
