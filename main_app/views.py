from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.db.models import Q

from .forms import OrganizationForm
from .models import Organization

# Create your views here.
def home_page(request):
    return render(request, 'main_app/home.html')


def contact_page(request):
    return render(request, 'main_app/contact.html')

class OrganizationDetailView(DetailView):
    model = Organization
    template_name = 'main_app/organizations/details.html'


class OrganizationResultsView(ListView):
    model = Organization
    template_name = 'main_app/organizations/results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        location = self.request.GET.get('l')
        category = self.request.GET.get('c')
        if not query and not location and not category:
            return Organization.objects.order_by('-name').all()
        if not query:
            query = 'None'
        if not location:
            location = 'None'            
        if not category:
            category = 'None'
        return Organization.objects.filter(
            Q(name__icontains=query) |
            Q(ein__icontains=query) |
            Q(address__icontains=location) |
            Q(city__icontains=location) |
            Q(state__icontains=location) |
            Q(zip_code=location) |
            Q(category__icontains=category)
        )

class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organization
    template_name = 'main_app/organizations/update.html'
    fields = [
        'name', 'ein', 'address', 'city', 
        'state', 'zip_code', 'phone','contact_email','website_url', 'category',
        'fiscal_sponsor','guidestar_url', 'logo_url','mission_statement', 'description',
    ]

@login_required
def organization_delete(request, pk):
    Organization.objects.get(id=pk).delete()
    return redirect('org_results')

@login_required
def organization_create(request):
    if not request.user.is_partial_complete():
        return redirect('account_update')
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            new_org = form.save(commit=False)
            new_org.user_id = request.user.id
            new_org.save()
            return redirect('org_details', pk=new_org.id)
        return redirect('org_results')
    org_form = OrganizationForm()
    return render(request, 'main_app/organizations/create.html', {
        'org_form': org_form
    })
    