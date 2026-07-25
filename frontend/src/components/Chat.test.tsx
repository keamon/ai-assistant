import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Chat from "./Chat";

const { assistantMock } = vi.hoisted(() => ({ assistantMock: vi.fn() }));
vi.mock("../api", () => ({ api: { assistant: assistantMock } }));

describe("Chat", () => {
  beforeEach(() => {
    assistantMock.mockReset();
    assistantMock.mockResolvedValue({ reply: "done", session_id: "s1" });
  });

  it("shows the market-intelligence starter prompt", () => {
    render(
      <Chat
        sessionId={null}
        setSessionId={() => {}}
        messages={[]}
        setMessages={() => {}}
        onAction={() => {}}
      />
    );
    expect(screen.getByText(/latest 10-Q and stock snapshot/i)).toBeInTheDocument();
  });

  it("sends the assistant request when a starter is clicked", async () => {
    render(
      <Chat
        sessionId={null}
        setSessionId={() => {}}
        messages={[]}
        setMessages={() => {}}
        onAction={() => {}}
      />
    );
    fireEvent.click(screen.getByText(/latest 10-Q and stock snapshot/i));
    await waitFor(() => expect(assistantMock).toHaveBeenCalledTimes(1));
    expect(assistantMock).toHaveBeenCalledWith(
      expect.stringContaining("Williams-Sonoma"),
      null
    );
  });
});
