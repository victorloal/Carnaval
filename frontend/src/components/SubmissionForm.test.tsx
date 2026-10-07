import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import "../i18n";
import { SubmissionForm } from "./SubmissionForm";

function form(container: HTMLElement): HTMLFormElement {
  const element = container.querySelector("form");
  if (!element) {
    throw new Error("the form did not render");
  }
  return element;
}

describe("SubmissionForm", () => {
  it("blocks without the rights and consent declarations", async () => {
    const action = vi.fn();
    const { container } = render(
      <SubmissionForm onCreated={vi.fn()} action={action} />,
    );

    fireEvent.submit(form(container));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /declaraciones/i,
    );
    expect(action).not.toHaveBeenCalled();
  });

  it("sends the declaration fields and reports the token", async () => {
    const action = vi.fn().mockResolvedValue({ token: "abc123", status: "pending" });
    const onCreated = vi.fn();
    const { container } = render(
      <SubmissionForm onCreated={onCreated} action={action} />,
    );

    fireEvent.change(screen.getByLabelText("Autoría"), {
      target: { value: "A. Photographer" },
    });
    fireEvent.change(screen.getByLabelText("Año aproximado"), {
      target: { value: "1975" },
    });
    fireEvent.click(screen.getByLabelText(/Declaro que soy el autor/));
    fireEvent.click(screen.getByLabelText(/He leído el aviso/));
    fireEvent.submit(form(container));

    await waitFor(() => expect(action).toHaveBeenCalledTimes(1));
    const data = action.mock.calls[0][0] as FormData;
    expect(data.get("kind")).toBe("image");
    expect(data.get("author")).toBe("A. Photographer");
    expect(data.get("year")).toBe("1975");
    expect(data.get("consent")).toBeNull();
    await waitFor(() =>
      expect(onCreated).toHaveBeenCalledWith({ token: "abc123", status: "pending" }),
    );
  });

  it("drops a submission that fills the honeypot", async () => {
    const action = vi.fn();
    const { container } = render(
      <SubmissionForm onCreated={vi.fn()} action={action} />,
    );

    fireEvent.change(screen.getByLabelText("Website"), {
      target: { value: "http://spam.example" },
    });
    fireEvent.click(screen.getByLabelText(/Declaro que soy el autor/));
    fireEvent.click(screen.getByLabelText(/He leído el aviso/));
    fireEvent.submit(form(container));

    expect(action).not.toHaveBeenCalled();
  });
});
