// The three seeded directions get a dedicated badge color; any direction an
// admin adds later falls back to a neutral "info" badge automatically.
const KNOWN: Record<string, 'back' | 'front' | 'qa'> = {
  'dir-back': 'back',
  'dir-front': 'front',
  'dir-qa': 'qa',
}

export function directionBadgeVariant(directionId: string): 'back' | 'front' | 'qa' | 'info' {
  return KNOWN[directionId] ?? 'info'
}
