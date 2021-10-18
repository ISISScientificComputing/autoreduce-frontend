# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #

from django.urls import path
from autoreduce_frontend.reduction_viewer.views import run_queue, run_summary, runs_list, fail_queue

app_name = "runs"

urlpatterns = [
    path('queue/', run_queue.run_queue, name='queue'),
    path('failed/', fail_queue.fail_queue, name='failed'),
    path('<str:instrument>/', runs_list.runs_list, name='list'),
    path('<str:instrument_name>/<int:run_number>/', run_summary.run_summary, name='summary'),
    path('<str:instrument_name>/batch/<int:pk>/', run_summary.run_summary_batch_run, name='batch_summary'),
    path('<str:instrument_name>/batch/<int:pk>/<int:run_version>/',
         run_summary.run_summary_batch_run,
         name='batch_summary'),
    path('<str:instrument_name>/<int:run_number>/<int:run_version>/', run_summary.run_summary, name='summary'),
]
