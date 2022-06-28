from django.shortcuts import render
from django.views.generic.base import TemplateView
from. import views



class AboutAuthorView(TemplateView):
    template_name ='about/author.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'