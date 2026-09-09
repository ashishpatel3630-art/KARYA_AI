import { apiRequest } from "./api";

export const getAgents = () => apiRequest("/api/agents");
export const createAgent = (agent) => apiRequest("/api/agents", { method: "POST", body: JSON.stringify(agent) });
export const getTasks = () => apiRequest("/api/tasks");
export const createTask = (task) => apiRequest("/api/tasks", { method: "POST", body: JSON.stringify(task) });
export const updateTask = (taskId, status) => apiRequest(`/api/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify({ status }) });
export const getDocuments = () => apiRequest("/api/documents");
export const uploadDocument = (file) => {
  const body = new FormData();
  body.append("file", file);
  return apiRequest("/api/documents/upload", { method: "POST", body });
};
export const getActivity = () => apiRequest("/api/activity");
export const askChat = (message, document_ids = []) => apiRequest("/api/chat", {
  method: "POST",
  body: JSON.stringify({ message, document_ids }),
});