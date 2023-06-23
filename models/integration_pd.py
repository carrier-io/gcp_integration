import json
from enum import Enum
from json import JSONDecodeError
from typing import Union, Optional

from google.cloud import compute_v1
from google.oauth2.service_account import Credentials
from pydantic import BaseModel
from pylon.core.tools import log

from tools import session_project
from ...integrations.models.pd.integration import SecretField


class IntegrationModel(BaseModel):
    service_account_info: Union[SecretField, str]
    project: str
    zone: str

    def check_connection(self):
        try:
            service_info = json.loads(
                self.service_account_info.unsecret(session_project.get()))
            credentials = Credentials.from_service_account_info(service_info)
            instance_client = compute_v1.InstancesClient(credentials=credentials)
            instance_client.list(
                project=self.project,
                zone=self.zone,
            )
        except JSONDecodeError:
            return "Failed to decode service account info"
        except Exception as exc:
            log.error(exc)
            return str(exc)
        return True

    def get_zones(self):
        service_info = json.loads(
            self.service_account_info.unsecret(session_project.get()))
        credentials = Credentials.from_service_account_info(service_info)
        zones_client = compute_v1.ZonesClient(credentials=credentials)
        zones = zones_client.list(project=self.project)
        return [zone.name for zone in zones]


class InstanceType(str, Enum):
    on_demand = "on-demand"
    spot = "spot"


class PerformanceBackendTestModel(IntegrationModel):
    id: int
    project_id: Optional[int]
    cpu_cores_limit: int
    memory_limit: int
    concurrency: int
    instance_type: InstanceType

    class Config:
        use_enum_values = True


class PerformanceUiTestModel(PerformanceBackendTestModel):
    ...
