import { createContext, useContext, useEffect, useMemo, useState } from "react";

import {
  createAgent as createAgentRequest,
  createTask as createTaskRequest,
  getActivity,
  getAgents,
  getDocuments,
  getTasks,
  updateTask,
  uploadDocument,
} from "../services/operations";

const OperationsContext = createContext(null);

function mapAgent(agent) {
  return { ...agent, taskCount: 0, workflowCount: 0, knowledgeCount: 0, toolCount: 0, successRate: null };
}

function mapDocument(document) {
  return {
    ...document,
    type: document.content_type?.split("/").pop()?.toUpperCase() || "DOCUMENT",
    size: `${Math.ceil(document.size_bytes / 1024)} KB`,
    usedByAgents: 0,
    usedByWorkflows: 0,
  };
}

function mapActivity(activity) {
  return {
    ...activity,
    timestamp: activity.created_at ? new Date(activity.created_at).toLocaleTimeString() : "",
    actor: "Workspace operator",
    severity: "INFO",
  };
}

export function OperationsProvider({ children }) {
  const [agents, setAgents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [knowledge, setKnowledge] = useState([]);
  const [activities, setActivities] = useState([]);
  const [workflows] = useState([]);
  const [approvals] = useState([]);
  const [integrations] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  function notify(message, type = "INFO") {
    setNotifications((current) => [{ id: Date.now(), message, type }, ...current].slice(0, 5));
  }

  async function refresh() {
    setLoading(true);
    const [agentResult, taskResult, documentResult, activityResult] = await Promise.allSettled([
      getAgents(),
      getTasks(),
      getDocuments(),
      getActivity(),
    ]);
    if (agentResult.status === "fulfilled") setAgents(agentResult.value.map(mapAgent));
    if (taskResult.status === "fulfilled") setTasks(taskResult.value);
    if (documentResult.status === "fulfilled") setKnowledge(documentResult.value.map(mapDocument));
    if (activityResult.status === "fulfilled") setActivities(activityResult.value.map(mapActivity));
    const failed = [agentResult, taskResult, documentResult, activityResult].find((result) => result.status === "rejected");
    if (failed) notify(failed.reason?.message || "Unable to load operations data.", "ATTENTION");
    setLoading(false);
  }

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!knowledge.some((document) => ["UPLOADED", "PROCESSING"].includes(document.status))) return undefined;
    const timer = window.setInterval(() => {
      getDocuments().then((documents) => setKnowledge(documents.map(mapDocument))).catch(() => undefined);
    }, 3000);
    return () => window.clearInterval(timer);
  }, [knowledge]);

  async function createAgent(input) {
    try {
      const agent = await createAgentRequest(input);
      await refresh();
      notify(`${agent.name} was created.`);
      return agent;
    } catch (error) {
      notify(error.message, "ATTENTION");
      return null;
    }
  }

  async function createTask(input) {
    try {
      const task = await createTaskRequest(input);
      await refresh();
      notify(`${task.title} was queued.`);
      return task;
    } catch (error) {
      notify(error.message, "ATTENTION");
      return null;
    }
  }

  async function runTask() {
    notify("Task execution is unavailable because no worker is configured.", "ATTENTION");
    return null;
  }

  async function cancelTask(taskId) {
    try {
      await updateTask(taskId, "CANCELLED");
      await refresh();
    } catch (error) {
      notify(error.message, "ATTENTION");
    }
  }

  async function addKnowledge(file) {
    try {
      await uploadDocument(file);
      await refresh();
      notify("Document uploaded. Processing has not started because no worker is configured.");
    } catch (error) {
      notify(error.message, "ATTENTION");
    }
  }

  function unsupportedAction() {
    notify("This operation is not available in the connected backend yet.", "ATTENTION");
  }

  const analytics = useMemo(() => ({
    totalExecutions: tasks.filter((task) => ["RUNNING", "COMPLETED"].includes(task.status)).length,
    successfulExecutions: tasks.filter((task) => task.status === "COMPLETED").length,
    failedExecutions: tasks.filter((task) => task.status === "FAILED").length,
    workflowRuns: 0,
    knowledgeRetrievals: activities.filter((activity) => activity.type === "KNOWLEDGE").length,
    approvalRate: 0,
  }), [activities, tasks]);

  const systemStatus = useMemo(() => ({
    system: loading ? "LOADING" : "OPERATIONAL",
    aiCore: "NOT_CONFIGURED",
    secureSession: true,
    activeAgents: agents.filter((agent) => agent.status === "ACTIVE").length,
    runningWorkflows: 0,
    pendingApprovals: 0,
    offlineIntegrations: 0,
  }), [agents, loading]);

  const value = {
    agents, tasks, workflows, knowledge, integrations, activities, approvals, notifications, analytics, systemStatus, loading,
    createAgent, createTask, runTask, cancelTask, addKnowledge, refresh,
    runWorkflow: unsupportedAction, createWorkflow: unsupportedAction, toggleIntegration: unsupportedAction, reviewApproval: unsupportedAction,
    clearNotifications: () => setNotifications([]),
  };

  return <OperationsContext.Provider value={value}>{children}</OperationsContext.Provider>;
}

export function useOperations() {
  const context = useContext(OperationsContext);
  if (!context) throw new Error("useOperations must be used within OperationsProvider");
  return context;
}
