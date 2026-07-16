import { type AuditLogEntry, parseAuditLogEntryList } from "@/features/audit-log/contracts";
import { apiRequest } from "@/shared/api/http";

export const AUDIT_LOG_ENDPOINT_PATH = "/audit-log";

export const readAuditLogEntries = (): Promise<AuditLogEntry[]> =>
  apiRequest<AuditLogEntry[]>(AUDIT_LOG_ENDPOINT_PATH, {
    parse: parseAuditLogEntryList,
  });
