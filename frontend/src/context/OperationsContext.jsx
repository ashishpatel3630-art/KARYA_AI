import { createContext, useContext, useMemo, useState } from "react";

const OperationsContext = createContext(null);

const initialAgents = [
  {
    id: "agent-maintenance",
    name: "Predictive Maintenance Agent",
    role: "Industrial reliability",
    model: "llama3.2:latest",
    status: "ACTIVE",
    taskCount: 24,
    workflowCount: 6,
    knowledgeCount: 18,
    toolCount: 4,
    successRate: 96.8,
  },
  {
    id: "agent-compliance",
    name: "Compliance Research Agent",
    role: "Evidence and policy",
    model: "llama3.2:latest",
    status: "IDLE",
    taskCount: 12,
    workflowCount: 3,
    knowledgeCount: 9,
    toolCount: 3,
    successRate: 98.1,
  },
];

const initialWorkflows = [
  {
    id: "workflow-maintenance",
    name: "Maintenance Detection",
    status: "READY",
    agentId: "agent-maintenance",
    progress: 74,
    nodes: ["Trigger", "Sensor data", "Knowledge search", "Analysis", "Approval", "Result"],
  },
  {
    id: "workflow-compliance",
    name: "Compliance Review",
    status: "READY",
    agentId: "agent-compliance",
    progress: 0,
    nodes: ["Document intake", "Research", "Evidence", "Review", "Result"],
  },
];

const initialTasks = [
  {
    id: "task-2048",
    title: "Review Compressor C-101 vibration report",
    description: "Extract measurements, compare only documented limits, and prepare a grounded recommendation.",
    agentId: "agent-maintenance",
    workflowId: "workflow-maintenance",
    status: "WAITING",
    priority: "HIGH",
    result: "Approval required before maintenance action.",
  },
  {
    id: "task-2047",
    title: "Index maintenance report evidence",
    description: "Prepare source chunks for retrieval.",
    agentId: "agent-maintenance",
    workflowId: "workflow-maintenance",
    status: "COMPLETED",
    priority: "NORMAL",
    result: "6 source chunks indexed.",
  },
];

const initialKnowledge = [
  { id: "knowledge-maintenance", name: "Maintenance report.pdf", type: "PDF", status: "INDEXED", size: "1.2 MB", usedByAgents: 1, usedByWorkflows: 1 },
  { id: "knowledge-safety", name: "Safety operating manual.pdf", type: "PDF", status: "INDEXED", size: "4.8 MB", usedByAgents: 2, usedByWorkflows: 2 },
];

const initialIntegrations = [
  { id: "integration-postgres", name: "PostgreSQL + pgvector", type: "DATABASE", status: "CONNECTED", usedBy: "Knowledge engine" },
  { id: "integration-ollama", name: "Local Ollama", type: "MODEL RUNTIME", status: "CONNECTED", usedBy: "AI core" },
  { id: "integration-redis", name: "Redis", type: "CACHE", status: "AVAILABLE", usedBy: "Session services" },
];

const initialActivities = [
  { id: "activity-1", type: "TASK", timestamp: "09:42:12", actor: "Predictive Maintenance Agent", entity: "Task #2048", description: "Waiting for human approval.", severity: "ATTENTION" },
  { id: "activity-2", type: "KNOWLEDGE", timestamp: "09:17:06", actor: "Knowledge Engine", entity: "Maintenance report.pdf", description: "Retrieved 6 verified source chunks.", severity: "INFO" },
  { id: "activity-3", type: "SYSTEM", timestamp: "08:54:21", actor: "AI Core", entity: "Local Ollama", description: "Runtime handshake completed.", severity: "INFO" },
];

const initialApprovals = [
  { id: "approval-2048", taskId: "task-2048", agentId: "agent-maintenance", action: "Schedule maintenance inspection", reason: "Task result requires human control before action.", risk: "MEDIUM", status: "PENDING", createdAt: "09:42:12" },
];

function createActivity(type, actor, entity, description, severity = "INFO") {
  return {
    id: `activity-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    type,
    timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    actor,
    entity,
    description,
    severity,
  };
}

export function OperationsProvider({ children }) {
  const [agents, setAgents] = useState(initialAgents);
  const [tasks, setTasks] = useState(initialTasks);
  const [workflows, setWorkflows] = useState(initialWorkflows);
  const [knowledge, setKnowledge] = useState(initialKnowledge);
  const [integrations, setIntegrations] = useState(initialIntegrations);
  const [activities, setActivities] = useState(initialActivities);
  const [approvals, setApprovals] = useState(initialApprovals);
  const [notifications, setNotifications] = useState([]);

  function recordActivity(activity) {
    setActivities((current) => [activity, ...current]);
  }

  function notify(message, type = "INFO") {
    setNotifications((current) => [{ id: Date.now(), message, type }, ...current].slice(0, 5));
  }

  function createAgent(input) {
    const agent = {
      id: `agent-${Date.now()}`,
      name: input.name,
      role: input.role || "General operations",
      model: input.model || "llama3.2:latest",
      status: "IDLE",
      taskCount: 0,
      workflowCount: 0,
      knowledgeCount: 0,
      toolCount: input.tools?.length || 0,
      successRate: 100,
    };
    setAgents((current) => [...current, agent]);
    recordActivity(createActivity("AGENT", agent.name, agent.name, "Agent created in local workspace."));
    notify(`${agent.name} is ready for work.`);
    return agent;
  }

  function createTask(input) {
    const task = {
      id: `task-${Date.now()}`,
      title: input.title,
      description: input.description || "No task description provided.",
      agentId: input.agentId || agents[0]?.id,
      workflowId: input.workflowId || workflows[0]?.id,
      status: "QUEUED",
      priority: input.priority || "NORMAL",
      result: null,
    };
    setTasks((current) => [task, ...current]);
    recordActivity(createActivity("TASK", "Workspace operator", task.title, "Task created and queued."));
    notify(`${task.title} was queued.`);
    return task;
  }

  function runTask(taskId) {
    const task = tasks.find((item) => item.id === taskId);
    if (!task || ["RUNNING", "COMPLETED"].includes(task.status)) return;

    setTasks((current) => current.map((item) => item.id === taskId ? { ...item, status: "RUNNING" } : item));
    setAgents((current) => current.map((agent) => agent.id === task.agentId ? { ...agent, status: "ACTIVE", taskCount: agent.taskCount + 1 } : agent));
    recordActivity(createActivity("TASK", "Workspace operator", task.title, "Task execution started."));

    window.setTimeout(() => {
      setTasks((current) => current.map((item) => item.id === taskId ? { ...item, status: "COMPLETED", result: "Execution completed in local workspace." } : item));
      setAgents((current) => current.map((agent) => agent.id === task.agentId ? { ...agent, status: "IDLE" } : agent));
      recordActivity(createActivity("TASK", task.title, task.title, "Task completed successfully."));
      notify(`${task.title} completed.`);
    }, 1400);
  }

  function cancelTask(taskId) {
    const task = tasks.find((item) => item.id === taskId);
    setTasks((current) => current.map((item) => item.id === taskId ? { ...item, status: "CANCELLED" } : item));
    if (task) recordActivity(createActivity("TASK", "Workspace operator", task.title, "Task cancelled."));
  }

  function runWorkflow(workflowId) {
    const workflow = workflows.find((item) => item.id === workflowId);
    if (!workflow) return;
    setWorkflows((current) => current.map((item) => item.id === workflowId ? { ...item, status: "RUNNING", progress: 15 } : item));
    recordActivity(createActivity("WORKFLOW", workflow.name, workflow.name, "Workflow execution started."));
    notify(`${workflow.name} is running.`);
    window.setTimeout(() => {
      setWorkflows((current) => current.map((item) => item.id === workflowId ? { ...item, status: "COMPLETED", progress: 100 } : item));
      recordActivity(createActivity("WORKFLOW", workflow.name, workflow.name, "Workflow execution completed."));
      notify(`${workflow.name} completed.`);
    }, 1600);
  }

  function createWorkflow(input) {
    const workflow = { id: `workflow-${Date.now()}`, name: input.name, status: "READY", agentId: input.agentId || agents[0]?.id, progress: 0, nodes: ["Trigger", "Agent", "Knowledge", "Result"] };
    setWorkflows((current) => [...current, workflow]);
    recordActivity(createActivity("WORKFLOW", "Workspace operator", workflow.name, "Workflow created."));
    notify(`${workflow.name} is ready.`);
    return workflow;
  }

  function addKnowledge(input) {
    const item = { id: `knowledge-${Date.now()}`, name: input.name, type: input.type || "DOCUMENT", status: "INDEXING", size: input.size || "Pending", usedByAgents: 0, usedByWorkflows: 0 };
    setKnowledge((current) => [item, ...current]);
    recordActivity(createActivity("KNOWLEDGE", "Knowledge Engine", item.name, "Knowledge source indexing started."));
    window.setTimeout(() => {
      setKnowledge((current) => current.map((entry) => entry.id === item.id ? { ...entry, status: "INDEXED" } : entry));
      recordActivity(createActivity("KNOWLEDGE", "Knowledge Engine", item.name, "Knowledge source indexed."));
      notify(`${item.name} is indexed.`);
    }, 1200);
  }

  function toggleIntegration(integrationId) {
    setIntegrations((current) => current.map((item) => {
      if (item.id !== integrationId) return item;
      const status = item.status === "CONNECTED" ? "OFFLINE" : "CONNECTED";
      recordActivity(createActivity("INTEGRATION", item.name, item.name, `Integration ${status.toLowerCase()}.`, status === "OFFLINE" ? "ATTENTION" : "INFO"));
      notify(`${item.name} is ${status.toLowerCase()}.`, status === "OFFLINE" ? "ATTENTION" : "INFO");
      return { ...item, status };
    }));
  }

  function reviewApproval(approvalId, status) {
    const approval = approvals.find((item) => item.id === approvalId);
    if (!approval) return;
    setApprovals((current) => current.map((item) => item.id === approvalId ? { ...item, status } : item));
    setTasks((current) => current.map((item) => item.id === approval.taskId ? { ...item, status: status === "APPROVED" ? "COMPLETED" : "CANCELLED" } : item));
    recordActivity(createActivity("APPROVAL", "Workspace operator", approval.action, `Approval ${status.toLowerCase()}.`, status === "REJECTED" ? "ATTENTION" : "INFO"));
    notify(`Approval ${status.toLowerCase()}.`);
  }

  const analytics = useMemo(() => ({
    totalExecutions: tasks.filter((task) => ["RUNNING", "COMPLETED"].includes(task.status)).length,
    successfulExecutions: tasks.filter((task) => task.status === "COMPLETED").length,
    failedExecutions: tasks.filter((task) => task.status === "FAILED").length,
    workflowRuns: workflows.filter((workflow) => ["RUNNING", "COMPLETED"].includes(workflow.status)).length,
    knowledgeRetrievals: activities.filter((activity) => activity.type === "KNOWLEDGE").length,
    approvalRate: approvals.length ? Math.round((approvals.filter((item) => item.status !== "PENDING").length / approvals.length) * 100) : 0,
  }), [activities, approvals, tasks, workflows]);

  const systemStatus = useMemo(() => {
    const offlineIntegrations = integrations.filter((item) => item.status === "OFFLINE").length;
    return {
      system: offlineIntegrations ? "DEGRADED" : "OPERATIONAL",
      aiCore: "ACTIVE",
      secureSession: true,
      activeAgents: agents.filter((agent) => agent.status === "ACTIVE").length,
      runningWorkflows: workflows.filter((workflow) => workflow.status === "RUNNING").length,
      pendingApprovals: approvals.filter((approval) => approval.status === "PENDING").length,
      offlineIntegrations,
    };
  }, [agents, approvals, integrations, workflows]);

  const value = {
    agents, tasks, workflows, knowledge, integrations, activities, approvals, notifications, analytics, systemStatus,
    createAgent, createTask, runTask, cancelTask, runWorkflow, createWorkflow, addKnowledge, toggleIntegration, reviewApproval,
    clearNotifications: () => setNotifications([]),
  };

  return <OperationsContext.Provider value={value}>{children}</OperationsContext.Provider>;
}

export function useOperations() {
  const context = useContext(OperationsContext);
  if (!context) throw new Error("useOperations must be used within OperationsProvider");
  return context;
}
