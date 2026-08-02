from enum import Enum

from core.security import Role, require_roles


class Permission(str, Enum):
    GENERAL_READ = "general.read"
    COMPLIANCE_READ = "compliance.read"
    PATTERNS_READ = "patterns.read"
    BENCHMARK_EXECUTE = "benchmark.execute"
    AUDIT_READ = "audit.read"
    DOCUMENT_UPLOAD = "document.upload"
    INCIDENT_CREATE = "incident.create"
    INCIDENT_UPDATE = "incident.update"
    WORK_ORDER_CREATE = "work_order.create"
    WORK_ORDER_UPDATE = "work_order.update"
    WORK_ORDER_APPROVE = "work_order.approve"
    WORK_ORDER_COMPLETE = "work_order.complete"
    USER_ADMIN = "user.admin"


ALL = tuple(Role)
PERMISSION_ROLES = {
    Permission.GENERAL_READ: ALL,
    Permission.COMPLIANCE_READ: (Role.SAFETY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR, Role.AUDITOR),
    Permission.PATTERNS_READ: (Role.RELIABILITY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR, Role.AUDITOR),
    Permission.BENCHMARK_EXECUTE: (Role.RELIABILITY_ENGINEER, Role.ADMINISTRATOR, Role.AUDITOR),
    Permission.AUDIT_READ: (Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR, Role.AUDITOR),
    Permission.DOCUMENT_UPLOAD: (Role.MAINTENANCE_ENGINEER, Role.RELIABILITY_ENGINEER, Role.SAFETY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR),
    Permission.INCIDENT_CREATE: (Role.OPERATOR, Role.SAFETY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR),
    Permission.INCIDENT_UPDATE: (Role.MAINTENANCE_ENGINEER, Role.RELIABILITY_ENGINEER, Role.SAFETY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR),
    Permission.WORK_ORDER_CREATE: (Role.MAINTENANCE_ENGINEER, Role.RELIABILITY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR),
    Permission.WORK_ORDER_UPDATE: (Role.MAINTENANCE_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR),
    Permission.WORK_ORDER_APPROVE: (Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR),
    Permission.WORK_ORDER_COMPLETE: (Role.MAINTENANCE_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR),
    Permission.USER_ADMIN: (Role.ADMINISTRATOR,),
}

ROUTE_PERMISSIONS = {
    "/dashboard": Permission.GENERAL_READ,
    "/assets": Permission.GENERAL_READ,
    "/copilot": Permission.GENERAL_READ,
    "/maintenance": Permission.GENERAL_READ,
    "/incidents": Permission.GENERAL_READ,
    "/reliability": Permission.GENERAL_READ,
    "/compliance": Permission.COMPLIANCE_READ,
    "/work-orders": Permission.GENERAL_READ,
    "/patterns": Permission.PATTERNS_READ,
    "/documents": Permission.GENERAL_READ,
    "/benchmarks": Permission.BENCHMARK_EXECUTE,
    "/audit": Permission.AUDIT_READ,
    "/settings": Permission.USER_ADMIN,
    "/architecture": Permission.GENERAL_READ,
}


def authorize(permission: Permission):
    dependency = require_roles(*PERMISSION_ROLES[permission])
    dependency.permission = permission.value
    return dependency