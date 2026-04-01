import { clerkMiddleware } from '@clerk/nextjs/server'

// Clerk's default JWT clock skew is 5s. Small drift vs Clerk's servers (common on Windows/NTP)
// yields "iat in the future", failed refresh, and redirect loops. Widen in dev only.
const envSkew = process.env.CLERK_CLOCK_SKEW_IN_MS
const parsedSkew = envSkew ? Number(envSkew) : NaN
const clockSkewInMs =
  Number.isFinite(parsedSkew) && parsedSkew > 0
    ? parsedSkew
    : process.env.NODE_ENV === 'development'
      ? 60_000
      : undefined

export default clerkMiddleware(clockSkewInMs != null ? { clockSkewInMs } : {})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
