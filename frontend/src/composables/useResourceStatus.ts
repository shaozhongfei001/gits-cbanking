export type ResourceStatus = 'idle' | 'loading' | 'success' | 'error'

export function deriveResourceStatus(args: {
  loading: boolean
  error: string
  hasData: boolean
  requested: boolean
}): ResourceStatus {
  if (args.loading) {
    return 'loading'
  }
  if (args.error) {
    return 'error'
  }
  if (args.hasData) {
    return 'success'
  }
  return args.requested ? 'success' : 'idle'
}
