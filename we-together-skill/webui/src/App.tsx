import {
  Activity,
  Archive,
  Boxes,
  GitBranch,
  MessageSquareText,
  Network,
  RefreshCcw,
  Save,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  X
} from "lucide-react";
import { FormEvent, Fragment, useDeferredValue, useEffect, useState } from "react";
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from "reactflow";

type ApiEnvelope<T> = { ok: true; data: T } | { ok: false; error: { code: string; message: string } };

type Summary = {
  person_count: number;
  relation_count: number;
  memory_count: number;
  scene_count: number;
  branch_count: number;
  patch_count: number;
  snapshot_count: number;
  world: { object_count: number; place_count: number; project_count: number };
};

type GraphNode = {
  id: string;
  type: string;
  label: string;
  status?: string;
  active_in_scene?: boolean;
  data?: Record<string, unknown>;
};

type GraphEdge = {
  id: string;
  type: string;
  source: string;
  target: string;
  label?: string;
  data?: Record<string, unknown>;
};

type Scene = { scene_id: string; scene_summary?: string; scene_type?: string; participant_count?: number; status?: string };
type Patch = { patch_id: string; operation: string; status: string; target_type?: string; target_id?: string };
type EventItem = { event_id: string; event_type?: string; summary?: string; created_at?: string };
type Snapshot = { snapshot_id: string; summary?: string; created_at?: string };
type Branch = { branch_id: string; reason?: string; status?: string; candidates: Array<{ candidate_id: string; label?: string; confidence?: number; payload_json?: unknown }> };
type Detail = { entity: Record<string, unknown>; links?: unknown; patches?: Patch[] };
type AuditRef = { event_id?: string; patch_id?: string; snapshot_id?: string; audit_event_id?: string };

type AppData = {
  summary?: Summary;
  scenes: Scene[];
  graphNodes: GraphNode[];
  graphEdges: GraphEdge[];
  events: EventItem[];
  patches: Patch[];
  snapshots: Snapshot[];
  branches: Branch[];
  world: { objects: unknown[]; places: unknown[]; projects: unknown[] };
};

const emptyData: AppData = {
  scenes: [],
  graphNodes: [],
  graphEdges: [],
  events: [],
  patches: [],
  snapshots: [],
  branches: [],
  world: { objects: [], places: [], projects: [] }
};

class ApiClient {
  constructor(private token: string) {}

  async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.token}`,
      ...(init.headers || {})
    };
    const response = await fetch(path, { ...init, headers });
    const payload = (await response.json()) as ApiEnvelope<T>;
    if (!response.ok || !payload.ok) {
      const message = payload.ok ? response.statusText : payload.error.message;
      throw new Error(message || `HTTP ${response.status}`);
    }
    return payload.data;
  }
}

function short(value: unknown): string {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "string") return value.length > 100 ? `${value.slice(0, 100)}...` : value;
  return JSON.stringify(value);
}

function nodeTone(type: string): string {
  if (type === "person") return "#67e8f9";
  if (type === "memory") return "#facc15";
  if (type === "group") return "#a7f3d0";
  return "#f8fafc";
}

function mapFlowNodes(nodes: GraphNode[]): Node[] {
  return nodes.map((item, index) => ({
    id: item.id,
    position: { x: (index % 4) * 230, y: Math.floor(index / 4) * 150 },
    data: { label: item.label },
    style: {
      background: "rgba(10, 18, 28, 0.96)",
      border: `1px solid ${nodeTone(item.type)}`,
      color: "#ecfeff",
      borderRadius: 18,
      padding: 12,
      minWidth: 150,
      boxShadow: item.active_in_scene ? "0 0 0 4px rgba(34, 211, 238, 0.18)" : "none"
    }
  }));
}

function mapFlowEdges(edges: GraphEdge[]): Edge[] {
  return edges
    .filter((edge) => edge.source && edge.target)
    .map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated: edge.type === "relation",
      style: { stroke: edge.type === "relation" ? "#22d3ee" : "#64748b" },
      labelStyle: { fill: "#cbd5e1", fontWeight: 600 }
    }));
}

export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("we_together_webui_token") || "");
  const [tokenDraft, setTokenDraft] = useState("");
  const [client, setClient] = useState<ApiClient | null>(() => (token ? new ApiClient(token) : null));
  const [data, setData] = useState<AppData>(emptyData);
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [page, setPage] = useState("graph");
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const [sceneFilter, setSceneFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [nameDraft, setNameDraft] = useState("");
  const [auditRef, setAuditRef] = useState<AuditRef | null>(null);
  const [chatInput, setChatInput] = useState("");
  const [chatOutput, setChatOutput] = useState("");

  async function loadWorkspace(api = client) {
    if (!api) return;
    setLoading(true);
    setError("");
    try {
      await api.request("/api/bootstrap");
      const [summary, scenes, graph, events, patches, snapshots, world, branches] = await Promise.all([
        api.request<Summary>("/api/summary"),
        api.request<{ scenes: Scene[] }>("/api/scenes"),
        api.request<{ nodes: GraphNode[]; edges: GraphEdge[] }>(sceneFilter ? `/api/graph?scene_id=${encodeURIComponent(sceneFilter)}` : "/api/graph"),
        api.request<{ events: EventItem[] }>("/api/events?limit=20"),
        api.request<{ patches: Patch[] }>("/api/patches"),
        api.request<{ snapshots: Snapshot[] }>("/api/snapshots?limit=20"),
        api.request<{ objects: unknown[]; places: unknown[]; projects: unknown[] }>(sceneFilter ? `/api/world?scene_id=${encodeURIComponent(sceneFilter)}` : "/api/world"),
        api.request<{ branches: Branch[] }>("/api/branches?status=open")
      ]);
      setData({
        summary,
        scenes: scenes.scenes,
        graphNodes: graph.nodes,
        graphEdges: graph.edges,
        events: events.events,
        patches: patches.patches,
        snapshots: snapshots.snapshots,
        world,
        branches: branches.branches
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (client) {
      void loadWorkspace(client);
    }
  }, [client, sceneFilter]);

  async function enterWorkbench(event: FormEvent) {
    event.preventDefault();
    const nextToken = tokenDraft.trim();
    if (!nextToken) return;
    sessionStorage.setItem("we_together_webui_token", nextToken);
    setToken(nextToken);
    setClient(new ApiClient(nextToken));
  }

  async function selectNode(node: GraphNode) {
    setSelected(node);
    setDetail(null);
    setEditMode(false);
    setAuditRef(null);
    setNameDraft(String(node.data?.primary_name || node.label || ""));
    if (!client) return;
    try {
      const nextDetail = await client.request<Detail>(`/api/entities/${node.type}/${node.id}`);
      setDetail(nextDetail);
      setNameDraft(String(nextDetail.entity.primary_name || nextDetail.entity.name || nextDetail.entity.summary || node.label || ""));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function submitPatch() {
    if (!client || !selected) return;
    const fieldName = selected.type === "person" ? "primary_name" : selected.type === "memory" ? "summary" : "summary";
    const result = await client.request<AuditRef>(`/api/entities/${selected.type}/${selected.id}`, {
      method: "PATCH",
      body: JSON.stringify({ fields: { [fieldName]: nameDraft } })
    });
    setAuditRef(result);
    setEditMode(false);
    await loadWorkspace();
  }

  async function sendChat(event: FormEvent) {
    event.preventDefault();
    if (!client || !chatInput.trim()) return;
    const sceneId = sceneFilter || data.scenes[0]?.scene_id;
    if (!sceneId) {
      setError("需要至少一个 scene 才能运行对话。");
      return;
    }
    const result = await client.request<{ text: string; event_id?: string }>("/api/chat/run-turn", {
      method: "POST",
      body: JSON.stringify({ scene_id: sceneId, input: chatInput })
    });
    setChatOutput(`${result.text}\n\n事件：${result.event_id || "-"}`);
    setChatInput("");
    await loadWorkspace();
  }

  async function resolveBranch(branch: Branch, candidateId: string) {
    if (!client) return;
    const result = await client.request<AuditRef>(`/api/branches/${branch.branch_id}/resolve`, {
      method: "POST",
      body: JSON.stringify({ candidate_id: candidateId, reason: "operator approved via WebUI" })
    });
    setAuditRef(result);
    await loadWorkspace();
  }

  const visibleNodes = data.graphNodes.filter((node) => {
    const text = `${node.label} ${node.id} ${node.type}`.toLowerCase();
    const matchesSearch = text.includes(deferredQuery.toLowerCase());
    const matchesType = typeFilter === "all" || node.type === typeFilter;
    return matchesSearch && matchesType;
  });
  const visibleNodeIds = new Set(visibleNodes.map((node) => node.id));
  const visibleEdges = data.graphEdges.filter((edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target));

  if (!client) {
    return (
      <main className="token-screen">
        <section className="token-panel">
          <div className="sigil"><ShieldCheck size={34} /></div>
          <p className="eyebrow">Host-local Control Plane</p>
          <h1>连接 we-together</h1>
          <p className="muted">静态界面可以打开，但所有图谱、对话、世界与复核 API 都必须使用 Bearer token。</p>
          <form onSubmit={enterWorkbench} className="token-form">
            <input
              placeholder="输入 Bearer token"
              value={tokenDraft}
              onChange={(event) => setTokenDraft(event.target.value)}
            />
            <button type="submit">进入工作台</button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">we-together</p>
          <h1>本地图谱工作台</h1>
        </div>
        <nav>
          <button className={page === "graph" ? "active" : ""} onClick={() => setPage("graph")}><Network size={18} />图谱</button>
          <button className={page === "chat" ? "active" : ""} onClick={() => setPage("chat")}><MessageSquareText size={18} />对话</button>
          <button className={page === "world" ? "active" : ""} onClick={() => setPage("world")}><Boxes size={18} />世界</button>
          <button className={page === "review" ? "active" : ""} onClick={() => setPage("review")}><GitBranch size={18} />复核</button>
          <button className={page === "metrics" ? "active" : ""} onClick={() => setPage("metrics")}><Activity size={18} />指标</button>
        </nav>
        <button className="ghost" onClick={() => void loadWorkspace()}><RefreshCcw size={16} />刷新</button>
        <button
          className="ghost"
          onClick={() => {
            sessionStorage.removeItem("we_together_webui_token");
            setToken("");
            setClient(null);
          }}
        >
          <Archive size={16} />锁定
        </button>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Phase 73</p>
            <h2>{page === "graph" ? "图谱工作台" : page === "chat" ? "Scene 对话" : page === "world" ? "World 面板" : page === "review" ? "Operator Review" : "Metrics"}</h2>
          </div>
          <div className="filters">
            <label>
              Scene
              <select value={sceneFilter} onChange={(event) => setSceneFilter(event.target.value)}>
                <option value="">全部</option>
                {data.scenes.map((scene) => <option key={scene.scene_id} value={scene.scene_id}>{scene.scene_summary || scene.scene_id}</option>)}
              </select>
            </label>
            <label>
              Type
              <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
                <option value="all">全部</option>
                <option value="person">人物</option>
                <option value="memory">记忆</option>
                <option value="group">群组</option>
              </select>
            </label>
            <label className="search">
              <Search size={15} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索 node / id" />
            </label>
          </div>
        </header>

        {error && <div className="error">{error}</div>}
        {loading && <div className="loading">正在读取图谱...</div>}

        {page === "graph" && (
          <section className="graph-layout">
            <div className="graph-canvas">
              <ReactFlow
                nodes={mapFlowNodes(visibleNodes)}
                edges={mapFlowEdges(visibleEdges)}
                fitView
                onNodeClick={(_, node) => {
                  const original = visibleNodes.find((item) => item.id === node.id);
                  if (original) void selectNode(original);
                }}
              >
                <Background color="#164e63" gap={28} />
                <MiniMap nodeColor={(node) => String(node.style?.border || "#22d3ee")} pannable zoomable />
                <Controls />
              </ReactFlow>
            </div>
            <div className="node-strip">
              {visibleNodes.map((node) => (
                <button key={node.id} onClick={() => void selectNode(node)}>
                  <span style={{ color: nodeTone(node.type) }}>{node.type}</span>
                  {node.label}
                </button>
              ))}
            </div>
          </section>
        )}

        {page === "chat" && (
          <section className="panel-page">
            <form className="chat-box" onSubmit={sendChat}>
              <textarea value={chatInput} onChange={(event) => setChatInput(event.target.value)} placeholder="对当前 scene 说一句话..." />
              <button type="submit"><Sparkles size={17} />运行 turn</button>
            </form>
            <pre className="response-box">{chatOutput || "等待一次 scene-grounded response。"}</pre>
            <div className="side-list">
              <h3>本轮可选 scenes</h3>
              {data.scenes.map((scene) => <p key={scene.scene_id}>{scene.scene_summary || scene.scene_id} · {scene.participant_count || 0} participants</p>)}
            </div>
          </section>
        )}

        {page === "world" && (
          <WorldPanel client={client} data={data} reload={() => loadWorkspace()} />
        )}

        {page === "review" && (
          <section className="panel-page">
            {data.branches.map((branch) => (
              <article className="branch" key={branch.branch_id}>
                <h3>{branch.branch_id}</h3>
                <p>{branch.reason || "无 reason"}</p>
                {branch.candidates.map((candidate) => (
                  <button key={candidate.candidate_id} onClick={() => void resolveBranch(branch, candidate.candidate_id)}>
                    选择 {candidate.label || candidate.candidate_id} · confidence {candidate.confidence ?? "-"}
                  </button>
                ))}
              </article>
            ))}
            {!data.branches.length && <p className="muted">当前没有 open local_branch。</p>}
          </section>
        )}

        {page === "metrics" && (
          <section className="metrics-grid">
            <Metric label="Persons" value={data.summary?.person_count} />
            <Metric label="Relations" value={data.summary?.relation_count} />
            <Metric label="Memories" value={data.summary?.memory_count} />
            <Metric label="Scenes" value={data.summary?.scene_count} />
            <Metric label="Patches" value={data.summary?.patch_count} />
            <Metric label="Snapshots" value={data.summary?.snapshot_count} />
          </section>
        )}

        <Timeline events={data.events} patches={data.patches} snapshots={data.snapshots} />
      </section>

      <aside className={`drawer ${selected ? "open" : ""}`}>
        <button className="close" onClick={() => setSelected(null)}><X size={17} /></button>
        <p className="eyebrow">Inspector</p>
        <h2>详情检查器</h2>
        {selected ? (
          <>
            <dl>
              <dt>ID</dt><dd>{selected.id}</dd>
              <dt>类型</dt><dd>{selected.type}</dd>
              <dt>标签</dt><dd>{selected.label}</dd>
              {detail && Object.entries(detail.entity).slice(0, 10).map(([key, value]) => (
                <Fragment key={key}><dt>{key}</dt><dd>{short(value)}</dd></Fragment>
              ))}
            </dl>
            {!editMode && <button onClick={() => setEditMode(true)}><SlidersHorizontal size={16} />编辑</button>}
            {editMode && (
              <div className="edit-form">
                <label>
                  名称
                  <input aria-label="名称" value={nameDraft} onChange={(event) => setNameDraft(event.target.value)} />
                </label>
                {nameDraft !== selected.label && (
                  <div className="diff">
                    <strong>Diff Preview</strong>
                    <p>- {selected.label}</p>
                    <p>+ {nameDraft}</p>
                  </div>
                )}
                <button onClick={() => void submitPatch()}><Save size={16} />提交 Patch</button>
              </div>
            )}
            {auditRef && <pre className="audit-ref">{JSON.stringify(auditRef, null, 2)}</pre>}
          </>
        ) : (
          <p className="muted">选择一个 node 或边查看详情。</p>
        )}
      </aside>
    </main>
  );
}

function Metric({ label, value }: { label: string; value?: number }) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value ?? "-"}</strong>
    </article>
  );
}

function Timeline({ events, patches, snapshots }: { events: EventItem[]; patches: Patch[]; snapshots: Snapshot[] }) {
  return (
    <footer className="timeline">
      <section>
        <h3>Events</h3>
        {events.slice(0, 4).map((item) => <p key={item.event_id}>{item.event_id} · {item.summary || item.event_type}</p>)}
      </section>
      <section>
        <h3>Patches</h3>
        {patches.slice(0, 4).map((item) => <p key={item.patch_id}>{item.patch_id} · {item.operation} · {item.status}</p>)}
      </section>
      <section>
        <h3>Snapshots</h3>
        {snapshots.slice(0, 4).map((item) => <p key={item.snapshot_id}>{item.snapshot_id} · {item.summary || "-"}</p>)}
      </section>
    </footer>
  );
}

function WorldPanel({ client, data, reload }: { client: ApiClient; data: AppData; reload: () => Promise<void> }) {
  const [kind, setKind] = useState("artifact");
  const [name, setName] = useState("");
  const [auditRef, setAuditRef] = useState<AuditRef | null>(null);

  async function createObject(event: FormEvent) {
    event.preventDefault();
    const result = await client.request<AuditRef>("/api/world/objects", {
      method: "POST",
      body: JSON.stringify({ kind, name })
    });
    setAuditRef(result);
    setName("");
    await reload();
  }

  return (
    <section className="panel-page world-grid">
      <form onSubmit={createObject} className="inline-form">
        <input value={kind} onChange={(event) => setKind(event.target.value)} placeholder="kind" />
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="world object name" />
        <button type="submit">创建 Object</button>
      </form>
      <WorldList title="Objects" items={data.world.objects} />
      <WorldList title="Places" items={data.world.places} />
      <WorldList title="Projects" items={data.world.projects} />
      {auditRef && <pre className="audit-ref">{JSON.stringify(auditRef, null, 2)}</pre>}
    </section>
  );
}

function WorldList({ title, items }: { title: string; items: unknown[] }) {
  return (
    <article className="world-list">
      <h3>{title}</h3>
      {items.slice(0, 8).map((item, index) => <p key={index}>{short(item)}</p>)}
      {!items.length && <p className="muted">暂无数据</p>}
    </article>
  );
}
