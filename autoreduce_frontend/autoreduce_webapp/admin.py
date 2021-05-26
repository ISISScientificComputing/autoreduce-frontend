# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Initialise admin pages
"""
from django.contrib import admin

from autoreduce_db.reduction_viewer.models import (Instrument, Experiment, Status, ReductionRun, DataLocation,
                                                   ReductionLocation, Setting, Notification)
from autoreduce_db.instrument.models import InstrumentVariable, RunVariable
from autoreduce_frontend.autoreduce_webapp.models import UserCache, InstrumentCache, ExperimentCache

admin.site.register(UserCache)
admin.site.register(InstrumentCache)
admin.site.register(ExperimentCache)

admin.site.register(Instrument)
admin.site.register(Experiment)
admin.site.register(Status)
admin.site.register(ReductionRun)
admin.site.register(DataLocation)
admin.site.register(ReductionLocation)
admin.site.register(Setting)
admin.site.register(Notification)

admin.site.register(InstrumentVariable)
admin.site.register(RunVariable)
