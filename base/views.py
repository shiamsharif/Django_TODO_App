from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task


# ✅ Custom Login View
class CustomLoginView(LoginView):
    """
    Handles user authentication using Django's built-in LoginView.
    - Uses 'base/Login.html' as the login page.
    - Redirects authenticated users away from the login page.
    - Redirects users to the 'tasks' page upon successful login.
    """
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
    



# ✅ Task List View (Shows tasks belonging only to the logged-in user)
class TaskListView(LoginRequiredMixin, ListView):
    """
    Displays a list of tasks that belong to the logged-in user.
    - Requires login.
    - Uses 'base/TaskListView.html' as the template.
    - Shows only the tasks of the logged-in user.
    """
    model = Task
    context_object_name = "tasks"
    template_name = "base/TaskListView.html"

    def get_queryset(self):
        """
        Filters the tasks so that users can only see their own tasks.
        This is more efficient than filtering inside `get_context_data`.
        """
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Adds additional context:
        - `count`: The number of incomplete tasks for the logged-in user.
        """
        context = super().get_context_data(**kwargs)
        context['count'] = self.get_queryset().filter(complete=False).count()
        return context


# ✅ Task Detail View (Displays a single task)
class TaskDetailView(LoginRequiredMixin, DetailView):
    """
    Shows details of a single task.
    - Requires login.
    - Uses 'base/TaskDetailView.html' as the template.
    """
    model = Task
    context_object_name = "task"
    template_name = "base/TaskDetailView.html"  # ⚠️ Fixed typo in the filename


# ✅ Task Create View (Allows users to create new tasks)
class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Allows a logged-in user to create a new task.
    - Uses 'base/TaskCreateView.html' as the template.
    - Only allows task creation for the logged-in user.
    - Redirects to the task list after successful creation.
    """
    model = Task
    template_name = "base/TaskCreateView.html"
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        """
        Before saving the form, set the user field to the logged-in user.
        This prevents users from creating tasks for other users.
        """
        print(f"User before assignmet: {form.instance.user}")
        form.instance.user = self.request.user
        print(f"User after assignmet: {form.instance.user}")

        return super().form_valid(form)


# ✅ Task Update View (Allows users to update their own tasks)
class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows a user to update their own task.
    - Uses 'base/TaskCreateView.html' (same as task creation form).
    - Requires login.
    - Users can only update their own tasks.
    - Redirects to the task list after a successful update.
    """
    model = Task
    template_name = "base/TaskCreateView.html"
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def test_func(self):
        """
        Ensures that only the owner of the task can update it.
        Returns True if the logged-in user is the owner of the task.
        """
        obj = self.get_object()
        return obj.user == self.request.user


# ✅ Task Delete View (Allows users to delete their own tasks)
class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allows a user to delete their own task.
    - Uses 'base/TaskDelete.html' for confirmation.
    - Requires login.
    - Users can only delete their own tasks.
    - Redirects to the task list after successful deletion.
    """
    model = Task
    context_object_name = "task"
    template_name = "base/TaskDelete.html"
    success_url = reverse_lazy('tasks')

    def test_func(self):
        """
        Ensures that only the owner of the task can delete it.
        Returns True if the logged-in user is the owner of the task.
        """
        obj = self.get_object()
        return obj.user == self.request.user
