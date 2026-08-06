export const roles = ["Operator", "Maintenance Engineer", "Reliability Engineer", "Safety Engineer", "Supervisor", "Plant Manager", "Administrator", "Auditor"];
const all = roles;
export const routeRoles = {
  "/dashboard": all, "/assets": all, "/copilot": all, "/maintenance": all, "/incidents": all, "/reliability": all,
  "/compliance": ["Safety Engineer", "Supervisor", "Plant Manager", "Administrator", "Auditor"],
  "/work-orders": all, "/patterns": ["Reliability Engineer", "Supervisor", "Plant Manager", "Administrator", "Auditor"],
  "/documents": all, "/benchmarks": ["Reliability Engineer", "Administrator", "Auditor"],
  "/audit": ["Supervisor", "Plant Manager", "Administrator", "Auditor"], "/settings": ["Administrator"], "/architecture": all,
};
export const actionRoles = {
  "document.upload": ["Maintenance Engineer", "Reliability Engineer", "Safety Engineer", "Supervisor", "Plant Manager", "Administrator"],
  "incident.create": ["Operator", "Safety Engineer", "Supervisor", "Plant Manager", "Administrator"],
  "incident.update": ["Maintenance Engineer", "Reliability Engineer", "Safety Engineer", "Supervisor", "Plant Manager", "Administrator"],
  "workOrder.create": ["Maintenance Engineer", "Reliability Engineer", "Supervisor", "Plant Manager", "Administrator"],
  "workOrder.update": ["Maintenance Engineer", "Supervisor", "Plant Manager", "Administrator"],
  "workOrder.approve": ["Supervisor", "Plant Manager", "Administrator"],
  "workOrder.complete": ["Maintenance Engineer", "Supervisor", "Plant Manager", "Administrator"],
  "user.admin": ["Administrator"],
};
export const canAccessRoute = (role, path) => Boolean(role && (routeRoles[path] || []).includes(role));
export const canPerform = (role, action) => Boolean(role && (actionRoles[action] || []).includes(role));