import { deleteAiCredential, readAiCredentials, saveAiCredential } from "@/features/ai-settings/api";

describe("AI settings API consumers", () => {
  it("reads provider status through the shared API client", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ items: [{ provider: "openai", configured: true, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" }] }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(readAiCredentials()).resolves.toHaveLength(1);
    const firstCall = fetchMock.mock.calls.at(0) as unknown[] | undefined;
    expect(firstCall?.[0]).toEqual(expect.stringContaining("/ai/credentials"));
  });

  it("saves a key without exposing it in the response contract", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ provider: "gemini", configured: true, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const credentialInput = "provider-test-value";
    await saveAiCredential({ provider: "gemini", apiKey: credentialInput });
    expect(fetchMock.mock.calls[0][1]).toEqual(expect.objectContaining({ body: JSON.stringify({ api_key: credentialInput }) }));
  });

  it("deletes a provider credential", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 204 });
    vi.stubGlobal("fetch", fetchMock);

    await deleteAiCredential("openai");
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/ai/credentials/openai"), expect.objectContaining({ method: "DELETE" }));
  });
});
