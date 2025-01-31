from django.shortcuts import render

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Task


class CustomLoginView(LoginView):
    template_name = "base/Login.html"
    fields = '__all__)'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class TaskListView(LoginRequiredMixin, ListView): 
    model = Task
    context_object_name = "tasks"
    template_name = "base/TaskListView.html"

    #! Show only the logged-in user's tasks
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()
        return context
    #! Show only the logged-in user's tasks
    # def get_queryset(self):
    #     return Task.objects.filter(user=self.request.user) 


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "base/TaskDeailView.html"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "base/TaskCreateView.html"
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    # 🔹  form.instance → This is the task (sticky note) that’s being created.
    # 🔹 .user → This is the owner of the task (the person who wrote the sticky note).
    # 🔹 self.request.user → This is the currently logged-in user (the person using the website).
    


class TaskUpdateView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Task
    template_name = "base/TaskCreateView.html"
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class TaskDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Task
    context_object_name = "task"
    template_name = "base/TaskDelete.html"
    success_url = reverse_lazy('tasks')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user
