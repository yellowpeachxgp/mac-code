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
const world = { ok: true, data: { objects: [], places: [], projects: [] } };
const branches = { ok: true, data: { branches: [{ branch_id: "branch_1", reason: "review", candidates: [] }] } };

function mockFetch() {
  return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const headers = init?.headers as Record<string, string> | undefined;
    if (url.startsWith("/api/") && headers?.Authorization !== "Bearer dev-token") {
      return new Response(JSON.stringify({ ok: false, error: { code: "unauthorized", message: "no" } }), { status: 401 });
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
    if (url.startsWith("/api/chat/run-turn")) return Response.json({ ok: true, data: { text: "收到", event_id: "evt_2" } });
    if (url.startsWith("/api/entities/person/person_web_1")) return Response.json({ ok: true, data: { patch_id: "patch_2", event_id: "webui_event_2", summary: summary.data } });
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
});
