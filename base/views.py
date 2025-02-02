from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q  # Import Q for advanced filtering

from .models import Task


class CustomLoginView(LoginView):
    template_name = "base/Login.html"
    fields = '__all__'  
    redirect_authenticated_user = True  # If the user is already logged in, redirect them

    def get_success_url(self):
        return reverse_lazy('tasks')  # Redirect to the task list after login
    

class RegistrationView(FormView):
    template_name = "base/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True  # If the user is already logged in, redirect them
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)
    



class TaskListView(LoginRequiredMixin, ListView): 
    model = Task
    context_object_name = "tasks"
    template_name = "base/TaskListView.html"

    def get_queryset(self):
        return Task.objects.filter(
            user=self.request.user, 
            title__icontains=self.request.GET.get("q", "")
        )


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "base/TaskDetailView.html"  # ⚠️ Fixed typo in the filename


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "base/TaskCreateView.html"
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        print(f"User before assignmet: {form.instance.user}")
        form.instance.user = self.request.user
        print(f"User after assignmet: {form.instance.user}")

        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = "base/TaskCreateView.html"
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    context_object_name = "task"
    template_name = "base/TaskDelete.html"
    success_url = reverse_lazy('tasks')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user
