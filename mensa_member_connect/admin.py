from django.contrib import admin

from mensa_member_connect.models.admin_action import AdminAction
from mensa_member_connect.models.connection_request import ConnectionRequest
from mensa_member_connect.models.expert import Expert
from mensa_member_connect.models.expertise import Expertise
from mensa_member_connect.models.industry import Industry
from mensa_member_connect.models.local_group import LocalGroup

# Register models with default admin
admin.site.register(AdminAction)
admin.site.register(ConnectionRequest)
admin.site.register(Expert)
admin.site.register(Expertise)
admin.site.register(Industry)
admin.site.register(LocalGroup)
