import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import "../i18n";
import { SubmissionStatus } from "./SubmissionStatus";

describe("SubmissionStatus", () => {
  it("translates a known state", () => {
    render(<SubmissionStatus status="pending" rejectionReason="" />);

    expect(screen.getByText("Pendiente de revisión")).toBeInTheDocument();
  });

  it("shows the rejection reason", () => {
    render(
      <SubmissionStatus status="rejected" rejectionReason="duplicate photo" />,
    );

    expect(screen.getByText("Rechazado")).toBeInTheDocument();
    expect(screen.getByText(/duplicate photo/)).toBeInTheDocument();
  });

  it("falls back to the raw state for an unknown one", () => {
    render(<SubmissionStatus status="something_new" rejectionReason="" />);

    expect(screen.getByText("something_new")).toBeInTheDocument();
  });
});
