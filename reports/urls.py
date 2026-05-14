from django.urls import path
from . import views

urlpatterns = [
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/ppt/', views.export_ppt, name='export_ppt'),
    path('generate-newsletter/', views.generate_newsletter, name='generate_newsletter'),
    path('archive/', views.report_archive, name='report_archive'),
    # Design-system infographic reports
    path('design/one-pager/', views.design_one_pager, name='design_one_pager'),
    path('design/newsletter/', views.design_newsletter, name='design_newsletter'),
    path('design/deck/', views.design_deck, name='design_deck'),
    path('design/reports/', views.design_reports_tab, name='design_reports_tab'),
]
