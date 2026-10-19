export type OperationKind = "model" | "search" | "page";
export type BudgetScope = "request" | "research";
export type OperationContext = { readonly signal: AbortSignal; readonly timeoutMs: number };
export type NativeResearchContext = OperationContext & { readonly maxToolCalls: 2 };
export type BudgetErrorCode = "LIMIT_EXCEEDED" | "DEADLINE_EXCEEDED" | "CANCELLED";

export class ExecutionBudgetError extends Error {
  readonly name = "ExecutionBudgetError";
  constructor(readonly code: BudgetErrorCode) {
    super(`Execution budget: ${code}`);
  }
}

const limits = { model: 6, search: 2, page: 3 } as const;

export class ExecutionBudget {
  readonly deadline: number;
  private readonly now: () => number;
  private readonly externalSignal: AbortSignal | undefined;
  private readonly active = new Set<AbortController>();
  // Counts are mutated only by the synchronous dispatch reservation.
  private readonly counts = { model: 0, search: 0, page: 0 };
  private nativeToolCallsReserved = 0;
  private researchDeadline: number | undefined;
  private stopped: ExecutionBudgetError | undefined;
  private readonly onExternalAbort = () => this.cancel();

  constructor(options: { readonly signal?: AbortSignal; readonly now?: () => number } = {}) {
    this.now = options.now ?? Date.now;
    this.deadline = this.now() + 180_000;
    this.externalSignal = options.signal;
  }

  snapshot() {
    return {
      modelCalls: this.counts.model,
      searches: this.counts.search,
      pageReads: this.counts.page,
      nativeToolCallsReserved: this.nativeToolCallsReserved,
      deadline: this.deadline,
    } as const;
  }

  startResearch(): void {
    this.assertAvailable(this.deadline);
    this.researchDeadline ??= Math.min(this.deadline, this.now() + 45_000);
    this.assertAvailable(this.researchDeadline);
  }

  async run<T>(
    kind: OperationKind,
    operation: (context: OperationContext) => Promise<T>,
    scope: BudgetScope = "request",
  ): Promise<T> {
    const research = scope === "research" || kind !== "model";
    if (research) this.startResearch();
    const deadline = Math.min(
      this.deadline,
      research ? (this.researchDeadline ?? this.deadline) : this.deadline,
      kind === "model" ? this.now() + 30_000 : this.deadline,
    );
    this.assertAvailable(deadline);
    if (this.counts[kind] >= limits[kind]) throw new ExecutionBudgetError("LIMIT_EXCEEDED");
    this.counts[kind] += 1;
    return this.withDeadline(deadline, operation);
  }

  async runNativeResearch<T>(
    operation: (context: NativeResearchContext) => Promise<T>,
  ): Promise<T> {
    this.startResearch();
    const deadline = Math.min(
      this.deadline,
      this.researchDeadline ?? this.deadline,
      this.now() + 30_000,
    );
    this.assertAvailable(deadline);
    if (this.counts.model >= limits.model || this.nativeToolCallsReserved + 2 > 2) {
      throw new ExecutionBudgetError("LIMIT_EXCEEDED");
    }
    // Reserve full hosted-tool capacity with the model before dispatch; never refund it.
    this.counts.model += 1;
    this.nativeToolCallsReserved += 2;
    return this.withDeadline(deadline, (context) => operation({ ...context, maxToolCalls: 2 }));
  }

  async runRequest<T>(operation: (context: OperationContext) => Promise<T>): Promise<T> {
    this.assertAvailable(this.deadline);
    return this.withDeadline(this.deadline, operation);
  }

  async runResearch<T>(operation: (context: OperationContext) => Promise<T>): Promise<T> {
    this.startResearch();
    return this.withDeadline(this.researchDeadline ?? this.deadline, operation);
  }

  cancel(): void {
    this.stop(new ExecutionBudgetError("CANCELLED"));
  }

  dispose(): void {
    this.cancel();
  }

  private stop(error: ExecutionBudgetError): void {
    this.stopped ??= error;
    for (const controller of this.active) controller.abort(this.stopped);
    this.externalSignal?.removeEventListener("abort", this.onExternalAbort);
  }

  private assertAvailable(deadline: number): void {
    if (this.externalSignal?.aborted) this.cancel();
    if (this.stopped) throw this.stopped;
    if (this.now() >= deadline) {
      const error = new ExecutionBudgetError("DEADLINE_EXCEEDED");
      this.stop(error);
      throw error;
    }
  }

  private async withDeadline<T>(
    deadline: number,
    operation: (context: OperationContext) => Promise<T>,
  ): Promise<T> {
    const controller = new AbortController();
    this.active.add(controller);
    this.externalSignal?.addEventListener("abort", this.onExternalAbort, { once: true });
    const timeoutMs = deadline - this.now();
    const timer = setTimeout(
      () => this.stop(new ExecutionBudgetError("DEADLINE_EXCEEDED")),
      timeoutMs,
    );
    let onAbort: () => void = () => {};
    const cancelled = new Promise<never>((_, reject) => {
      onAbort = () => reject(controller.signal.reason);
      controller.signal.addEventListener("abort", onAbort, { once: true });
    });
    try {
      const dispatched = new Promise<T>((resolve) => {
        resolve(operation({ signal: controller.signal, timeoutMs }));
      });
      const result = await Promise.race([dispatched, cancelled]);
      this.assertAvailable(deadline);
      return result;
    } finally {
      clearTimeout(timer);
      controller.signal.removeEventListener("abort", onAbort);
      this.active.delete(controller);
      if (this.active.size === 0) {
        this.externalSignal?.removeEventListener("abort", this.onExternalAbort);
      }
    }
  }
}
