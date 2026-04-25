import "@testing-library/jest-dom/vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const bootstrap = {
  ok: true,
  data: {
    tenant_id: "default",
    capabilities: { graph: true, chat: true, world: true, review: true, editor: true },
    feature_flags: { patch_first_editor: true }
  }
};

const summary = {
  ok: true,
  data: {
    person_count: 2,
    relation_count: 1,
    memory_count: 1,
    scene_count: 1,
    branch_count: 1,
    patch_count: 2,
    snapshot_count: 1,
    world: { object_count: 1, place_count: 1, project_count: 1 }
  }
};

const graph = {
  ok: true,
  data: {
    nodes: [
      { id: "person_web_1", type: "person", label: "Alice", data: { primary_name: "Alice" } },
      { id: "memory_web_1", type: "memory", label: "Shared launch", data: { summary: "Shared launch" } }
    ],
    edges: [
      { id: "relation_web_1", type: "relation", source: "person_web_1", target: "memory_web_1", label: "remembers" }
    ]
  }
};

const scenes = { ok: true, data: { scenes: [{ scene_id: "scene_web_1", scene_summary: "sync", participant_count: 2 }] } };
const timeline = { ok: true, data: { events: [{ event_id: "evt_1", summary: "hello" }] } };
const patches = { ok: true, data: { patches: [{ patch_id: "patch_1", operation: "update_entity", status: "applied" }] } };
const snapshots = { ok: true, data: { snapshots: [{ snapshot_id: "snap_1", summary: "after edit" }] } };
const world = {
  ok: true,
  data: {
    objects: [{ object_id: "obj_1", kind: "tool", name: "Shared Notebook", status: "active", owner_id: "person_web_1" }],
    places: [{ place_id: "place_1", name: "Web Room", scope: "virtual", status: "active" }],
    projects: [{ project_id: "proj_1", name: "WebUI Phase", status: "active", goal: "ship workbench" }]
  }
};
const branches = {
  ok: true,
  data: {
    branches: [{
      branch_id: "branch_1",
      reason: "review needed",
      candidates: [{
        candidate_id: "candidate_1",
        label: "Keep current",
        confidence: 0.8,
        payload_json: { effect_patches: [{ operation: "noop" }] }
      }]
    }]
  }
};

function mockFetch() {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method || "GET";
    const headers = init?.headers as Record<string, string> | undefined;
    if (url.startsWith("/api/") && headers?.Authorization !== "Bearer dev-token") {
      return new Response(JSON.stringify({ ok: false, error: { code: "unauthorized", message: "no" } }), { status: 401 });
    }
    if (method === "PATCH" && url.startsWith("/api/entities/person/person_web_1")) {
      return Response.json({ ok: true, data: { patch_id: "patch_2", event_id: "webui_event_2", summary: summary.data } });
    }
    if (method === "POST" && url.startsWith("/api/chat/run-turn")) {
      return Response.json({
        ok: true,
        data: {
          text: "收到",
          event_id: "evt_2",
          retrieval_package: { scene_id: "scene_web_1", participants: [{ primary_name: "Alice" }] }
        }
      });
    }
    if (method === "POST" && url.startsWith("/api/world/objects")) {
      return Response.json({ ok: true, data: { object_id: "obj_2", audit_event_id: "webui_event_3", summary: summary.data } });
    }
    if (method === "PATCH" && url.startsWith("/api/world/objects/obj_1/status")) {
      return Response.json({ ok: true, data: { object_id: "obj_1", status: "lost", audit_event_id: "webui_event_4" } });
    }
    if (method === "PATCH" && url.startsWith("/api/world/projects/proj_1/status")) {
      return Response.json({ ok: true, data: { project_id: "proj_1", status: "completed", audit_event_id: "webui_event_5" } });
    }
    if (method === "POST" && url.startsWith("/api/branches/branch_1/resolve")) {
      return Response.json({ ok: true, data: { patch_id: "patch_3", event_id: "webui_event_6", summary: summary.data } });
    }
    if (url.startsWith("/api/bootstrap")) return Response.json(bootstrap);
    if (url.startsWith("/api/summary")) return Response.json(summary);
    if (url.startsWith("/api/scenes")) return Response.json(scenes);
    if (url.startsWith("/api/graph")) return Response.json(graph);
    if (url.startsWith("/api/events")) return Response.json(timeline);
    if (url.startsWith("/api/patches")) return Response.json(patches);
    if (url.startsWith("/api/snapshots")) return Response.json(snapshots);
    if (url.startsWith("/api/world")) return Response.json(world);
    if (url.startsWith("/api/branches")) return Response.json(branches);
    if (url.startsWith("/api/entities/person/person_web_1")) return Response.json({ ok: true, data: { entity: graph.data.nodes[0], patches: [] } });
    return Response.json({ ok: true, data: {} });
  });
}

describe("we-together WebUI", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.stubGlobal(
      "ResizeObserver",
      class {
        observe() {}
        unobserve() {}
        disconnect() {}
      }
    );
    vi.stubGlobal("fetch", mockFetch());
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("renders token gate before API access", () => {
    render(<App />);
    expect(screen.getByText("连接 we-together")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("输入 Bearer token")).toBeInTheDocument();
  });

  it("loads graph workspace after token entry", async () => {
    render(<App />);
    await userEvent.type(screen.getByPlaceholderText("输入 Bearer token"), "dev-token");
    await userEvent.click(screen.getByRole("button", { name: "进入工作台" }));
    await waitFor(() => expect(screen.getByText("图谱工作台")).toBeInTheDocument());
    expect(screen.getAllByText("Alice").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Shared launch").length).toBeGreaterThan(0);
  });

  it("opens detail drawer and submits a patch edit", async () => {
    const fetchMock = globalThis.fetch as unknown as ReturnType<typeof vi.fn>;
    render(<App />);
    await userEvent.type(screen.getByPlaceholderText("输入 Bearer token"), "dev-token");
    await userEvent.click(screen.getByRole("button", { name: "进入工作台" }));
    await waitFor(() => expect(screen.getAllByText("Alice").length).toBeGreaterThan(0));
    await userEvent.click(screen.getAllByText("Alice").at(-1)!);
    expect(screen.getByText("详情检查器")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "编辑" }));
    await userEvent.clear(screen.getByLabelText("名称"));
    await userEvent.type(screen.getByLabelText("名称"), "Alice Web");
    expect(screen.getByText("Diff Preview")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "提交 Patch" }));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/entities/person/person_web_1",
      expect.objectContaining({
        method: "PATCH",
        headers: expect.objectContaining({ Authorization: "Bearer dev-token" })
      })
    );
  });

  it("runs a chat turn and shows response plus retrieval package", async () => {
    render(<App />);
    await userEvent.type(screen.getByPlaceholderText("输入 Bearer token"), "dev-token");
    await userEvent.click(screen.getByRole("button", { name: "进入工作台" }));
    await waitFor(() => expect(screen.getByText("图谱工作台")).toBeInTheDocument());
    await userEvent.click(screen.getByRole("button", { name: /对话/ }));
    await userEvent.type(screen.getByPlaceholderText("对当前 scene 说一句话..."), "继续推进");
    await userEvent.click(screen.getByRole("button", { name: /运行 turn/ }));
    await waitFor(() => expect(screen.getByText(/收到/)).toBeInTheDocument());
    expect(screen.getByText(/evt_2/)).toBeInTheDocument();
    expect(screen.getByText(/retrieval_package/)).toBeInTheDocument();
    expect(screen.getByText(/Alice/)).toBeInTheDocument();
  });

  it("renders world lists and creates audited object updates", async () => {
    const fetchMock = globalThis.fetch as unknown as ReturnType<typeof vi.fn>;
    render(<App />);
    await userEvent.type(screen.getByPlaceholderText("输入 Bearer token"), "dev-token");
    await userEvent.click(screen.getByRole("button", { name: "进入工作台" }));
    await waitFor(() => expect(screen.getByText("图谱工作台")).toBeInTheDocument());
    await userEvent.click(screen.getByRole("button", { name: /世界/ }));
    expect(screen.getByText(/Shared Notebook/)).toBeInTheDocument();
    expect(screen.getByText(/Web Room/)).toBeInTheDocument();
    expect(screen.getByText(/WebUI Phase/)).toBeInTheDocument();
    await userEvent.type(screen.getByPlaceholderText("world object name"), "Review Token");
    await userEvent.click(screen.getByRole("button", { name: "创建 Object" }));
    await waitFor(() => expect(screen.getByText(/webui_event_3/)).toBeInTheDocument());
    await userEvent.selectOptions(screen.getByLabelText("Object status"), "lost");
    await userEvent.click(screen.getByRole("button", { name: "更新 Object 状态" }));
    await userEvent.selectOptions(screen.getByLabelText("Project status"), "completed");
    await userEvent.click(screen.getByRole("button", { name: "更新 Project 状态" }));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/world/objects",
      expect.objectContaining({ method: "POST", headers: expect.objectContaining({ Authorization: "Bearer dev-token" }) })
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/world/objects/obj_1/status",
      expect.objectContaining({ method: "PATCH" })
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/world/projects/proj_1/status",
      expect.objectContaining({ method: "PATCH" })
    );
  });

  it("renders review candidate payloads and resolves a branch", async () => {
    const fetchMock = globalThis.fetch as unknown as ReturnType<typeof vi.fn>;
    render(<App />);
    await userEvent.type(screen.getByPlaceholderText("输入 Bearer token"), "dev-token");
    await userEvent.click(screen.getByRole("button", { name: "进入工作台" }));
    await waitFor(() => expect(screen.getByText("图谱工作台")).toBeInTheDocument());
    await userEvent.click(screen.getByRole("button", { name: /复核/ }));
    expect(screen.getByText("branch_1")).toBeInTheDocument();
    expect(screen.getByText(/Keep current/)).toBeInTheDocument();
    expect(screen.getByText(/effect_patches/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /选择 Keep current/ }));
    await waitFor(() => expect(screen.getByText(/patch_3/)).toBeInTheDocument());
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/branches/branch_1/resolve",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: "Bearer dev-token" })
      })
    );
  });
});
