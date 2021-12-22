# -*- coding: utf-8 -*-

from .split.service import BillPeriodSplitService
from .bill.aggr import BillPeriodAggr

import service.controls.domain.event as event
import service.controls.domain.bill.event as bill_event

event.BillPeriodSplitService = BillPeriodSplitService
bill_event.BillPeriodAggr = BillPeriodAggr

