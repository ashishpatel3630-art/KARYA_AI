# KARYA Workers

Workers handle long-running and asynchronous operations that should not block API requests.

## Why Workers?

Some operations can take significant time:

* Document processing
* OCR
* Embedding generation
* RAG indexing
* AI evaluation
* Large file processing
* Workflow execution
* Agent tasks

Instead of keeping an HTTP request open:

```text
API
 ↓
Create Job
 ↓
Worker Queue
 ↓
Worker
 ↓
Process
 ↓
Store Result
 ↓
Notify / Poll
```

---

## Example

```text
User uploads PDF
       ↓
FastAPI accepts file
       ↓
Job created
       ↓
Worker picks job
       ↓
Extract text
       ↓
Generate embeddings
       ↓
Index knowledge
       ↓
Job completed
```

---

## Benefits

* Better API responsiveness
* Fault isolation
* Retry capability
* Parallel processing
* Scalable architecture
* Long-running task support
