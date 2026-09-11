from enum import Enum


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    DEPLOYING = "deploying"
    HEALTH_CHECK = "health_check"
    SMOKE_TEST = "smoke_test"
    SWITCHING = "switching"
    MONITORING = "monitoring"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"