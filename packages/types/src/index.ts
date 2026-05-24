/**
 * packages/types/src/index.ts — Shared TypeScript type definitions.
 *
 * Phase 0: Stubs only. Types are filled in as each phase introduces
 * domain entities (sermons, events, users, churches, etc.)
 */

export type Role = 'superadmin' | 'admin' | 'staff' | 'member' | 'guest'

export interface VersionInfo {
  version: string
  codename: string
}
